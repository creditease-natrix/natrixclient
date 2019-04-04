#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 需要上报的信息,ip地址，子网掩码，网关，MAC地址(并且作为树莓派唯一ID)，主机名,公网IP，区域，运营商

"""
"network": {
    "macaddr": "b827ebbf1124",
    "timestamp": 1508838771,
    "hostname": "pi-b827ebbf1124",
    "public_ip": "106.39.60.230",
    "local_ip": "10.101.1.23",
    "netmask": "255.255.255.128",
    "gateway": "10.101.1.1",
    "access_internet": true,
    "access_corporate": true,
    "access_intranet": true
}
"""


import json
import logging
import netifaces
import sys
import socket
import subprocess
from python_hosts import Hosts
from python_hosts import HostsEntry
from natrixclient.common.const import CONFIG_PATH
from natrixclient.common.config import NatrixConfig
from natrixclient.command.ping.pyping import Ping
from natrixclient.command.check.iplocation import IpLocation
from natrixclient.command.check.ippublic import IpPublic


logger = logging.getLogger(__name__)


class NetInfo(object):
    # 初始化固有属性macaddr,localip,netmask,gateway,hostname
    def __init__(self, parameters=None):
        self.config = NatrixConfig()
        self.parameters = parameters
        # logger
        if parameters and parameters.get("logger"):
            global logger
            logger = logging.getLogger(parameters.get("logger"))

    def ping_access(self, website, interface):
        access = False
        try:
            logger.debug("ping website {} using interface {}".format(website, interface))
            pobj = Ping(destination=website, parameters=self.parameters)
            presult = pobj.ping()
            if presult:
                access = True
            else:
                logger.error("ping website {} using interface {} got empty result".format(website, interface))
        except Exception as e:
            logger.exception("ping website {} using interface {} cause exception: {}".format(website, interface, e))
        return access

    # 请输入互联网网站
    # 如果不存在, 默认能访互联网, 返回True
    # 如果存在, 只要有任何一个能访问, 就代表能访问, 返回True
    def access_internet(self, interface):
        access = True
        try:
            internet_websites = self.config.get_value("NETWORK", "internet_websites")
            internet_websites = internet_websites.replace("[", "").replace("]", "").replace("\"", "").\
                replace("'", "").replace(" ", "")
            if internet_websites:
                websites = internet_websites.split(",")
                for website in websites:
                    website = website.strip()
                    logger.debug("access internet {} using interface {}".format(website, interface))
                    access = self.ping_access(website, interface)
                    if access:
                        logger.debug("interface {} can access internet {}".format(interface, website))
                        break
                    else:
                        logger.warning("interface {} cannot access internet {}".format(interface, website))
            else:
                logger.error("please set NETWORK: internet_websites in {}".format(CONFIG_PATH))
        except KeyError as ke:
            logger.exception("fail to get NETWORK:internet_websites from configuration file {}. \nexception: {}".
                                  format(CONFIG_PATH, str(ke)))
        return access

    # 请输入公司内网网站域名
    # 如果不存在, 默认能访问公司HTTP网络, 返回True
    # 如果存在, 只要有任何一个能访问, 就代表能访问, 返回True
    def access_corporate(self, interface):
        access = True
        try:
            corporate_websites = self.config.get_value("NETWORK", "corporate_websites")
            corporate_websites = corporate_websites.replace("[", "").replace("]", "").replace("\"", "").\
                replace("'", "").replace(" ", "")
            if corporate_websites:
                websites = corporate_websites.split(",")
                for website in websites:
                    website = website.strip()
                    logger.debug("access corporate {} using interface {}".format(website, interface))
                    access = self.ping_access(website, interface)
                    if access:
                        logger.debug("interface {} can access corporate {}".format(interface, website))
                        break
                    else:
                        logger.warning("interface {} cannot access corporate {}".format(interface, website))
            else:
                logger.error("please set NETWORK:corporate_websites in {}".format(CONFIG_PATH))
        except KeyError as ke:
            logger.exception("fail to get NETWORK:corporate_websites from configuration file {}. \nexception: {}".
                                  format(CONFIG_PATH, str(ke)))
        return access

    # 请输入公司局域网IP
    # 如果不存在, 默认能访问公司内部网络, 返回True
    # 如果存在, 只要有任何一个能访问, 就代表能访问, 返回True
    def access_intranet(self, interface):
        access = True
        try:
            intranet_ips = self.config.get_value("NETWORK", "intranet_ips")
            intranet_ips = intranet_ips.replace("[", "").replace("]", "").replace("\"", "").replace("'", "").replace(" ", "")
            if intranet_ips:
                ips = intranet_ips.split(",")
                for ip in ips:
                    ip = ip.strip()
                    logger.debug("access intranet {} using interface {}".format(ip, interface))
                    access = self.ping_access(ip, interface)
                    if access:
                        logger.debug("interface {} can access intranet {}".format(interface, ip))
                        break
                    else:
                        logger.warning("interface {} cannot access intranet {}".format(interface, ip))
            else:
                logger.error("please set NETWORK:intranet_websites in {}".format(CONFIG_PATH))
        except KeyError as ke:
            logger.exception("fail to get NETWORK:intranet_websites from configuration file {}. \nexception: {}".
                                  format(CONFIG_PATH, str(ke)))
        return access

    @staticmethod
    def set_gateways(interfaces_json):
        netgateways = netifaces.gateways()
        gateways = netgateways.get(netifaces.AF_INET)
        for gateway in gateways:
            gw = gateway[0]
            gintf = gateway[1]
            gdefault = gateway[2]
            interfaces_json[gintf]["gateway"] = gw
            interfaces_json[gintf]["is_default"] = gdefault

    # 获取主机名,如果主机名不符合规范,重设主机名
    @staticmethod
    def set_hostname():
        macaddress = NetInfo.get_default_mac().replace(":", "")
        default_hostname = "pi-" + macaddress
        init_hostname = socket.gethostname()
        logger.debug("get hostname = %s" % init_hostname)
        # self.hostname = inithostname
        if init_hostname != default_hostname:
            logger.debug("set hostname = %s" % init_hostname)
            # 重设主机名
            args = "hostname  %s " % default_hostname
            subprocess.Popen(args, shell=True, stdout=subprocess.PIPE).communicate()

            # 修改/etc/hostname文件
            f = open('/etc/hostname', 'w')
            f.write(default_hostname)
            f.close()

            # 修改/etc/hosts
            if 'linux' in sys.platform or 'darwin' in sys.platform:
                filename = '/etc/hosts'
            else:
                filename = 'c:\windows\system32\drivers\etc\hosts'

            hosts = Hosts(path=filename)
            # 移除旧域名
            hosts.remove_all_matching(name=init_hostname)
            new_entry = HostsEntry(entry_type='ipv4', address='127.0.0.1', names=[default_hostname])
            hosts.add([new_entry])
            hosts.write()

    # 得到单独的接口信息
    # 网络类型
    # WIRED = "wired"
    # WIRELESS = "wireless"
    # MOBILE = "dns"
    # CELLULAR_3G = "3G"
    # CELLULAR_4G = "4G"
    # UNKNOWN = "unknown"
    @staticmethod
    def get_interface(interface):
        interface_json = {
            "type": "wired",
            "name": interface
        }
        wireless_keys = ["wlan"]
        for wireless_key in wireless_keys:
            if interface.find(wireless_key) >= 0:
                interface_json["type"] = "wireless"
                break
        info = netifaces.ifaddresses(interface)
        # 地址信息
        interface_json["macaddress"] = None
        info_mac = info.get(netifaces.AF_LINK)
        if info_mac:
            if len(info_mac) == 1:
                interface_json["macaddress"] = info_mac[0].get("addr").replace(":", "").lower()
            else:
                logger.error("get mac address for interface {} wrong: {}".format(interface, str(info_mac)))
        else:
            logger.error("cannot get mac address for interface {}".format(interface))

        # ip地址信息, need to consider with gateway
        info_ipv4 = info.get(netifaces.AF_INET)
        if info_ipv4 and len(info_ipv4) == 1:
            local_ip = info_ipv4[0].get("addr")
            interface_json["local_ip"] = local_ip
            interface_json["local_location"] = IpLocation.get_location(local_ip)
            interface_json["netmask"] = info_ipv4[0].get("netmask")
            interface_json["broadcast"] = info_ipv4[0].get("broadcast")
            interface_json["is_default"] = False
        elif info_ipv4 and len(info_ipv4) > 1:
            """
            存在1个接口对应n个IP, 例如
            $ ip addr
            1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1
                link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
                inet 127.0.0.1/8 scope host lo
                   valid_lft forever preferred_lft forever
                inet6 ::1/128 scope host 
                   valid_lft forever preferred_lft forever
            2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000
                link/ether b8:27:eb:f9:41:74 brd ff:ff:ff:ff:ff:ff
                inet 10.10.36.222/24 brd 10.10.36.255 scope global eth0
                   valid_lft forever preferred_lft forever
                inet 10.10.36.55/24 brd 10.10.36.255 scope global secondary eth0
                   valid_lft forever preferred_lft forever
                inet6 fe80::ba27:ebff:fef9:4174/64 scope link 
                   valid_lft forever preferred_lft forever
            """
            msg = "interface: {} have {} ip, natrix do not support, please check your network!".format(
                    interface, len(info))
            logger.warning(msg)

            local_ip = None
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                # doesn't even have to be reachable
                s.connect(('10.255.255.255', 1))
                local_ip = s.getsockname()[0]
            except Exception:
                msg = "Cannot get an default ip for interface {}".format(interface)
                logger.exception(msg)

            if local_ip:
                for info in info_ipv4:
                    if info.get("addr") == local_ip:
                        interface_json["local_ip"] = info.get("addr")
                        interface_json["local_location"] = IpLocation.get_location(local_ip)
                        interface_json["netmask"] = info.get("netmask")
                        interface_json["broadcast"] = info.get("broadcast")
                        interface_json["is_default"] = False

            if not interface_json.get("local_ip"):
                interface_json["local_ip"] = None
                interface_json["local_location"] = None
                interface_json["netmask"] = None
                interface_json["broadcast"] = None
                interface_json["is_default"] = False
        else:
            msg = "interface {} do not have IPV4 address".format(interface)
            logger.warning(msg)
            interface_json["local_ip"] = None
            interface_json["local_location"] = None
            interface_json["netmask"] = None
            interface_json["broadcast"] = None
            interface_json["is_default"] = False

        # in all situation, set gateway to None
        interface_json["gateway"] = None

        # 公网IP
        if interface_json["local_ip"]:
            public_ip = IpPublic.get_publicip(interface)
            interface_json["public_ip"] = public_ip
        else:
            interface_json["public_ip"] = None

        if interface_json.get("public_ip"):
            interface_json["public_location"] = IpLocation.get_location(interface_json.get("public_ip"))
        else:
            interface_json["public_location"] = None
        return interface_json

    # 得到所有的接口信息
    @staticmethod
    def get_interfaces():
        interfaces_json = {}
        for interface in netifaces.interfaces():
            if interface != "lo":
                interface_json = NetInfo.get_interface(interface)
                interfaces_json[interface] = interface_json
        # 设置 gateway 和 is_default 信息
        NetInfo.set_gateways(interfaces_json)
        # 设置名称
        # NetInfo.set_hostname(interfaces_json)
        # 解析网关信息
        return interfaces_json

    def get_access_interface(self, interface):
        interface_json = {
            "type": "wired",
            "name": interface
        }
        wireless_keys = ["wlan"]
        for wireless_key in wireless_keys:
            if interface.find(wireless_key) >= 0:
                interface_json["type"] = "wireless"
                break
        info = netifaces.ifaddresses(interface)
        # 地址信息
        interface_json["macaddress"] = None
        info_mac = info.get(netifaces.AF_LINK)
        if info_mac:
            if len(info_mac) == 1:
                interface_json["macaddress"] = info_mac[0].get("addr").replace(":", "").lower()
            else:
                logger.error("get mac address for interface {} wrong: {}".format(interface, str(info_mac)))
        else:
            logger.error("cannot get mac address for interface {}".format(interface))

        ipl = IpLocation(self.parameters)
        ipp = IpPublic(self.parameters)

        # ip地址信息, need to consider with gateway
        info_ipv4 = info.get(netifaces.AF_INET)
        if info_ipv4 and len(info_ipv4) == 1:
            local_ip = info_ipv4[0].get("addr")
            interface_json["local_ip"] = local_ip
            interface_json["local_location"] = ipl.get_location(local_ip)
            interface_json["netmask"] = info_ipv4[0].get("netmask")
            interface_json["broadcast"] = info_ipv4[0].get("broadcast")
            interface_json["is_default"] = False
        elif info_ipv4 and len(info_ipv4) > 1:
            """
            存在1个接口对应n个IP, 例如
            $ ip addr
            1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1
                link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
                inet 127.0.0.1/8 scope host lo
                   valid_lft forever preferred_lft forever
                inet6 ::1/128 scope host 
                   valid_lft forever preferred_lft forever
            2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000
                link/ether b8:27:eb:f9:41:74 brd ff:ff:ff:ff:ff:ff
                inet 10.10.36.222/24 brd 10.10.36.255 scope global eth0
                   valid_lft forever preferred_lft forever
                inet 10.10.36.55/24 brd 10.10.36.255 scope global secondary eth0
                   valid_lft forever preferred_lft forever
                inet6 fe80::ba27:ebff:fef9:4174/64 scope link 
                   valid_lft forever preferred_lft forever
            """
            msg = "interface: {} have {} ip, natrix do not support, please check your network!".format(
                    interface, len(info))
            logger.warning(msg)

            local_ip = None
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                # doesn't even have to be reachable
                s.connect(('10.255.255.255', 1))
                local_ip = s.getsockname()[0]
            except Exception:
                msg = "Cannot get an default ip for interface {}".format(interface)
                logger.exception(msg)

            if local_ip:
                for info in info_ipv4:
                    if info.get("addr") == local_ip:
                        interface_json["local_ip"] = info.get("addr")
                        interface_json["local_location"] = ipl.get_location(local_ip)
                        interface_json["netmask"] = info.get("netmask")
                        interface_json["broadcast"] = info.get("broadcast")
                        interface_json["is_default"] = False

            if not interface_json.get("local_ip"):
                interface_json["local_ip"] = None
                interface_json["local_location"] = None
                interface_json["netmask"] = None
                interface_json["broadcast"] = None
                interface_json["is_default"] = False
        else:
            msg = "interface {} do not have IPV4 address".format(interface)
            logger.warning(msg)
            interface_json["local_ip"] = None
            interface_json["local_location"] = None
            interface_json["netmask"] = None
            interface_json["broadcast"] = None
            interface_json["is_default"] = False

        # in all situation, set gateway to None
        interface_json["gateway"] = None

        # 公网IP
        if interface_json["local_ip"]:
            public_ip = ipp.get_publicip(interface)
            interface_json["public_ip"] = public_ip
        else:
            interface_json["public_ip"] = None

        if interface_json.get("public_ip"):
            interface_json["public_location"] = ipl.get_location(interface_json.get("public_ip"))
        else:
            interface_json["public_location"] = None

        # 连接信息
        if interface_json["local_ip"]:
            interface_json["access_intranet"] = self.access_intranet(interface)
            interface_json["access_corporate"] = self.access_corporate(interface)
            interface_json["access_internet"] = self.access_internet(interface)
        else:
            interface_json["access_intranet"] = False
            interface_json["access_corporate"] = False
            interface_json["access_internet"] = False
        return interface_json

    # 得到所有的接口信息
    def get_access_interfaces(self):
        interfaces_json = {}
        for interface in netifaces.interfaces():
            if interface != "lo":
                interface_access_json = self.get_access_interface(interface)
                interfaces_json[interface] = interface_access_json
        # 设置 gateway 和 is_default 信息
        NetInfo.set_gateways(interfaces_json)
        # 设置名称
        # NetInfo.set_hostname(interfaces_json)
        # 解析网关信息
        return interfaces_json

    # 得到接口的IP地址
    # 方法写道natrixclient.common.nettools
    @staticmethod
    def get_ip(interface):
        local_ip = None
        info = netifaces.ifaddresses(interface)
        info_ipv4 = info.get(netifaces.AF_INET)
        if info_ipv4:
            # 存在1个接口对应n个IP
            if len(info_ipv4) > 1:
                msg = "interface: {} have {} ips, please check your network!".format(interface, len(info_ipv4))
                logger.warning(msg)
            local_ip = info_ipv4[0].get("addr")
        return local_ip

    # 得到所有接口的IP地址
    @staticmethod
    def get_ips():
        ips = {}
        for interface in netifaces.interfaces():
            if interface == "lo":
                continue
            ip = NetInfo.get_ip(interface)
            ip_dict = {"interface": interface, "ip": ip}
            ips.append(ip_dict)
        return ips

    @staticmethod
    def get_default_mac():
        interface_json = NetInfo.get_interfaces()
        # 如果有缺省的使用缺省的
        for key, interface_json in interface_json.items():
            if interface_json.get("is_default") and interface_json.get("macaddress"):
                return interface_json.get("macaddress")
        # 如果没有缺省的, 使用第一个非空的
        for interface in interface_json:
            interface_json = json.loads(interface)
            if interface_json.get("macaddress"):
                return interface_json.get("macaddress")
        # 2个都不满足, 返回空
        return None

    # 得到接口的mac地址信息
    @staticmethod
    def get_mac(interface):
        info = netifaces.ifaddresses(interface)
        # 地址信息
        mac = None
        info_mac = info.get(netifaces.AF_LINK)
        if info_mac:
            if len(info_mac) == 1:
                mac = info_mac[0].get("addr").replace(":", "").lower()
            else:
                logger.error("get mac address for interface {} wrong: {}".format(interface, str(info_mac)))
        else:
            logger.error("cannot get mac address for interface {}".format(interface))
        return mac

    # 得到所有的mac地址信息
    @staticmethod
    def get_macs():
        macs = []
        for interface in netifaces.interfaces():
            if interface == "lo":
                continue
            mac = NetInfo.get_mac(interface)
            if mac:
                macs.append(mac)
        return macs

    @staticmethod
    def get_basic():
        return NetInfo.get_interfaces()

    def get_advance(self):
        return self.get_access_interfaces()

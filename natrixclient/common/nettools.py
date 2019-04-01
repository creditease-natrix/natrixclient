#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging
import netifaces


logger = logging.getLogger(__name__)


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
def get_ips():
    ips = {}
    for interface in netifaces.interfaces():
        if interface == "lo":
            continue
        ip = get_ip(interface)
        ip_dict = {"interface": interface, "ip": ip}
        ips.append(ip_dict)
    return ips


# 得到接口的mac地址信息
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
def get_macs():
    macs = []
    for interface in netifaces.interfaces():
        if interface == "lo":
            continue
        mac = get_mac(interface)
        if mac:
            macs.append(mac)
    return macs

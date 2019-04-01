#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging
import json
import re
import urllib3
from functools import reduce
from natrixclient.common.const import HttpOperation
from natrixclient.command.nhttp import HttpTest


logger = logging.getLogger(__name__)


class IpPublic(object):
    def __init__(self, parameters=None):
        if parameters and parameters.get("logger"):
            global logger
            logger = logging.getLogger(parameters.get("logger"))

    @staticmethod
    def get_publicip(interface=None):
        return IpPublic.get_publicip_by_httpbin(interface)

    @staticmethod
    def get_publicip_by_httpbin(interface):
        pub_url = 'https://httpbin.org/ip'
        logger.debug("get public ip by url {}".format(pub_url))
        params = {
            "interface": interface,
            "save_response_body": True,
        }
        http = HttpTest(HttpOperation.GET, pub_url, params)
        result = http.execute()
        response_str = result.get("data").get("response_body")
        if response_str:
            response_json = json.loads(response_str)
        else:
            logger.warning("interface {} do not have public ip".format(interface))
            return None

        # TODO, 需要指定接口
        # pub_url = 'https://httpbin.org/ip'
        # response = requests.get(pub_url)
        myip = response_json.get("origin")
        if myip:
            try:
                publicip = re.search('\d+\.\d+\.\d+\.\d+', myip).group(0)
                logger.debug("interface {} public ip {}".format(interface, publicip))
                return publicip
            except AttributeError:
                logger.warning("interface {} cannot get public ip using {}, result {}".format(interface, pub_url, myip))
        else:
            logger.warning("interface {} cannot get public ip using {}".format(interface, pub_url))

    @staticmethod
    def get_publicip_by_3322(interface):
        pub_urls = ["http://www.3322.org/dyndns/getip"]
        for pub_url in pub_urls:
            try:
                publicip = IpPublic.visit(pub_url, interface)
                if IpPublic.check_ip(publicip):
                    return publicip
            except Exception as e:
                logger.exception("can not get public ip using: " + pub_url, exc_info=True)
        return ''

    @staticmethod
    def check_ip(ipaddr):
        if ipaddr is None or not ipaddr.strip():
            logger.error("The ip address is none or empty string")
            return False
        addr = ipaddr.strip().split('.')  # 切割IP地址为一个列表
        if len(addr) != 4:  # 切割后列表必须有4个参数
            logger.warning("The ip address can not be split into 4 section: " + ipaddr)
            return False
        for i in range(4):
            try:
                addr[i] = int(addr[i])  # 每个参数必须为数字，否则校验失败
            except ValueError:
                logger.warning("The section: " + str(i) + " in ip address " + ipaddr +
                               "can not be converted into integer")
                return False
            if addr[i] < 0 or addr[i] > 255:  # 每个参数值必须在0-255之间
                logger.warning("The section: " + str(i) + " in ip address " + ipaddr + " must between 0 and 255")
                return False
        return True

    @staticmethod
    def ip_into_int(ip):
        # 先把 192.168.1.13 变成16进制的 c0.a8.01.0d ，再去了“.”后转成10进制的 3232235789 即可。
        # (((((192 * 256) + 168) * 256) + 1) * 256) + 13
        return reduce(lambda x, y: (x << 8) + y, map(int, ip.split('.')))

    @staticmethod
    def visit(url, interface):
        # TODO, need to set interface
        logger.debug("get public ip from %s" % url)
        timeout = 5
        try:
            opener = urllib3.request.urlopen(url=url, timeout=timeout)
        except urllib3.request.URLError as e:
            logger.exception("url %s error " % url)
            return None
        except Exception as e:
            logger.exception("access url %s in %s seconds failed" % (url, str(timeout)))
            return None
        if url == opener.geturl():
            ip_response = opener.read().decode('utf-8')
            logger.debug("the origin response after decode utf-8: " + ip_response)
            publicip = re.search('\d+\.\d+\.\d+\.\d+', ip_response).group(0)
        else:
            publicip = None
        if publicip:
            logger.debug("public ip from %s is %s" % (url, publicip))
        else:
            logger.error("public ip from %s is None" % url)
        return publicip

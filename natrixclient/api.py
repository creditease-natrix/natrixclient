#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging
import time
from logging.handlers import RotatingFileHandler
from natrixclient.common import const
from natrixclient.common.const import API_LEVEL
from natrixclient.common.const import API_FILE_LEVEL
from natrixclient.common.const import API_STREAM_LEVEL
from natrixclient.common.const import FILE_MAX_BYTES
from natrixclient.common.const import FILE_BACKUP_COUNTS
from natrixclient.common.const import HttpOperation
from natrixclient.command.nping import PingTest
from natrixclient.command.nhttp import HttpTest
from natrixclient.command.ncheck import CheckTest
from natrixclient.command.ndns import DnsTest
from natrixclient.command.ntraceroute import RouteTest


"""
TODO
外部系统调用natrixclient的入口
外部系统安装
pip install natrixclient
使用
import natrixclient
params = {"count":3, "timeout": 1}
result = natrixclient.ping("www.baidu.com", params=params)
得到结果, 结果是json格式
"""


ln = "natrixclient_api"
logger = logging.getLogger(ln)
logger.setLevel(API_LEVEL)

# create file handler which logs even debug messages
fn = const.LOGGING_PATH + ln + '.log'
fh = RotatingFileHandler(filename=fn, maxBytes=FILE_MAX_BYTES, backupCount=FILE_BACKUP_COUNTS)
fh.setLevel(API_FILE_LEVEL)
fh_fmt = logging.Formatter(fmt=const.FILE_LOGGING_FORMAT, datefmt=const.FILE_LOGGING_DATE_FORMAT)
fh.setFormatter(fh_fmt)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(API_STREAM_LEVEL)
# create formatter and add it to the handlers
ch_fmt = logging.Formatter(fmt=const.CONSOLE_LOGGING_FORMAT)
ch.setFormatter(ch_fmt)

# add the handlers to logger
logger.addHandler(ch)
logger.addHandler(fh)


class NatrixClientAPI(object):
    def ping(self, destination, parameters=None):
        """
        :param destination: PING的destination
        :param parameters:
            count
            timeout
            interface
        :param config_file
            配置文件
        :return:
            ping dict result
        """
        logger.debug("natrix api ping")
        request_parameters = {"count": const.PING_COUNT, "timeout": const.PING_TIMEOUT}
        if parameters and parameters.get("count"):
            request_parameters["count"] = parameters.get("count")
        if parameters and parameters.get("timeout"):
            request_parameters["timeout"] = parameters.get("timeout")
        if parameters and parameters.get("interface"):
            request_parameters["interface"] = parameters.get("interface")
        # terminal_request_receive_time
        request_parameters["terminal_request_receive_time"] = time.time()
        request_parameters["logger"] = ln
        pingobj = PingTest(destination, request_parameters)
        result = pingobj.ping()
        result["stamp"]["terminal_response_return_time"] = time.time()
        return result

    def get(self, destination, parameters=None):
        logger.debug("natrix http get")
        result = self.http(HttpOperation.GET, destination, parameters)
        return result

    def post(self, destination, parameters=None):
        logger.debug("natrix api http post")
        result = self.http(HttpOperation.POST, destination, parameters)
        return result

    def put(self, destination, parameters=None):
        logger.debug("natrix api http put")
        result = self.http(HttpOperation.PUT, destination, parameters)
        return result

    def delete(self, destination, parameters=None):
        logger.debug("natrix api http delete")
        result = self.http(HttpOperation.DELETE, destination, parameters)
        return result

    def http(self, operation, destination, parameters=None):
        if not parameters:
            parameters = dict()
        parameters["terminal_request_receive_time"] = time.time()
        parameters["logger"] = ln
        http_obj = HttpTest(operation, destination, parameters)
        http_result = http_obj.execute()
        http_result["stamp"]["terminal_response_return_time"] = time.time()
        return http_result

    def performance(self, destination, params):
        logger.debug("natrix api performance")
        pass

    def dns(self, destination, parameters):
        logger.debug("natrix api dns")
        parameters["logger"] = ln
        parameters["terminal_request_receive_time"] = time.time()
        dns_obj = DnsTest(destination, parameters)
        dns_result = dns_obj.execute()
        dns_result["stamp"]["terminal_response_return_time"] = time.time()
        return dns_result

    def traceroute(self, destination, parameters=None):
        logger.debug("natrix api traceroute")
        parameters["logger"] = ln
        parameters["terminal_request_receive_time"] = time.time()
        route_obj = RouteTest(destination, parameters)
        route_result = route_obj.execute()
        route_result["stamp"]["terminal_response_return_time"] = time.time()
        return route_result

    def check(self, parameters):
        logger.debug("natrix api check")
        parameters["logger"] = ln
        check_test = CheckTest(parameters)
        check_result = check_test.check()
        return check_result


# if __name__ == '__main__':
#     params = dict()
#     ping_result = ping("http://www.baidu.com", params)
#     print(ping_result)






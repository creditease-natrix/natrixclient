# -*- coding: utf-8 -*-

import time
from natrixclient.common.natrix_logging import NatrixLogging
from natrixclient.common import const
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


ln = "natrixclient"
logger = NatrixLogging(ln)


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


if __name__ == '__main__':
    natrix_api = NatrixClientAPI()
    params = {'logger': logger}
    ping_result = natrix_api.http(const.HttpOperation.GET, "http://www.baidu.com", params)
    ping_result = natrix_api.http(const.HttpOperation.GET, "http://www.baidu.com", params)
    ping_result = natrix_api.http(const.HttpOperation.GET, "http://www.baidu.com", params)
    ping_result = natrix_api.http(const.HttpOperation.GET, "http://www.baidu.com", params)
    print(ping_result)






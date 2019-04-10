#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import threading
from natrixclient.common.config import NatrixConfig
from natrixclient.command.performance.webdriver import Firefox
from natrixclient.command.performance.webdriver import Chrome
from natrixclient.command.performance.webdriver import Curl


logger = logging.getLogger(__name__)


def execute(args):
    print("---------PERFORMANCE--------")
    print(args)


class BrowserPerformance():

    def execute(self, nconfig):
        print("==================Performance EXECUTE========================")
        destination = nconfig.get_value("DEFAULT", "destination")
        browser = nconfig.get_value("DEFAULT", "browser")
        mode = nconfig.get_value("DEFAULT", "mode")
        opt = nconfig.get_value("output", "type")

        if opt == "rabbitmq":
            conf = NatrixConfig()
            # TODO. need to decrypt password
            # TODO, for debug, log
            if nconfig.get_config()["DEFAULT"]["debug"].lower() == "true":
                print("rabbitmq_host = " + conf["host"])
                print("rabbitmq_port = " + conf["port"])
                print("rabbitmq_username = " + conf["username"])
                print("rabbitmq_password = " + conf["password"])
                print("rabbitmq_vhost = " + conf["vhost"])

        if browser not in ("curl", "firefox", "chrome"):
            msg = "invalid choice: '{}' (choose from 'firefox', 'chrome', 'curl')".format(browser)
            raise BrowserChooseException(msg)

        # rabbitmq_conf["destination"] = destination
        # execute performance
        PerformanceThread(destination, mode, browser, opt, **conf).start()


class PerformanceThread(threading.Thread):
    def __init__(self, dest, mode, browser, opt, **param):
        threading.Thread.__init__(self)
        self.dest = "http://" + dest if not dest.startswith("http") else dest
        self.mode = mode
        self.browser = browser
        self.opt = opt
        self.param = param

    def run(self):
        if self.browser in ("firefox", "chrome"):
            if self.mode == "time":
                per_result = Performance(self.dest, self.browser).get_time()
            elif self.mode == "resource":
                per_result = Performance(self.dest, self.browser).get_resources()
            elif self.mode == "data":
                per_result = Performance(self.dest, self.browser).get_performance()
            else:
                raise ValueError("invalid choice: {} (choose from 'time', 'resource', 'data')".format(self.mode))
        else:
            if self.mode == "data":
                per_result = Performance(self.dest, self.browser).curl_get_performance()
            else:
                raise ValueError("invalid choice: {} (curl only can choose 'data')".format(self.mode))

        per_result = json.dumps(per_result)
        print(per_result)

        self.param["operation"] = "performance"
        self.param["destination"] = self.dest
        parameters = self.param
        Output(self.opt, per_result, **parameters).store()


class Performance(object):
    def __init__(self, dest, browser):
        self.dest = dest
        self.browser = browser
        if self.browser == 'firefox':
            self.browser = Firefox()
        elif self.browser == 'chrome':
            self.browser = Chrome()
        elif self.browser == 'curl':
            self.browser = Curl()
        else:
            raise ValueError("invalid choice: {} (choose from 'firefox', 'chrome')".format(self.browser))

    # 浏览器获取页面整体请求时间元数据
    def get_time(self):
        try:
            time_result = self.browser.get_performance_timing(self.dest)
            data = json.loads(time_result)
            if 'toJSON' in data:
                del data['toJSON']
        except Exception as e:
            result = {
                "status": 1,
                "data": {
                    "errorinfo": "Invalid destination".format(self.dest),
                    "errorcode": 120
                }
            }
            return result
        result = {
            "status": 0,
            "data": data
        }
        return result

    # 浏览器获取资源请求数据
    def get_resources(self):
        try:
            resource_results = self.browser.get_performance_resource(self.dest)
            data = json.loads(resource_results)
        except Exception as e:
            result = {
                "status": 1,
                "data": {
                    "errorinfo": "Invalid destination".format(self.dest),
                    "errorcode": 120
                }
            }
            return result
        for res in data:
            if 'toJSON' in res:
                del res['toJSON']
        result = {
            "status": 0,
            "data": data,
        }
        return result

    # 浏览器获取整体(资源+时间)数据
    def get_performance(self):
        try:
            data = self.browser.get_performance(self.dest)
        except Exception as e:
            result = {
                "status": 1,
                "data": {
                    "errorinfo": "Invalid destination".format(self.dest),
                    "errorcode": 120
                }
            }
            return result
        time_data = data['timing']
        res_data = data['resources']
        if 'toJSON' in time_data:
            del time_data['toJSON']
        for res in res_data:
            if 'toJSON' in res:
                del res['toJSON']
        result = {
            "status": 0,
            "data": data
        }
        return result

    def curl_get_performance(self):
        try:
            data = Curl().get_performance(self.dest)
        except Exception as e:
            result = {
                "status": 1,
                "data": {
                    "errorinfo": "Invalid destination".format(self.dest),
                    "errorcode": 120
                }
            }
            return result
        if 'status' in data and data['status'] == 1:
            result = data
            return result

        data['status'] = 0
        result = data
        return result

# if __name__ == '__main__':
#     result = Performance("http://www.baidu.com", "chrome").get_performance()
#     print(result)

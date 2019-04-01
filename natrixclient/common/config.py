#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
from natrixclient.common import const


class NatrixConfig(object):
    """
    配置信息主要来自3个地方, 按照优先级如下
    1. 命令行设置 / API参数 / RABBITMQ获取数据
    2. configuration file (default /etc/natrix/natrix.ini)
    3. const.py
    """
    def __init__(self):
        self.config_path = const.CONFIG_PATH
        try:
            fnatrix = open(self.config_path, encoding='utf-8')
            fnatrix.close()
            # configuration parser
            pconfig = configparser.ConfigParser()
            pconfig.read(self.config_path)
            self.config_parser = pconfig
        except FileNotFoundError:
            # TODO, throw exception
            print("ERROR: Cannot find File {}".format(self.config_path))
            # raise FileNotFoundError()
        except PermissionError:
            # TODO, throw exception
            print("ERROR: Do not have permission to access File {}".format(self.config_path))
            # raise PermissionError()

    def get_value(self, fkey=None, skey=None):
        if self.config_parser:
            try:
                conf_value = self.config_parser[fkey][skey]
            except KeyError as k:
                raise KeyError("Config Key Error:{}".format(k))
        else:
            try:
                conf_name = fkey.strip().upper() + "_" + skey.strip().upper()
                conf_value = getattr(const, conf_name)
            except AttributeError as ae:
                raise KeyError("Default Key Error:{}".format(conf_name))
        return conf_value

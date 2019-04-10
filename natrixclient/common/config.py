#!/usr/bin/env python
# -*- coding: utf-8 -*-


import io
try:
    import configparser
except ImportError:
    import ConfigParser as configparser
from natrixclient.common import const
# for python2, IOError; for python3 FileNotFoundError
try:
    FileNotFoundError = FileNotFoundError
except NameError:
    FileNotFoundError = IOError
# for python2, OSError; for python3 FileNotFoundError
try:
    PermissionError = PermissionError
except NameError:
    PermissionError = OSError


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
            fnatrix = io.open(self.config_path, "r", encoding='utf-8')
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

    def get_value(self, section=None, option=None):
        if self.config_parser:
            try:
                conf_value = self.config_parser[section][option]
            except AttributeError:
                # python 2
                # TODO, add try ... except ...
                conf_value = self.config_parser.get(section, option)
            except KeyError as k:
                raise KeyError("Config Key Error:{}".format(k))
        else:
            try:
                conf_name = section.strip().upper() + "_" + option.strip().upper()
                conf_value = getattr(const, conf_name)
            except AttributeError as ae:
                raise KeyError("Default Key Error:{}".format(conf_name))
        return conf_value

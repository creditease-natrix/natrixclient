#!/usr/bin/env python
# -*- coding: utf-8 -*-


import distro
import logging
import platform
import natrixclient
from natrixclient.common.utils import get_command_output


'''
已经测试过的平台包括
    1. ubuntu       18.04       64位
    2. raspbian     stretch

# 相关参考资料
https://docs.python.org/2/library/platform.html
https://docs.python.org/3/library/platform.html
'''


logger = logging.getLogger(__name__)


class SystemInfo(object):
    def __init__(self, parameters=None):
        self.type = SystemInfo.get_type()
        self.series = SystemInfo.get_series()
        self.name = SystemInfo.get_name()
        self.codename = SystemInfo.get_codename()
        self.major_version = SystemInfo.get_major_version()
        self.minor_version = SystemInfo.get_minor_version()
        self.kernel_version = SystemInfo.get_kernel_version()
        self.architecture = SystemInfo.get_architecture()
        self.platform = SystemInfo.get_platform()
        self.python_version = SystemInfo.get_python_version()
        # 是否桌面版本
        self.desktop_version = self.get_desktop_version()
        self.selenium_version = self.get_selenium_version()
        self.chrome_version = self.get_chrome_version()
        self.chrome_webdriver_path, self.chrome_webdriver_version = self.get_chrome_webdirver()
        self.firefox_version = self.get_firefox_version()
        self.firefox_webdriver_path, self.firefox_webdriver_version = self.get_firefox_webdirver()
        # natrixclient版本信息
        self.natrixclient_version = self.get_natrixclient_version()
        # logger
        if parameters and parameters.get("logger"):
            global logger
            logger = logging.getLogger(parameters.get("logger"))

    # 操作系统类型, 例如Linux或Windows
    @staticmethod
    def get_type():
        type = platform.system()
        if not type:
            type = "UNKNOWN"
        return type

    # 操作系统系列, 例如debian或redhat
    @staticmethod
    def get_series():
        series = distro.like()
        if not series:
            series = "UNKNOWN"
        return series

    # 操作系统名称，例如ubuntu或centos
    @staticmethod
    def get_name():
        name = distro.name()
        if not name:
            name = "UNKNOWN"
        return name

    # 操作系统发行代号, 例如strech或'Bionic Beaver'
    @staticmethod
    def get_codename():
        codename = distro.codename()
        if not codename:
            codename = "UNKNOWN"
        return codename

    # 操作系统主版本号
    @staticmethod
    def get_major_version():
        major_version = distro.major_version()
        if not major_version:
            major_version = "UNKNOWN"
        return major_version

    # 操作系统次版本号
    @staticmethod
    def get_minor_version():
        minor_version = distro.minor_version()
        if not minor_version:
            minor_version = "UNKNOWN"
        return minor_version

    # 操作系统内核版本信息, 例如linux kernel的版本信息
    @staticmethod
    def get_kernel_version():
        kernel_version = platform.release()
        if not kernel_version:
            kernel_version = "UNKNOWN"
        return kernel_version

    # 操作系统架构信息, 例如 amd64 或 arm
    @staticmethod
    def get_architecture():
        architecture = "UNKNOWN"
        architectures = platform.architecture()
        if architectures and architectures[0]:
            architecture = architectures[0]
        return architecture

    # 综合平台信息，例如 'Linux-4.15.0-42-generic-x86_64-with-Ubuntu-18.04-bionic'
    @staticmethod
    def get_platform():
        pf = platform.platform()
        if not pf:
            pf = "UNKNOWN"
        return pf

    # python版本信息
    @staticmethod
    def get_python_version():
        pv = platform.python_version()
        if not pv:
            pv = "UNKNOWN"
        return pv

    # 0代表不是桌面版,
    def get_desktop_version(self):
        desktop_version = "UNKNOWN"
        if self.get_series() and "debian" == self.get_series().lower():
            status, output = get_command_output("dpkg -l | grep gnome-desktop3-data")
            if status == 0 and output:
                osp = output.split()
                if len(osp) > 2:
                    desktop_version = osp[2]
        return desktop_version

    # selenium版本信息, 0代表未安装
    # TODO, 得不到信息, 有BUG
    def get_selenium_version(self):
        selenium_version = "0"
        if self.get_python_version().split(".")[0] == "3":
            command = "pip3 list | grep selenium"
        else:
            command = "pip list | grep selenium"
        status, output = get_command_output(command)
        if status == 0:
            # some result like this
            # DEPRECATION: The default format will switch to columns in the future. You can use --format=(legacy|columns) (or define a format=(legacy|columns) in your pip.conf under the [list] section) to disable this warning.
            # selenium (3.141.0)
            rows = output.split("\n")
            for row in rows:
                if row and row.strip().lower().rfind("selenium") >= 0:
                    selenium_version = row.split()[1].strip("(").strip(")")
        return selenium_version

    # chrome版本信息, 0代表未安装
    def get_chrome_version(self):
        chrome_version = "0"
        if self.get_series() and "debian" == self.get_series().lower():
            command = "chromium-browser --version"
            status, output = get_command_output(command)
            if status == 0:
                chrome_version = output.split()[1]
        return chrome_version

    # chrome webdirver 路径和版本信息
    @staticmethod
    def get_chrome_webdirver():
        chrome_webdriver_path = ""
        chrome_webdirver_version = "0"
        chrome_webdriver_paths = ["/usr/local/bin/chromedriver", "/usr/lib/chromium-browser/chromedriver"]
        for path in chrome_webdriver_paths:
            command = "ls " + path
            status, output = get_command_output(command)
            if status == 0:
                chrome_webdriver_path = path
            break
        # 如果在这2个目录中找到了, 就得到版本信息.
        if chrome_webdriver_path:
            command = path + " --version"
            status, output = get_command_output(command)
            if status == 0:
                chrome_webdirver_version = output.split()[1]
        # 否则, 查找 chromedriver 文件, 得到版本信息
        else:
            # TODO, 查找 chromedriver, 得到版本信息
            pass
        return chrome_webdriver_path, chrome_webdirver_version

    # firefox版本信息, 0代表未安装
    # TODO, can not get info
    # Running Firefox as root in a regular user's session is not supported.
    def get_firefox_version(self):
        firefox_version = "0"
        if self.get_series() and "debian" == self.get_series().lower():
            command = "firefox --version"
            status, output = get_command_output(command)
            if status == 0:
                firefox_version = output.split()[2]
        return firefox_version

    # firefox webdirver 路径和版本信息
    @staticmethod
    def get_firefox_webdirver():
        firefox_webdriver_path = ""
        firefox_webdirver_version = "0"
        firefox_webdriver_paths = ["/usr/local/bin/geckodriver"]
        for path in firefox_webdriver_paths:
            command = "ls " + path
            status, output = get_command_output(command)
            if status == 0:
                firefox_webdriver_path = path
            break
        # 如果在这2个目录中找到了, 就得到版本信息.
        if firefox_webdriver_path:
            command = path + " --version"
            status, output = get_command_output(command)
            if status == 0:
                firefox_webdirver_version = output.split()[1]
        # 否则, 查找 chromedriver 文件, 得到版本信息
        else:
            # TODO, 查找 geckodriver, 得到版本信息
            pass
        return firefox_webdriver_path, firefox_webdirver_version

    # natrixclient的版本信息
    @staticmethod
    def get_natrixclient_version():
        return natrixclient.version()

    # 获取所有信息,以字典形式返回
    def get_advance(self):
        logger.debug("get system advance information")
        info = {
            "operating": {
                "type": self.type,
                "series": self.series,
                "name": self.name,
                "codename": self.codename,
                "major_version": self.major_version,
                "minor_version": self.minor_version,
                "kernel_version": self.kernel_version,
                "architecture": self.architecture,
                "platform": self.platform,
                "python_version": self.python_version,
                "desktop_version": self.desktop_version,
                "selenium_version": self.selenium_version,
                "chrome_version": self.chrome_version,
                "chrome_webdriver_path": self.chrome_webdriver_path,
                "chrome_webdriver_version": self.chrome_webdriver_version,
                "firefox_version": self.firefox_version,
                "firefox_webdriver_path": self.firefox_webdriver_path,
                "firefox_webdriver_version": self.firefox_webdriver_version,
            },
            "natrixclient": {
                "natrixclient_version": self.natrixclient_version,
            }
        }
        return info

    def get_basic(self):
        logger.debug("get system basic information")
        info = {
            "natrixclient_version": self.natrixclient_version,
        }
        return info




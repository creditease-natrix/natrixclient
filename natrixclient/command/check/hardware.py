#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
获取树莓派的硬件信息,包括cpu型号,内存大小,磁盘大小,网络接口流量,硬件版本(2B / 3B)
"""


import logging
import psutil
import socket
from natrixclient.command.check.system import SystemInfo
from natrixclient.command.check.network import NetInfo
from natrixclient.common.utils import get_command_output


logger = logging.getLogger(__name__)


class HardwareInfo(object):
    def __init__(self, parameters=None):
        # logger
        if parameters and parameters.get("logger"):
            global logger
            logger = logging.getLogger(parameters.get("logger"))

    # 对于unix-like系统(非raspbian), 使用
    # 如果得不到sn, 使用缺省网卡的mac地址
    @staticmethod
    def get_sn():
        sn = None
        system_type = SystemInfo.get_type().strip().lower()
        system_name = SystemInfo.get_name().strip().lower()
        if system_type == "linux":
            if system_name and system_name.strip().lower().find("raspbian") >= 0:
                # for raspberry pi
                # The serial number can be found in /proc/cpuinfo
                # cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2
                command = "cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2"
                status, output = get_command_output(command)
                if status == 0:
                    sn = output
                else:
                    logger.error("cannot get serial number from /proc/cpuinfo for raspbian")
            else:
                command1 = "sudo dmidecode -t system | grep -i serial | cut -d ':' -f 2"
                status1, output1 = get_command_output(command1)
                if status1 == 0 and output1.strip() != "0":
                    sn = output1.strip()
                else:
                    command2 = "sudo dmidecode -t system | grep UUID"
                    status2, output2 = get_command_output(command2)
                    if status2 == 0:
                        sn = output2.split(":")[1].strip()
                    else:
                        logger.error("cannot get uuid using dmidecode")
        else:
            logger.error("just support linux system")

        # 如果得不到sn, 使用缺省网卡的mac地址
        if not sn:
            sn = NetInfo.get_default_mac()
        return sn

    # 获取主机名,如果主机名不符合规范,重设主机名
    @staticmethod
    def get_hostname():
        hostname = socket.gethostname()
        logger.debug("get hostname = %s" % hostname)
        return hostname

    # 从操作系统获得树莓派硬件版本,目前没有别的更好的办法
    # cat /sys/firmware/devicetree/base/model
    # Raspberry Pi 3 Model B Rev 1.2
    # 对于其他的linux系统, 使用 dmidecode -t system | grep uuid
    @staticmethod
    def get_product():
        product = "UNKNOWN"
        if SystemInfo.get_type().strip().lower() == "linux":
            if SystemInfo.get_name().strip().lower() == "raspbian":
                try:
                    f = open('/sys/firmware/devicetree/base/model', 'r')
                    product = f.read()
                    f.close()
                except:
                    product = "get hardware product error in raspbian system"
            else:
                # need sudo
                command = "dmidecode -t system | grep \"Product Name\""
                status, output = get_command_output(command)
                if status == 0:
                    product = output.split(":")[1].strip()
                else:
                    product = "get hardware product error in unix-like system"
        return product

    # 获取开机时间
    @staticmethod
    def get_boot_time():
        return psutil.boot_time()

    @staticmethod
    def get_cpu_info(interval=1):
        cpu_info = {}
        # CPU型号
        # system_type = SystemInfo.get_type().strip().lower()
        # if system_type == "darwin":
        #     # for mac os
        #     mac_cpu_info = get_cpu_info()
        #     cpu_info["cpu_model"] = mac_cpu_info.get("brand")
        # else:
        #     with open('/proc/cpuinfo') as fd:
        #         for line in fd:
        #             if line.startswith('model name'):
        #                 cpu_model = line.split(':')[1].strip()
        #                 break
        cpu_model = "UNKNOWN"
        with open('/proc/cpuinfo') as fd:
            for line in fd:
                if line.startswith('model name'):
                    cpu_model = line.split(':')[1].strip()
                    break
        cpu_info["cpu_model"] = cpu_model
        # cpu 核心数
        cpu_info["cpu_core"] = psutil.cpu_count()
        # cpu 使用率
        # psutil.cpu_percent(interval=20,percpu=False)
        # interval：代表时间（秒），在这段时间内的cpu使用率
        # percpu：选择总的使用率还是每个cpu的使用率。False为总体，True为单个，返回列表
        cpu_info["cpu_percent"] = psutil.cpu_percent(interval)
        return cpu_info

    @staticmethod
    def get_memory_info():
        # 内存相关信息
        memory_info = {}
        memory = psutil.virtual_memory()
        memory_info["memory_total"] = memory.total
        memory_info["memory_used"] = memory.used
        memory_percent = "%.2f" % (memory.used / memory.total * 100)
        memory_info["memory_percent"] = float(memory_percent)
        # memory_info["memory_frequency"] = None
        return memory_info

    # 获取磁盘使用率
    @staticmethod
    def get_disk_info():
        disk_info = dict()
        disk_info["disk_percent"] = psutil.disk_usage('/').percent
        return disk_info

    @staticmethod
    def get_advance():
        info = {
            "sn": HardwareInfo.get_sn(),
            "hostname": HardwareInfo.get_hostname(),
            "product": HardwareInfo.get_product(),
            "boot_time": HardwareInfo.get_boot_time(),
            "cpu_info": HardwareInfo.get_cpu_info(),
            "memory_info": HardwareInfo.get_memory_info(),
            "disk_info": HardwareInfo.get_disk_info(),
        }
        return info

    @staticmethod
    def get_basic():
        info = {
            "sn": HardwareInfo.get_sn(),
            "hostname": HardwareInfo.get_hostname(),
            "cpu_percent": HardwareInfo.get_cpu_info().get("cpu_percent"),
            "memory_percent": HardwareInfo.get_memory_info().get("memory_percent"),
            "disk_percent": HardwareInfo.get_disk_info().get("disk_percent"),
        }
        return info

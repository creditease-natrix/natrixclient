#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging
import json
import threading
import time
from natrixclient.common.const import LOGGING_PATH
from natrixclient.common.const import FILE_MAX_BYTES
from natrixclient.common.const import FILE_BACKUP_COUNTS
from natrixclient.common.const import FILE_LOGGING_DATE_FORMAT
from natrixclient.common.const import THREAD_LOGGING_FORMAT
from natrixclient.command.check.network import NetInfo
from natrixclient.command.check.hardware import HardwareInfo
from natrixclient.command.check.system import SystemInfo
from natrixclient.command.storage import storage
from natrixclient.common.config import NatrixConfig


logger = logging.getLogger(__name__)


def add_logger_handler(logger):
    fn = LOGGING_PATH + 'natrixclient_check.log'
    fh = logging.handlers.RotatingFileHandler(filename=fn, maxBytes=FILE_MAX_BYTES, backupCount=FILE_BACKUP_COUNTS)
    fh.setLevel(logging.DEBUG)
    fh_fmt = logging.Formatter(fmt=THREAD_LOGGING_FORMAT, datefmt=FILE_LOGGING_DATE_FORMAT)
    fh.setFormatter(fh_fmt)
    logger.addHandler(fh)


def execute(request_parameters, response_parameters):
    if request_parameters.get("logger"):
        global logger
        logger = logging.getLogger(request_parameters.get("logger"))
        add_logger_handler(logger)
    logger.info("==================CHECK EXECUTE========================")
    # execute check
    CheckThread(request_parameters=request_parameters,
                response_parameters=response_parameters).start()


class CheckThread(threading.Thread):
    def __init__(self, request_parameters, response_parameters):
        threading.Thread.__init__(self)
        self.request_parameters = request_parameters
        self.response_parameters = response_parameters

    def run(self):
        check_obj = CheckTest(self.request_parameters)
        check_dict = check_obj.check()

        storage(result=check_dict, parameters=self.response_parameters)


class CheckTest(object):
    def __init__(self, request_parameters):
        self.parameters = request_parameters
        # logger
        if request_parameters.get("logger"):
            global logger
            logger = logging.getLogger(request_parameters.get("logger"))
            add_logger_handler(logger)
        self.check_type = request_parameters.get("type")
        self.config = NatrixConfig()

    def check(self):
        pi_info = {}
        if self.check_type in ("system", "basic", "advance"):
            logger.debug("get system information ... ")
            sys_info_obj = SystemInfo(self.parameters)
            if self.check_type == "basic":
                sys_info_result = sys_info_obj.get_basic()
            else:
                sys_info_result = sys_info_obj.get_advance()
            if sys_info_result:
                logger.debug("system information: %s " % json.dumps(sys_info_result))
                pi_info["system"] = sys_info_result

        if self.check_type in ("hardware", "basic", "advance"):
            logger.debug("get hardware information ... ")
            hard_info_obj = HardwareInfo(self.parameters)
            if self.check_type == "basic":
                hard_info_result = hard_info_obj.get_basic()
            else:
                hard_info_result = hard_info_obj.get_advance()
            if hard_info_result:
                logger.debug("hardware information: %s " % json.dumps(hard_info_result))
                pi_info["hardware"] = hard_info_result
                # print(hard_info_result)

        if self.check_type in ("network", "basic", "advance"):
            logger.debug("get network information ... ")
            net_info_obj = NetInfo(self.parameters)
            if self.check_type == "basic":
                net_info_result = net_info_obj.get_advance()
            else:
                net_info_result = net_info_obj.get_advance()
            if net_info_result:
                logger.debug("network information: %s " % json.dumps(net_info_result))
                pi_info["networks"] = net_info_result

        pi_info["heartbeat"] = time.time()

        logger.debug("reporter data: %s" % json.dumps(pi_info))
        return pi_info

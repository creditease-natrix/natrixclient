# -*- coding: utf-8 -*-

import json
import threading
import time

from natrixclient.command.check.network import NetInfo
from natrixclient.command.check.hardware import HardwareInfo
from natrixclient.command.check.system import SystemInfo
from natrixclient.command.storage import storage
from natrixclient.common.config import NatrixConfig
from natrixclient.common.natrix_logging import NatrixLogging


logger = NatrixLogging(__name__)


def execute(request_parameters, response_parameters):
    logger.print('==================CHECK EXECUTE========================')
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
        self.check_type = request_parameters.get('type')
        # not use
        self.config = NatrixConfig()

    def check(self):
        device_info = {}
        
        # system-related information
        if self.check_type in ('system', 'basic', 'advance'):
            sys_info_obj = SystemInfo(self.parameters)
            if self.check_type == 'basic':
                sys_info_result = sys_info_obj.get_basic()
            else:
                sys_info_result = sys_info_obj.get_advance()

            if sys_info_result:
                logger.debug('system information: %s ' % json.dumps(sys_info_result))
                device_info['system'] = sys_info_result
            else:
                logger.error('Cant get system information({})'.format(self.check_type))

        # hardware-related information
        if self.check_type in ('hardware', 'basic', 'advance'):
            hard_info_obj = HardwareInfo(self.parameters)
            if self.check_type == 'basic':
                hard_info_result = hard_info_obj.get_basic()
            else:
                hard_info_result = hard_info_obj.get_advance()
            if hard_info_result:
                logger.debug('hardware information: %s ' % json.dumps(hard_info_result))
                device_info['hardware'] = hard_info_result
            else:
                logger.error('Cant get hardware information({})'.format(self.check_type))

        if self.check_type in ('network', 'basic', 'advance'):
            net_info_obj = NetInfo(self.parameters)
            if self.check_type == 'basic':
                net_info_result = net_info_obj.get_advance()
            else:
                net_info_result = net_info_obj.get_advance()

            if net_info_result:
                logger.debug('network information: %s ' % json.dumps(net_info_result))
                device_info['networks'] = net_info_result
            else:
                logger.error('Cant get network information({})'.format(self.check_type))

        device_info['heartbeat'] = time.time()

        logger.debug('reporter data: %s' % json.dumps(device_info))
        return device_info

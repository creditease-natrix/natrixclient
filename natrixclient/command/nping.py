# -*- coding: utf-8 -*-

import logging
import threading
import time
from natrixclient.common.const import PING_COUNT
from natrixclient.common.const import PING_TIMEOUT
from natrixclient.common.const import LOGGING_PATH
from natrixclient.common.const import FILE_MAX_BYTES
from natrixclient.common.const import FILE_BACKUP_COUNTS
from natrixclient.common.const import FILE_LOGGING_DATE_FORMAT
from natrixclient.common.const import THREAD_LOGGING_FORMAT
from natrixclient.command.check.iplocation import IpLocation
from natrixclient.command.ping.pyping import Ping
from natrixclient.command.storage import storage

"""
request_parameters
{
    "interface": "eth0",
    "count": 3,
    "timeout": 10
}
response_parameters
{
    # storage_type, will be console/rabbitmq/file/restful
    "storage_type": "console",
    # for file
    "storage_path": "/var/log/natrix",
    "storage_file": "test.log",
    # for rabbitmq
    "storage_exchange": "exchange_name",
    "storage_queue": "queue_name",
    "storage_routing": "routing_name",
    # for rabbitmq
    "command_uuid": "test",
    "command_terminal": "xxxxxxxxxxx",
    "command_generate_timestamp": 12345678,
}
"""


logger = logging.getLogger(__name__)


def add_logger_handler(logger):
    fn = LOGGING_PATH + 'natrixclient_ping.log'
    fh = logging.handlers.RotatingFileHandler(filename=fn, maxBytes=FILE_MAX_BYTES, backupCount=FILE_BACKUP_COUNTS)
    fh.setLevel(logging.DEBUG)
    fh_fmt = logging.Formatter(fmt=THREAD_LOGGING_FORMAT, datefmt=FILE_LOGGING_DATE_FORMAT)
    fh.setFormatter(fh_fmt)
    logger.addHandler(fh)


def execute(destination, request_parameters, response_parameters):
    # logger
    if request_parameters.get("logger"):
        global logger
        logger = logging.getLogger(request_parameters.get("logger"))
        add_logger_handler(logger)
    logger.info("==================PING EXECUTE========================")
    # TODO, need to check interface exist and connection
    # execute ping
    PingThread(destination, request_parameters, response_parameters).start()


class PingThread(threading.Thread):
    def __init__(self, destination, request_parameters, response_parameters):
        threading.Thread.__init__(self)
        self.destination = destination
        self.request_parameters = request_parameters
        self.response_parameters = response_parameters

    def run(self):
        ping_obj = PingTest(self.destination, self.request_parameters)
        ping_dict = ping_obj.ping()
        # command
        logger.debug("processing ping command response infomation ...")
        if self.response_parameters.get("command_uuid"):
            command = dict()
            command["uuid"] = self.response_parameters.get("command_uuid")
            command["terminal"] = self.response_parameters.get("command_terminal")
            ping_dict["command"] = command
        logger.debug("storaging ping response ...")
        storage(result=ping_dict, parameters=self.response_parameters)


class PingTest(object):
    def __init__(self, destination, parameters):
        self.destination = destination
        # parameters
        self.parameters = parameters
        # logger
        if parameters.get("logger"):
            global logger
            logger = logging.getLogger(parameters.get("logger"))
            add_logger_handler(logger)
        self.server_request_generate_time = parameters.get("server_request_generate_time")
        self.terminal_request_receive_time = parameters.get("terminal_request_receive_time")
        self.terminal_interface = parameters.get("interface", None)
        # count
        if parameters and parameters.get("count"):
            self.count = int(parameters.get("count"))
        else:
            self.count = PING_COUNT
        # timeout
        if parameters and parameters.get("timeout"):
            self.timeout = int(parameters.get("timeout")) * 1000
        else:
            self.timeout = PING_TIMEOUT

    def ping(self):
        try:
            terminal_request_send_time = time.time()
            logger.debug("starting ping {} ......".format(self.destination))
            pobj = Ping(self.destination, self.parameters)
            data = pobj.ping()
            logger.debug("ending ping {} ......".format(self.destination))
            terminal_response_receive_time = time.time()
        except Exception as e:
            ping_result = {
                "status": 1,
                "data": {
                    "errorinfo": e,
                    "errorcode": 140
                }
            }
            return ping_result

        if data:
            ipt = IpLocation(self.parameters)
            ping_result = {
                "status": 0,
                "data": {
                    "destination": self.destination,
                    "destination_ip": data.destination_ip,
                    "destination_location": ipt.get_location(data.destination_ip),
                    "packet_send": self.count,
                    "packet_receive": (self.count - data.packet_lost),
                    "packet_loss": data.packet_lost,
                    "packet_size": data.packet_size,
                    "avg_time": data.avg_rtt,
                    "max_time": data.max_rtt,
                    "min_time": data.min_rtt,
                },
                "stamp": {
                    "server_request_generate_time": self.server_request_generate_time,
                    "terminal_request_receive_time": self.terminal_request_receive_time,
                    "terminal_request_send_time": terminal_request_send_time,
                    "terminal_response_receive_time": terminal_response_receive_time,
                }
            }
        else:
            ping_result = {
                "status": 1,
                "data": {
                    "errorinfo": "Unable to establish communication, data acquisition failed:" + self.destination,
                    "errorcode": 141
                },
                "stamp": {
                    "server_request_generate_time": self.server_request_generate_time,
                    "terminal_request_receive_time": self.terminal_request_receive_time,
                    "terminal_request_send_time": terminal_request_send_time,
                    "terminal_response_receive_time": terminal_response_receive_time,
                }
            }
        return ping_result


if __name__ == '__main__':
    pingobj = PingTest("www.baidu.com.com", 3, 3)
    result = pingobj.ping()
    print(result)

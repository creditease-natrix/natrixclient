#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import logging
import os
import subprocess
import time
import threading
from natrixclient.common.const import LOGGING_PATH
from natrixclient.common.const import FILE_MAX_BYTES
from natrixclient.common.const import FILE_BACKUP_COUNTS
from natrixclient.common.const import FILE_LOGGING_DATE_FORMAT
from natrixclient.common.const import THREAD_LOGGING_FORMAT
from natrixclient.common.const import TRACEROUTE_ICMP
from natrixclient.common.const import TRACEROUTE_TCP
from natrixclient.common.const import TRACEROUTE_UDP
from natrixclient.common.const import TRACEROUTE_MAX_HOPS
from natrixclient.command.check.iplocation import IpLocation
from natrixclient.command.storage import storage


"""
request_parameters
{
    "interface": "eth0",
    "protocol": "icmp",
    "max_hops": 10
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
    "command_uuid": "test",
    "command_terminal": "xxxxxxxxxxx",
    "command_generate_timestamp": 12345678,
}
"""


logger = logging.getLogger(__name__)


def add_logger_handler(logger):
    fn = LOGGING_PATH + 'natrixclient_traceroute.log'
    fh = logging.handlers.RotatingFileHandler(filename=fn, maxBytes=FILE_MAX_BYTES, backupCount=FILE_BACKUP_COUNTS)
    fh.setLevel(logging.DEBUG)
    fh_fmt = logging.Formatter(fmt=THREAD_LOGGING_FORMAT, datefmt=FILE_LOGGING_DATE_FORMAT)
    fh.setFormatter(fh_fmt)
    logger.addHandler(fh)


def execute(destination, request_parameters, response_parameters):
    if request_parameters.get("logger"):
        global logger
        logger = logging.getLogger(request_parameters.get("logger"))
        add_logger_handler(logger)
    logger.info("==================TRACEROUTE EXECUTE========================")
    RouteThread(destination, request_parameters, response_parameters).start()


class RouteThread(threading.Thread):
    def __init__(self, destination, request_parameters, response_parameters):
        threading.Thread.__init__(self)
        self.destination = destination
        self.request_parameters = request_parameters
        self.response_parameters = response_parameters

    def run(self):
        route_obj = RouteTest(self.destination, self.request_parameters)
        route_dict = route_obj.execute()

        if self.response_parameters.get("command_uuid"):
            command = dict()
            command["uuid"] = self.response_parameters.get("command_uuid")
            command["terminal"] = self.response_parameters.get("command_terminal")
            route_dict["command"] = command

        logger.debug("storage route result")
        storage(result=route_dict, parameters=self.response_parameters)


class RouteTest(object):
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
        self.traceroute_icmp = parameters.get("traceroute_icmp", TRACEROUTE_ICMP)
        self.traceroute_tcp = parameters.get("traceroute_tcp", TRACEROUTE_TCP)
        self.traceroute_udp = parameters.get("traceroute_udp", TRACEROUTE_UDP)
        self.traceroute_method = "-I"
        self.traceroute_interface = parameters.get("traceroute_interface")
        self.traceroute_max_hops = parameters.get("traceroute_max_hops", TRACEROUTE_MAX_HOPS)

    def execute(self):
        # Finding traceroute path
        route_paths = ["/usr/bin/traceroute", "/usr/sbin/traceroute"]
        route_command = None
        for route_path in route_paths:
            if os.path.isfile(route_path):
                logger.debug("traceroute command exist in %s" % route_path)
                route_command = route_path
                break
            else:
                logger.warning("traceroute command do not exist in %s" % route_path)
        if not route_command:
            which_route = ['which', 'traceroute']
            which_route_proc = subprocess.Popen(which_route, stdout=subprocess.PIPE)
            which_route_value = which_route_proc.communicate()
            if which_route_value[0]:
                route_command = which_route_value[0].decode().strip('\n')
            else:
                erromsg = "Can not find command traceroute, please install it manually"
                logger.error(erromsg)
                error_info = {"errorcode": 100, "errorinfo": erromsg}
                result = {
                    "status": 1,
                    "data": error_info
                }
                return result

        # Determine the "method" parameter, specifying the type of traceroute sending packet.
        if self.traceroute_icmp:
            self.traceroute_method = "-I"
        elif self.traceroute_udp:
            self.traceroute_method = "-U"
        elif self.traceroute_tcp:
            self.traceroute_method = "-T"
        else:
            self.traceroute_method = "-I"

        # Read command line
        if self.traceroute_interface:
            route_cmd = [route_command, self.traceroute_method, "-i", self.traceroute_interface, "-m", str(self.traceroute_max_hops), self.destination]
        else:
            route_cmd = [route_command, self.traceroute_method, "-m", str(self.traceroute_max_hops), self.destination]

        try:
            traceroute_list = []
            # terminal_request_send_time
            terminal_request_send_time = time.time()
            route_proc = subprocess.Popen(route_cmd, stdout=subprocess.PIPE)
            route_value = route_proc.communicate()
            if route_value and route_value[0]:
                logger.debug("route_result = %s" % route_value[0])
                route_values = route_value[0].decode().split("\n")
                for route_item in route_values[1:]:
                    logger.debug("route_item = {}".format(route_item))
                    items = route_item.split()
                    if items:
                        traceroute_item = dict()
                        ttl = int(items[0].strip())
                        traceroute_item["seq"] = ttl
                        routes = self.parse_routes(items[1:])
                        traceroute_item["routes"] = routes
                        traceroute_list.append(traceroute_item)
                result = {
                    "status": 0,
                    "data": traceroute_list,
                    "stamp": {
                        "server_request_generate_time": self.server_request_generate_time,
                        "terminal_request_receive_time": self.terminal_request_receive_time,
                        "terminal_request_send_time": terminal_request_send_time,
                        "terminal_response_receive_time": time.time(),
                    }
                }
                return result
            else:
                if route_value:
                    erromsg = "execute command %s, return: %s" % (route_cmd, json.dumps(route_value))
                else:
                    erromsg = "execute command %s, return: None" % route_cmd
                logger.error(erromsg)
                error_info = {"errorcode": 103, "errorinfo": erromsg}
                result = {
                    "status": 1,
                    "data": error_info,
                    "stamp": {
                        "server_request_generate_time": self.server_request_generate_time,
                        "terminal_request_receive_time": self.terminal_request_receive_time,
                        "terminal_request_send_time": terminal_request_send_time,
                        "terminal_response_receive_time": time.time(),
                    }
                }
                return result
        except subprocess.CalledProcessError as err:
            erromsg = "Can not execute command %s, exception: %s" % (route_cmd, err.stderr)
            logger.exception(erromsg)
            error_info = {"errorcode": 101, "errorinfo": erromsg}
            result = {
                "status": 1,
                "data": error_info,
                "stamp": {
                    "server_request_generate_time": self.server_request_generate_time,
                    "terminal_request_receive_time": self.terminal_request_receive_time,
                    "terminal_request_send_time": terminal_request_send_time,
                    "terminal_response_receive_time": time.time(),
                }
            }
            return result
        except Exception as err:
            erromsg = "Can not execute command %s, exception: %s" % (route_cmd, err)
            logger.exception(erromsg)
            error_info = {"errorcode": 102, "errorinfo": erromsg}
            result = {
                "status": 1,
                "data": error_info,
                "stamp": {
                    "server_request_generate_time": self.server_request_generate_time,
                    "terminal_request_receive_time": self.terminal_request_receive_time,
                    "terminal_request_send_time": terminal_request_send_time,
                    "terminal_response_receive_time": time.time(),
                }
            }
            return result

    def parse_routes(self, items):
        routes = []
        while items:
            if items[0] == '*':
                logger.debug("parse traceroute like: *")
                route = {'ip': '*', 'hostname': '*', 'location': None, 'response_times': 0}
                items = items[1:]
            elif items.index('ms') == 3:
                logger.debug("parse traceroute like: \"bogon (10.199.13.51)  6.527 ms\"")
                hostname = items[0].strip()
                ip = items[1].strip('(').strip(')').strip()
                ipt = IpLocation(self.parameters)
                location = ipt.get_location(ip)
                rtime = float(items[2])
                route = {'ip': ip, 'hostname': hostname, 'location': location, 'response_times': rtime}
                items = items[4:]
            elif items.index('ms') == 1:
                logger.debug("parse traceroute like: \"6.527 ms\"")
                rtime = float(items[0])
                preroute = routes[len(routes) - 1]
                if preroute:
                    route = {'ip': preroute['ip'], 'hostname': preroute['hostname'], 'location': preroute['location'],
                             'response_times': rtime}
                else:
                    route = {'ip': '*', 'hostname': '*', 'location': '', 'response_times': rtime}
                items = items[2:]
            else:
                logger.error("Can not parse route: %s" % items)
            routes.append(route)
        return routes


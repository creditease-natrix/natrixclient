#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import socket
import time
import threading
import dns
from dns import rdatatype
from dns import resolver
from natrixclient.common.const import DNS_METHOD
from natrixclient.common.const import DNS_TIMEOUT
from natrixclient.common.const import LOGGING_PATH
from natrixclient.common.const import FILE_MAX_BYTES
from natrixclient.common.const import FILE_BACKUP_COUNTS
from natrixclient.common.const import FILE_LOGGING_DATE_FORMAT
from natrixclient.common.const import THREAD_LOGGING_FORMAT
from natrixclient.common.const import DnsMethod
from natrixclient.command.check.iplocation import IpLocation
from natrixclient.command.ndnserror import DnsError
from natrixclient.command.storage import storage


logger = logging.getLogger(__name__)


def add_logger_handler(logger):
    fn = LOGGING_PATH + 'natrixclient_dns.log'
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
    logger.info("=====================DNS EXECUTE======================")
    # execute dns query
    DnsThread(destination, request_parameters, response_parameters).start()


class DnsThread(threading.Thread):
    def __init__(self, destination, request_parameters, response_parameters):
        threading.Thread.__init__(self)
        self.destination = destination
        self.request_parameters = request_parameters
        self.response_parameters = response_parameters

    def run(self):
        dns_obj = DnsTest(self.destination, self.request_parameters)
        dns_dict = dns_obj.execute()

        if self.response_parameters.get("command_uuid"):
            command = dict()
            command["uuid"] = self.response_parameters.get("command_uuid")
            command["terminal"] = self.response_parameters.get("command_terminal")
            dns_dict["command"] = command

        # dns_result = json.dumps(dns_dict)
        storage(result=dns_dict, parameters=self.response_parameters)


class DnsTest(object):
    def __init__(self, destination, parameters):
        # destination
        self.destination = destination
        self.parameters = parameters
        # logger
        if parameters.get("logger"):
            global logger
            logger = logging.getLogger(parameters.get("logger"))
            add_logger_handler(logger)
        # server_request_generate_time
        self.server_request_generate_time = parameters.get("server_request_generate_time")
        # terminal_request_receive_time
        self.terminal_request_receive_time = parameters.get("terminal_request_receive_time")
        # terminal_request_send_time
        self.terminal_request_send_time = None
        # terminal_response_receive_time
        self.terminal_response_receive_time = None
        self.dns_server = parameters.get("dns_server", None)
        self.dns_method = parameters.get("dns_method", DNS_METHOD)
        self.dns_timeout = parameters.get("dns_timeout", DNS_TIMEOUT)
        # python2 self.dns_method.lower() == DnsMethod.A
        if self.dns_method.lower() == DnsMethod.A or self.dns_method.lower() == DnsMethod.A.value:
            self.rdtype = rdatatype.A
        elif self.dns_method.lower() == DnsMethod.CNAME or self.dns_method.lower() == DnsMethod.CNAME.value:
            self.rdtype = rdatatype.CNAME
        elif self.dns_method.lower() == DnsMethod.NS or self.dns_method.lower() == DnsMethod.NS.value:
            self.rdtype = rdatatype.NS
        elif self.dns_method.lower() == DnsMethod.MX or self.dns_method.lower() == DnsMethod.MX.value:
            self.rdtype = rdatatype.MX
        else:
            logger.error("Unknown Type {}, will use default {}".format(self.dns_method, DNS_METHOD))
            self.rdtype = rdatatype.A

    def execute(self):
        data = dict()
        ip_list = []
        cname_list = []
        mx_list = []
        ns_list = []

        # terminal_request_send_time
        self.terminal_request_send_time = time.time()
        self.parameters["terminal_request_send_time"] = self.terminal_request_send_time
        if self.dns_server:
            try:
                dns_query = dns.message.make_query(qname=self.destination, rdtype=self.rdtype)
                querya = dns.query.udp(dns_query, self.dns_server, timeout=self.dns_timeout)
                data_ptime = querya.time * 1000
                answer = querya.answer
            except dns.exception.Timeout as e:
                logger.exception("dns timeout exception")
                return DnsError(url=self.destination, error=e, parameters=self.parameters).dns_timeout_error()
            except (resolver.NXDOMAIN, socket.gaierror) as e:
                logger.exception("dns server exception")
                return DnsError(url=self.destination, error=e, parameters=self.parameters).dns_server_error()
        else:
            dns_servers = resolver.get_default_resolver().nameservers
            if not dns_servers:
                logger.error("do not have dns servers")
                return DnsError(url=self.destination, parameters=self.parameters).miss_default_error()

            dns_query = dns.message.make_query(qname=self.destination, rdtype=self.rdtype)

            timeout_flag = 0
            dns_server_flag = 0
            for dns_server in dns_servers:
                try:
                    querya = dns.query.udp(dns_query, dns_server, timeout=self.dns_timeout)
                    data_ptime = querya.time * 1000
                    answer = querya.answer
                    self.dns_server = dns_server
                    break
                except dns.exception.Timeout as e:
                    logger.exception("dns server {} got timeout exception".format(str(dns_server)))
                    timeout_flag += 1
                    if timeout_flag + dns_server_flag == len(dns_servers):
                        return DnsError(url=self.destination, error=e, parameters=self.parameters).dns_timeout_error()
                except (resolver.NXDOMAIN, socket.gaierror) as e:
                    logger.exception("dns server {} got server exception".format(str(dns_server)))
                    dns_server_flag += 1
                    if timeout_flag + dns_server_flag == len(dns_servers):
                        return DnsError(url=self.destination, error=e, parameters=self.parameters).dns_server_error()

        self.terminal_response_receive_time = time.time()

        ipt = IpLocation(self.parameters)

        for queryans in answer:
            for item in queryans.items:
                # A记录 又称IP指向
                if item.rdtype == rdatatype.A:
                    ip_dict = dict()
                    ip = item.address
                    ip_dict["ip"] = ip
                    location = ipt.get_location(ip)
                    ip_dict["location"] = location
                    ip_list.append(ip_dict)
                #  CNAME 通常称别名指向
                elif item.rdtype == rdatatype.CNAME:
                    cname_list.append(str(item.target))
                # MAIL记录
                elif item.rdtype == rdatatype.MX:
                    mx_list.append(str(item.exchange))
                # NS记录
                elif item.rdtype == rdatatype.NS:
                    ns_list.append(str(item.target))

        if self.dns_method == "mx":
            if mx_list:
                data["mxs"] = mx_list
            else:
                return DnsError(url=self.destination, parameters=self.parameters).dns_query_error()
        elif self.dns_method == "a":
            if ip_list:
                data["ips"] = ip_list
            else:
                return DnsError(url=self.destination, parameters=self.parameters).dns_query_error()
        elif self.dns_method == "ns":
            if ns_list:
                data["ns"] = ns_list
            else:
                return DnsError(url=self.destination, parameters=self.parameters).dns_query_error()
        elif self.dns_method == "cname":
            if cname_list:
                data["cnames"] = cname_list
            else:
                return DnsError(url=self.destination, parameters=self.parameters).dns_query_error()
        else:
            return DnsError(url=self.destination, parameters=self.parameters).dns_query_error()
        data["destination"] = self.destination
        data["ptime"] = data_ptime
        data["dns_server"] = dict()
        data["dns_server"]["ip"] = self.dns_server
        data["dns_server"]["location"] = ipt.get_location(self.dns_server)

        result = {
            "status": 0,
            "data": data,
            "stamp": {
                "server_request_generate_time": self.server_request_generate_time,
                "terminal_request_receive_time": self.terminal_request_receive_time,
                "terminal_request_send_time": self.terminal_request_send_time,
                "terminal_response_receive_time": self.terminal_response_receive_time,
            }
        }
        return result

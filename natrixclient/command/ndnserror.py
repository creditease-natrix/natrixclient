# -*- coding: utf-8 -*-


import time
from natrixclient.common import const


class DnsError(object):
    def __init__(self, url=None, error=None, parameters=None):
        self.url = url
        self.dnstype = parameters.get("dnstype", const.DNS_METHOD)
        self.timeout = parameters.get("timeout", const.DNS_TIMEOUT)
        self.dnsserver = parameters.get("dnsserver", None)
        self.error = error
        self.server_request_generate_time = parameters.get("server_request_generate_time")
        self.terminal_request_receive_time = parameters.get("terminal_request_receive_time")
        self.terminal_request_send_time = parameters.get("terminal_request_send_time")
        self.terminal_response_receive_time = time.time()

    def dns_server_error(self):
        result = {
            "status": 1,
            "data": {
                "errorinfo": "Name or service not known:{}".format(self.dnsserver),
                "errorcode": 101
            },
            "stamp": {
                "server_request_generate_time": self.server_request_generate_time,
                "terminal_request_receive_time": self.terminal_request_receive_time,
                "terminal_request_send_time": self.terminal_request_send_time,
                "terminal_response_receive_time": self.terminal_response_receive_time,
            }
        }
        return result

    def dns_timeout_error(self):
        result = {
            "status": 1,
            "data": {
                "errorinfo": "The DNS operation timed out.(timeout={})".format(self.timeout),
                "errorcode": 102
            },
            "stamp": {
                "server_request_generate_time": self.server_request_generate_time,
                "terminal_request_receive_time": self.terminal_request_receive_time,
                "terminal_request_send_time": self.terminal_request_send_time,
                "terminal_response_receive_time": self.terminal_response_receive_time,
            }
        }
        return result

    def dns_query_error(self):
        result = {
            "status": 1,
            "data": {
                "errorinfo": "Unable to get '{}' record for {}".format(self.dnstype, self.url),
                "errorcode": 103
            },
            "stamp": {
                "server_request_generate_time": self.server_request_generate_time,
                "terminal_request_receive_time": self.terminal_request_receive_time,
                "terminal_request_send_time": self.terminal_request_send_time,
                "terminal_response_receive_time": self.terminal_response_receive_time,
            }
        }
        return result

    def record_error(self):
        result = {
            "status": 1,
            "data": {
                "errorinfo": "the resolved mode '{}' is invalid, "
                             "choose from ('mx', 'a', 'cname', 'ns') ".format(self.dnstype),
                "errorcode": 104
            },
            "stamp": {
                "server_request_generate_time": self.server_request_generate_time,
                "terminal_request_receive_time": self.terminal_request_receive_time,
                "terminal_request_send_time": self.terminal_request_send_time,
                "terminal_response_receive_time": self.terminal_response_receive_time,
            }
        }
        return result

    def miss_default_error(self):
        result = {
            "status": 1,
            "data": {
                "errorinfo": "Unable to get default DNS",
                "errorcode": 105
            },
            "stamp": {
                "server_request_generate_time": self.server_request_generate_time,
                "terminal_request_receive_time": self.terminal_request_receive_time,
                "terminal_request_send_time": self.terminal_request_send_time,
                "terminal_response_receive_time": self.terminal_response_receive_time,
            }
        }
        return result

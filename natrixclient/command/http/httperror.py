# -*- coding: utf-8 -*-


class HttpError(object):

    def __init__(self, url=None, timeout=None):
        self.url = url
        self.timeout = timeout

    def connection_error(self):
        data = {
            "errorcode": 152,
            "errorinfo": "Name or service not known {}".format(self.url)
        }
        result = {
            "status": 1,
            "data": data
        }
        return result

    def connect_timeout(self):
        data = {
            "errorcode": 151,
            "errorinfo": "Connection to {} timed out. (connect timeout={})".format(self.url, self.timeout)
        }
        result = {
            "status": 1,
            "data": data
        }
        return result

    def read_timeout(self):
        data = {
            "errorcode": 153,
            "errorinfo": "Read timed out. (read timeout={})".format(self.timeout)
        }
        result = {
            "status": 1,
            "data": data
        }
        return result

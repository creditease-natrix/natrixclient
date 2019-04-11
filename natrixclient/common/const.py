#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging
from enum import Enum


# configuration settings
CONFIG_DIR = "/etc/natrix/"
CONFIG_FILE = "natrix.ini"
CONFIG_PATH = "/etc/natrix/natrix.ini"

# PING
PING_COUNT = 3
# seconds
PING_TIMEOUT = 100
PING_PACKET_SIZE = 55

# HTTP
# seconds
HTTP_ALLOW_REDIRECTS = True
HTTP_MAX_REDIRECTS = 30
HTTP_AUTH_TYPE = "basic"
# 整个请求的超时时间 3 分钟
HTTP_TIMEOUT = 180
# HTTP 默认连接超时 1 分钟
HTTP_CONNECT_TIMEOUT = 60
# 设置保存DNS信息的时间，默认 10 分钟
HTTP_DNS_CACHE_TIMEOUT = 600
HTTP_USER_AGENT = "Mozilla/5.2 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50324)"
# 缺省是0, 代表可以使用老的连接
HTTP_FRESH_CONNECT = True
HTTP_SAVE_RESPONSE_HEADER = False
HTTP_SAVE_RESPONSE_BODY = False

TRACEROUTE_ICMP = True
TRACEROUTE_TCP = False
TRACEROUTE_UDP = False
TRACEROUTE_MAX_HOPS = 60

DNS_METHOD = "a"
DNS_TIMEOUT = 60

# crontab
CRONTAB_BASIC_MINUTES = 1
CRONTAB_BASIC_COMMAND = "sudo natrix report basic >> /var/log/natrix/natrixclient_crontab_basic.log 2>&1"
CRONTAB_BASIC_COMMENT = "natrix basic keep alive crontab, added by natrixclient"
CRONTAB_ADVANCE_MINUTES = 30
CRONTAB_ADVANCE_COMMAND = "sudo natrix report advance >> /var/log/natrix/natrixclient_crontab_advance.log 2>&1"
CRONTAB_ADVANCE_COMMENT = "natrix advanced keep alive crontab, added by natrixclient"
CRONTAB_REBOOT_HOURS = 1
CRONTAB_REBOOT_MINUTES = 30
CRONTAB_REBOOT_COMMAND = "sudo reboot"
CRONTAB_REBOOT_COMMENT = "natrix terminal reboot crontab, added by natrixclient"

# rabbitmq queue
QUEUE_KEEP_ALIVE_PREFIX = "keep_alive_"
QUEUE_KEEP_ALIVE_BASIC = "keep_alive_basic"
QUEUE_KEEP_ALIVE_ADVANCE = "keep_alive_advance"
QUEUE_COMMAND_PREFIX = "natrix_request_"

# rabbitmq routing
ROUTING_KEEP_ALIVE_PREFIX = "keep_alive_"
ROUTING_KEEP_ALIVE_BASIC = "keep_alive_basic"
ROUTING_KEEP_ALIVE_ADVANCE = "keep_alive_advance"

# rabbitmq exchange
EXCHANGE_COMMAND_DEAD = 'natrix_command_dlx'

REQUEST_STORAGE_QUEUE_NAME = "natrix_dial_response"
REQUEST_STORAGE_ROUTING_KEY = "natrix_dial_response"

# logging
LOGGING_PATH = "/var/log/natrix/"
FILE_LOGGING_FORMAT = "%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s"
FILE_LOGGING_DATE_FORMAT = "%Y/%m/%d %H:%M:%S"
FILE_MODE = 'a'
# 10MB=10485760
FILE_MAX_BYTES = 10485760
FILE_BACKUP_COUNTS = 10
FILE_ENCODING = None
THREAD_LOGGING_FORMAT = "%(asctime)s %(pathname)s[line:%(lineno)d] %(process)s:%(thread)s %(levelname)s %(message)s"
CONSOLE_LOGGING_FORMAT = "%(message)s"
# 通过命令行输出的log level
CONSOLE_LEVEL = logging.DEBUG
CONSOLE_FILE_LEVEL = logging.DEBUG
CONSOLE_STREAM_LEVEL = logging.INFO
# api log level
API_LEVEL = logging.DEBUG
API_FILE_LEVEL = logging.DEBUG
API_STREAM_LEVEL = logging.INFO
# rabbitmq log level
RABBITMQ_LEVEL = logging.DEBUG
RABBITMQ_FILE_LEVEL = logging.DEBUG
RABBITMQ_STREAM_LEVEL = logging.INFO


class Command(Enum):
    PING = "ping"
    TRACEROUTE = "traceroute"
    DNS = "dns"
    HTTP = "http"
    PERFORMANCE = "performance"
    CHECK = "check"


class StorageMode(Enum):
    RABBITMQ = "rabbitmq"
    CONSOLE = "console"
    RESTFUL = "restful"
    FILE = "file"


class TracerouteProtocol(Enum):
    ICMP = "icmp"
    TCP = "tcp"
    UDP = "udp"


class DnsMethod(Enum):
    A = "a"
    CNAME = "cname"
    MX = "mx"
    NS = "ns"


class HttpOperation(Enum):
    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"


class AuthType(Enum):
    BASIC = "basic"
    DIGEST = "digest"

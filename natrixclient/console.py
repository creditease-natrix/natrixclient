#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import os
import sys
import shutil
import subprocess
import time
from crontab import CronTab
from logging.handlers import RotatingFileHandler
from natrixclient.common import const
from natrixclient.common.const import CONSOLE_LEVEL
from natrixclient.common.const import CONSOLE_FILE_LEVEL
from natrixclient.common.const import CONSOLE_STREAM_LEVEL
from natrixclient.common.const import FILE_MAX_BYTES
from natrixclient.common.const import FILE_BACKUP_COUNTS
from natrixclient.common.const import StorageMode
from natrixclient.common.const import TracerouteProtocol
from natrixclient.common.const import HttpOperation
from natrixclient.command.nping import execute as ping_execute
from natrixclient.command.ntraceroute import execute as traceroute_execute
from natrixclient.command.ndns import execute as dns_execute
from natrixclient.command.ncheck import execute as check_execute
from natrixclient.command.nreport import execute as report_execute
from natrixclient.command.nhttp import execute as http_execute


ln = "natrixclient_console"
logger = logging.getLogger(ln)
logger.setLevel(CONSOLE_LEVEL)

# create log path first
if not os.path.exists(const.LOGGING_PATH):
    os.makedirs(const.LOGGING_PATH)

# create file handler which logs even debug messages
fn = const.LOGGING_PATH + ln + '.log'
fh = RotatingFileHandler(filename=fn, maxBytes=FILE_MAX_BYTES, backupCount=FILE_BACKUP_COUNTS)
fh.setLevel(CONSOLE_FILE_LEVEL)
fh_fmt = logging.Formatter(fmt=const.FILE_LOGGING_FORMAT, datefmt=const.FILE_LOGGING_DATE_FORMAT)
fh.setFormatter(fh_fmt)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(CONSOLE_STREAM_LEVEL)
# create formatter and add it to the handlers
ch_fmt = logging.Formatter(fmt=const.CONSOLE_LOGGING_FORMAT)
ch.setFormatter(ch_fmt)

# add the handlers to logger
logger.addHandler(ch)
logger.addHandler(fh)


epilog = """
Natrix Command Line Interface.  
Natrix - An Open Source Cloud Automation Testing Project.
"""
parser = argparse.ArgumentParser(prog="natrix", epilog=epilog, description="Natrix Command Line Interface")
# subcommand
subparsers = parser.add_subparsers(title="Natrix Sub Commands",
                                   description="natrix sub commands.",
                                   help='help information about the natrix sub commands')


def parse_ping(args):
    # need sudo
    if os.geteuid():
        logger.error("ERROR: natrix ping need root authorization, please use sudo")
        exit()
    destination = args.destination
    request_parameters = dict()
    if args.interface:
        request_parameters["interface"] = args.interface
    request_parameters["count"] = args.count
    request_parameters["timeout"] = args.timeout
    # terminal_request_receive_time
    request_parameters["terminal_request_receive_time"] = time.time()
    request_parameters["logger"] = ln
    response_parameters = dict()
    response_parameters["storage_type"] = StorageMode.CONSOLE
    response_parameters["logger"] = ln
    ping_execute(destination, request_parameters, response_parameters)


# subcommand - ping
def console_ping():
    parser_ping = subparsers.add_parser('ping',
                                        help='natrix sub command - ping.')
    parser_ping.add_argument('destination',
                             help="natrix ping command destination, url or ip.")
    parser_ping.add_argument("-i",
                             "--interface",
                             dest="interface",
                             type=str,
                             help="interface  is  either  an address, or an interface name.  "
                                  "If interface is an address, it sets source address to specified interface address.  "
                                  "If interface in an interface name, it sets source interface to specified interface.")
    parser_ping.add_argument("-c",
                             "--count",
                             dest="count",
                             type=int,
                             default=const.PING_COUNT,
                             help="Stop after sending count ECHO_REQUEST packets. default {}".format(str(const.PING_COUNT)))
    parser_ping.add_argument("-t",
                             "--timeout",
                             dest="timeout",
                             type=int,
                             default=const.PING_TIMEOUT,
                             help="Time to wait for a response, in seconds. default {}".format(str(const.PING_TIMEOUT)))
    # config-file
    # parser_ping.add_argument("-f",
    #                          "--config-file",
    #                          dest="config_file",
    #                          type=str,
    #                          help="the configuration file name, recommend /etc/natrix/natrix.ini .")

    parser_ping.add_argument("-s",
                             "--size",
                             dest="packet_size",
                             type=int,
                             help="Specify the size of the sending packet for Ping")

    parser_ping.set_defaults(func=parse_ping)


def parse_http_request_parameters(args):
    parameters = dict()
    if args.interface:
        parameters["interface"] = args.interface
    parameters["allow_redirects"] = args.allow_redirects
    parameters["max_redirects"] = args.max_redirects
    if args.auth_type:
        parameters["auth_type"] = args.auth_type
    if args.auth_user:
        parameters["auth_user"] = args.auth_user
        auths = args.auth_user.split(":")
        if len(auths) != 2:
            logger.error("Error: auth_user format should be like username:password")
            exit(0)
    parameters["timeout"] = args.timeout
    parameters["connect_timeout"] = args.connect_timeout
    # parameters["request_timeout"] = args.request_timeout
    parameters["dns_cache_timeout"] = args.dns_cache_timeout
    parameters["fresh_connect"] = args.fresh_connect
    if args.http_header:
        parameters["http_header"] = args.http_header
    if args.http_body:
        parameters["http_body"] = args.http_body
    parameters["save_response_header"] = args.save_response_header
    parameters["save_response_body"] = args.save_response_body
    parameters["terminal_request_receive_time"] = time.time()
    # logger
    parameters["logger"] = ln
    return parameters


def parse_http_response_parameters():
    parameters = dict()
    parameters["storage_type"] = StorageMode.CONSOLE
    # logger
    parameters["logger"] = ln
    return parameters


def parse_http_get(args):
    destination = args.destination
    http_execute(HttpOperation.GET, destination, parse_http_request_parameters(args),
                 parse_http_response_parameters())


def parse_http_post(args):
    destination = args.destination
    http_execute(HttpOperation.POST, destination, parse_http_request_parameters(args),
                 parse_http_response_parameters())


def parse_http_put(args):
    destination = args.destination
    http_execute(HttpOperation.PUT, destination, parse_http_request_parameters(args),
                 parse_http_response_parameters())


def parse_http_delete(args):
    destination = args.destination
    http_execute(HttpOperation.DELETE, destination, parse_http_request_parameters(args),
                 parse_http_response_parameters())


# subcommand - HTTP
def console_http():
    parser_http = subparsers.add_parser("http",
                                        help='natrix sub command - http. such as GET, POST, PUT, DELETE ans so on')
    # sub commands
    httpsubparsers = parser_http.add_subparsers(title="Natrix HTTP Sub Commands",
                                                description="Natrix HTTP Sub Commands.",
                                                help='Help Information About the Natrix HTTP sub commands')
    # sub command - GET
    parser_http_get = httpsubparsers.add_parser('get',
                                                help='Natrix HTTP Sub Command - GET.')
    parser_http_get.set_defaults(func=parse_http_get)
    # sub command - POST
    parser_http_post = httpsubparsers.add_parser('post',
                                                 help='Natrix HTTP Sub Command - POST.')
    parser_http_post.set_defaults(func=parse_http_post)
    # sub command - PUT
    parser_http_put = httpsubparsers.add_parser('put',
                                                help='Natrix HTTP Sub Command - PUT.')
    parser_http_put.set_defaults(func=parse_http_put)
    # sub command - DELETE
    parser_http_delete = httpsubparsers.add_parser('delete',
                                                   help='Natrix HTTP Sub Command - DELETE.')
    parser_http_delete.set_defaults(func=parse_http_delete)
    # common arguments
    parser_http.add_argument('destination',
                             help="natrix http command destination, url or ip.")
    # HTTP版本
    # parser_http.add_argument("--http-version",
    #                          help="HTTP version, support 1.0 / 1.1 / 2.0")
    # 接口
    parser_http.add_argument("-i",
                             "--interface",
                             help="user can use dedicated network interface.")
    # 重定向
    # --allow_redirects -R
    parser_http.add_argument("--allow-redirects",
                             dest="allow_redirects",
                             # type=bool,
                             action="store_true",
                             default=const.HTTP_ALLOW_REDIRECTS,
                             help="Allow Redirects, Default is {}.".format(const.HTTP_ALLOW_REDIRECTS))
    # 最大重定向数
    # --max_redirects -r
    parser_http.add_argument("--max-redirects",
                             dest="max_redirects",
                             type=int,
                             default=const.HTTP_MAX_REDIRECTS,
                             help="Set Max Redirects. Default is {}.".format(str(const.HTTP_MAX_REDIRECTS)))
    # 安全验证
    # --authentication-type -a
    parser_http.add_argument("-a",
                             "--auth-type",
                             dest="auth_type",
                             default=const.HTTP_AUTH_TYPE,
                             help="Authentication Type. support basic")
    # 安全验证
    # --authentication-content -c
    parser_http.add_argument("-u",
                             "--auth-user",
                             dest="auth_user",
                             help="Specify the user name and password to use for server authentication, "
                                  "for basic_auth, like guest:guest")
    # 超时时间
    parser_http.add_argument("-t",
                             "--timeout",
                             dest="timeout",
                             default=const.HTTP_TIMEOUT,
                             help="Set an expiration time.")
    # 连接超时时间
    parser_http.add_argument("--connect-timeout",
                             dest="connect_timeout",
                             default=const.HTTP_CONNECT_TIMEOUT,
                             help="HTTP connect timeout, HTTP连接超时. "
                                  "default is {} seconds".format(str(const.HTTP_CONNECT_TIMEOUT)))
    # 请求超时时间
    # parser_http.add_argument("--request-timeout",
    #                          dest="request_timeout",
    #                          default=const.HTTP_REQUEST_TIMEOUT,
    #                          help="HTTP request timeout, HTTP请求超时. "
    #                               "default is {} seconds".format(str(const.HTTP_REQUEST_TIMEOUT)))

    # DNS信息保存时间
    parser_http.add_argument("--dns-cache-timeout",
                             dest="dns_cache_timeout",
                             default=const.HTTP_DNS_CACHE_TIMEOUT,
                             help="DNS information timeout, DNS信息保存时间. "
                                  "default is {} seconds".format(str(const.HTTP_DNS_CACHE_TIMEOUT)))
    # 强制获取新连接
    parser_http.add_argument("--fresh-connect",
                             dest="fresh_connect",
                             action="store_true",
                             default=const.HTTP_FRESH_CONNECT,
                             help="Force to set new HTTP connection, 强制获取新连接. "
                                  "default is {}".format(str(const.HTTP_FRESH_CONNECT)))
    # 头部信息
    parser_http.add_argument("-H",
                             "--http-header",
                             dest="http_header",
                             help="Custom HTTP Headers.")
    # BODY信息
    parser_http.add_argument("-D",
                             "--http-body",
                             dest="http_body",
                             help="Custom HTTP Body.")
    # 保存response头部信息
    parser_http.add_argument("--save-response-header",
                             dest="save_response_header",
                             # type=bool,
                             action="store_true",
                             default=const.HTTP_SAVE_RESPONSE_HEADER,
                             help="Save Response Header Information in Return Result.")
    # 保存response body 信息
    parser_http.add_argument("--save-response-body",
                             dest="save_response_body",
                             # type=bool,
                             action="store_true",
                             default=const.HTTP_SAVE_RESPONSE_BODY,
                             help="Save Response Body Information in Return Result.")


def parse_performance(args):
    logger.info("==========PERFORMANCE==========")
    logger.debug(args)


# subcommand - performance
def console_performance():
    parser_perf = subparsers.add_parser(
        "performance",
        help='natrix sub command - performance.'
    )
    parser_perf.add_argument(
        "-b",
        "--browser",
        choices=["firefox", "chrome", "curl"],
        help="Select a browser that you want to use to execute instructions."
    )
    parser_perf.add_argument(
        "-m",
        "--mode",
        choices=["time", "resource", "data"],
        help="Specify the instructions you want to execute. for \"time\", \
        get the page query time data; for \"resource\", get all resources data loaded by the page; for \"data\", \
        simultaneously obtain the above two kinds of data."
    )
    parser_perf.add_argument('destination',
                        help="nantrix performance command destination, url or ip.")
    parser_perf.set_defaults(func=parse_performance)


def parse_traceroute(args):
    destination = args.destination
    request_parameters = dict()
    if args.traceroute_interface:
        request_parameters["interface"] = args.traceroute_interface
    if args.traceroute_icmp:
        request_parameters["protocol"] = TracerouteProtocol.ICMP
    elif args.traceroute_tcp:
        request_parameters["protocol"] = TracerouteProtocol.ICMP
    elif args.traceroute_udp:
        request_parameters["protocol"] = TracerouteProtocol.ICMP
    else:
        logger.error("ERROR: traceroute just support protocol icmp/udp/tcp")
        exit(1)
    if args.traceroute_max_hops:
        request_parameters["max_hops"] = args.traceroute_max_hops
    # terminal_request_receive_time
    request_parameters["terminal_request_receive_time"] = time.time()
    # request logger
    request_parameters["logger"] = ln
    response_parameters = dict()
    response_parameters["storage_type"] = StorageMode.CONSOLE
    # response logger
    response_parameters["logger"] = ln
    traceroute_execute(destination, request_parameters, response_parameters)


# subcommand - traceroute
def console_traceroute():
    parser_traceroute = subparsers.add_parser('traceroute',
                                              help='Natrix sub command - traceroute.')
    group_traceroute = parser_traceroute.add_mutually_exclusive_group()
    group_traceroute.add_argument("-I",
                                  "--icmp",
                                  dest="traceroute_icmp",
                                  # type=bool,
                                  default=const.TRACEROUTE_ICMP,
                                  action="store_true",
                                  help="Default: Use ICMP ECHO for probes.")
    group_traceroute.add_argument("-T",
                                  "--tcp",
                                  dest="traceroute_tcp",
                                  # type=bool,
                                  default=const.TRACEROUTE_TCP,
                                  action="store_true",
                                  help="Use TCP SYN for probes")
    group_traceroute.add_argument("-U",
                                  "--udp",
                                  dest="traceroute_udp",
                                  # type=bool,
                                  default=const.TRACEROUTE_ICMP,
                                  action="store_true",
                                  help="Use UDP to particular destination port for \
                                  tracerouting (instead of increasing the port per each probe).\
                                  Default port is 53 (dns).")
    parser_traceroute.add_argument("-i",
                                   "--interface",
                                   dest="traceroute_interface",
                                   help="Specify a network interface to operate with.")
    parser_traceroute.add_argument("-m",
                                   "--max-hops",
                                   dest="traceroute_max_hops",
                                   type=int,
                                   default=const.TRACEROUTE_MAX_HOPS,
                                   help="Specifies the maximum number of hops traceroute will probe. "
                                        "The default is {}.".format(str(const.TRACEROUTE_MAX_HOPS)))
    parser_traceroute.add_argument('destination',
                                   help="Natrix traceroute command destination, URL or IP.")
    parser_traceroute.set_defaults(func=parse_traceroute)


def parse_dns(args):
    destination = args.destination
    request_parameters = dict()
    request_parameters["dns_server"] = args.dns_server
    request_parameters["dns_method"] = args.dns_method
    request_parameters["dns_timeout"] = args.dns_timeout
    request_parameters["terminal_request_receive_time"] = time.time()
    request_parameters["logger"] = ln
    response_parameters = dict()
    response_parameters["storage_type"] = StorageMode.CONSOLE
    response_parameters["logger"] = ln
    dns_execute(destination, request_parameters, response_parameters)


# subcommand - dns
def console_dns():
    parser_dns = subparsers.add_parser('dns',
                                       help='Natrix sub command - dns.')
    parser_dns.add_argument("-s",
                            "--server",
                            dest="dns_server",
                            help="Specify a DNS server.")
    parser_dns.add_argument("-m",
                            "--method",
                            choices=["A", "NS", "MX", "CNAME"],
                            dest="dns_method",
                            default=const.DNS_METHOD,
                            help="Change the type of the information query. default is {}.".format(const.DNS_METHOD))
    parser_dns.add_argument("-t",
                            "--timeout",
                            dest="dns_timeout",
                            type=int,
                            default=const.DNS_TIMEOUT,
                            help="Set parsing timeout for dns. default is {}".format(str(const.HTTP_DNS_CACHE_TIMEOUT)))
    parser_dns.add_argument('destination',
                            help="Natrix dns command destination, URL or IP.")
    parser_dns.set_defaults(func=parse_dns)


def parse_check_basic(args):
    request_parameters = {"type": "basic",
                          "logger": ln}
    response_parameters = {"storage_type": StorageMode.CONSOLE,
                           "logger": ln}
    check_execute(request_parameters=request_parameters,
                  response_parameters=response_parameters)


def parse_check_advance(args):
    request_parameters = {"type": "advance",
                          "logger": ln}
    response_parameters = {"storage_type": StorageMode.CONSOLE,
                           "logger": ln}
    check_execute(request_parameters=request_parameters,
                  response_parameters=response_parameters)


def parse_check_hardware(args):
    request_parameters = {"type": "hardware",
                          "logger": ln}
    response_parameters = {"storage_type": StorageMode.CONSOLE,
                           "logger": ln}
    check_execute(request_parameters=request_parameters,
                  response_parameters=response_parameters)


def parse_check_system(args):
    request_parameters = {"type": "system",
                          "logger": ln}
    response_parameters = {"storage_type": StorageMode.CONSOLE,
                           "logger": ln}
    check_execute(request_parameters=request_parameters,
                  response_parameters=response_parameters)


def parse_check_network(args):
    request_parameters = {"type": "network",
                          "logger": ln}
    response_parameters = {"storage_type": StorageMode.CONSOLE,
                           "logger": ln}
    check_execute(request_parameters=request_parameters,
                  response_parameters=response_parameters)


# subcommand - check
def console_check():
    parser_check = subparsers.add_parser(
        "check",
        help="natrix sub command - check. check the information such as system, hardware and so on..."
    )
    # 创建子命令项
    checksubparsers = parser_check.add_subparsers(title="Natrix Check Sub Commands",
                                                  description="natrix check sub commands.",
                                                  help='help information about the natrix check sub commands')
    # parser_check.set_defaults(func=parse_check)
    # 创建具体的子命令
    parser_check_basic = checksubparsers.add_parser('basic',
                                                    help='natrix check sub command - basic.')
    parser_check_basic.set_defaults(func=parse_check_basic)
    parser_check_advance = checksubparsers.add_parser('advance',
                                                      help='natrix check sub command - advance.')
    parser_check_advance.set_defaults(func=parse_check_advance)
    parser_check_system = checksubparsers.add_parser('system',
                                                     help='natrix check sub command - system.')
    parser_check_system.set_defaults(func=parse_check_system)
    parser_check_hardware = checksubparsers.add_parser('hardware',
                                                       help='natrix check sub command - hardware.')
    parser_check_hardware.set_defaults(func=parse_check_hardware)
    parser_check_network = checksubparsers.add_parser('network',
                                                      help='natrix check sub command - network.')
    parser_check_network.set_defaults(func=parse_check_network)


def parse_report_basic(args):
    request_parameters = {"type": "basic",
                          "logger": ln}
    response_parameters = dict()
    response_parameters["storage_type"] = StorageMode.RABBITMQ
    response_parameters["storage_queue"] = const.QUEUE_KEEP_ALIVE_BASIC
    response_parameters["storage_routing"] = const.ROUTING_KEEP_ALIVE_BASIC
    response_parameters["logger"] = ln
    report_execute(request_parameters=request_parameters,
                   response_parameters=response_parameters)


def parse_report_advance(args):
    request_parameters = {"type": "advance",
                          "logger": ln}
    response_parameters = dict()
    response_parameters["storage_type"] = StorageMode.RABBITMQ
    response_parameters["storage_queue"] = const.QUEUE_KEEP_ALIVE_ADVANCE
    response_parameters["storage_routing"] = const.ROUTING_KEEP_ALIVE_ADVANCE
    response_parameters["logger"] = ln
    report_execute(request_parameters=request_parameters,
                   response_parameters=response_parameters)


# subcommand - report
def console_report():
    parser_report = subparsers.add_parser("report",
                                          help="Natrix Sub Command - Report. report information to AMQP server")
    # 创建子命令项
    report_subparsers = parser_report.add_subparsers(title="Natrix Report Sub Command",
                                                     help='help information about the report sub command')
    # 创建具体的子命令
    parser_report_basic = report_subparsers.add_parser('basic',
                                                       help='natrix report sub command - basic.')
    parser_report_basic.set_defaults(func=parse_report_basic)
    parser_report_advance = report_subparsers.add_parser('advance',
                                                         help='natrix report sub command - advance.')
    parser_report_advance.set_defaults(func=parse_report_advance)
    # config-file
    # parser_report.add_argument("-f",
    #                            "--config-file",
    #                            dest="config_file",
    #                            type=str,
    #                            default=const.CONFIG_PATH,
    #                            help="the configuration file name, default {} .".format(const.CONFIG_PATH))


def parse_crontab_basic(args):
    basic_minutes = args.minutes
    create_crontab_basic(basic_minutes)


def create_crontab_basic(basic_minutes):
    basic_cron = CronTab(user=True)
    basic_command = const.CRONTAB_BASIC_COMMAND
    basic_comment = const.CRONTAB_BASIC_COMMENT
    # need to find command first
    basic_iter = basic_cron.find_command(basic_command)
    # if exist, remove first
    for basic_exist_job in basic_iter:
        basic_cron.remove(basic_exist_job)
    basic_job = basic_cron.new(command=basic_command, comment=basic_comment)
    basic_job.minute.every(basic_minutes)
    logger.info("add natrix basic keep alive crontab successfully, please use \"crontab -l\" to check")
    basic_job.enable()
    basic_cron.write()


def parse_crontab_advance(args):
    advance_minutes = args.minutes
    create_crontab_advance(advance_minutes)


def create_crontab_advance(advance_minutes):
    advance_cron = CronTab(user=True)
    advance_command = const.CRONTAB_ADVANCE_COMMAND
    advance_comment = const.CRONTAB_ADVANCE_COMMENT
    # need to find command first
    advance_iter = advance_cron.find_command(advance_command)
    # if exist, remove first
    for advance_exist_job in advance_iter:
        advance_cron.remove(advance_exist_job)
    advance_job = advance_cron.new(command=advance_command, comment=advance_comment)
    advance_job.minute.every(advance_minutes)
    logger.info("add natrix advance keep alive crontab successfully, please use \"crontab -l\" to check")
    advance_job.enable()
    advance_cron.write()


def parse_crontab_reboot(args):
    reboot_hours = args.hours
    reboot_minutes = args.minutes
    create_crontab_reboot(reboot_hours, reboot_minutes)


def create_crontab_reboot(reboot_hours, reboot_minutes):
    reboot_cron = CronTab(user=True)
    reboot_command = const.CRONTAB_REBOOT_COMMAND
    reboot_comment = const.CRONTAB_REBOOT_COMMENT
    # need to find comment first
    reboot_iter = reboot_cron.find_comment(reboot_comment)
    # if exist, remove first
    for reboot_exist_job in reboot_iter:
        reboot_cron.remove(reboot_exist_job)
    reboot_job = reboot_cron.new(command=reboot_command, comment=reboot_comment)
    reboot_job.hour.on(reboot_hours)
    reboot_job.minute.on(reboot_minutes)
    logger.info("add natrix reboot crontab successfully, please use \"crontab -l\" to check")
    reboot_job.enable()
    reboot_cron.write()


def parse_crontab_all(args):
    # basic
    basic_minutes = const.CRONTAB_BASIC_MINUTES
    create_crontab_basic(basic_minutes)
    # advanced
    advance_minutes = const.CRONTAB_ADVANCE_MINUTES
    create_crontab_advance(advance_minutes)
    # reboot
    reboot_hours = const.CRONTAB_REBOOT_HOURS
    reboot_minutes = const.CRONTAB_REBOOT_MINUTES
    create_crontab_reboot(reboot_hours, reboot_minutes)


def parse_crontab_clean(args):
    clean_cron = CronTab(user=True)
    # basic
    basic_command = const.CRONTAB_BASIC_COMMAND
    basic_iter = clean_cron.find_command(basic_command)
    for basic_exist_job in basic_iter:
        clean_cron.remove(basic_exist_job)
    # advance
    advance_command = const.CRONTAB_ADVANCE_COMMAND
    advance_iter = clean_cron.find_command(advance_command)
    for advance_exist_job in advance_iter:
        clean_cron.remove(advance_exist_job)
    # reboot
    reboot_comment = const.CRONTAB_REBOOT_COMMENT
    reboot_iter = clean_cron.find_comment(reboot_comment)
    for reboot_exist_job in reboot_iter:
        clean_cron.remove(reboot_exist_job)
    logger.info("clean natrix crontab successfully, please use \"crontab -l\" to check")
    clean_cron.write()


# subcommand - crontab
def console_crontab():
    parser_crontab = subparsers.add_parser("crontab",
                                           help="Natrix Sub Command - crontab. "
                                                "set crontab job for keepalive information to AMQP server")
    # 创建子命令项
    crontab_subparsers = parser_crontab.add_subparsers(title="Natrix crontab Sub Command",
                                                       help='help information about the crontab sub command')
    # 创建具体的子命令
    # basic
    parser_crontab_basic = crontab_subparsers.add_parser('basic',
                                                         help='natrix crontab sub command - basic.')
    parser_crontab_basic.add_argument("minutes",
                                      type=int,
                                      default=const.CRONTAB_BASIC_MINUTES,
                                      help="The periodic number to report basic information to natrix server, "
                                           "default is {} minutes".format(str(const.CRONTAB_BASIC_MINUTES)))
    parser_crontab_basic.set_defaults(func=parse_crontab_basic)
    # advance
    parser_crontab_advance = crontab_subparsers.add_parser('advance',
                                                           help='natrix crontab sub command - advance.')
    parser_crontab_advance.add_argument("minutes",
                                        type=int,
                                        default=const.CRONTAB_ADVANCE_MINUTES,
                                        help="The periodic number to report advanced information to natrix server, "
                                             "default is {} minutes".format(str(const.CRONTAB_ADVANCE_MINUTES)))
    parser_crontab_advance.set_defaults(func=parse_crontab_advance)
    # reboot
    parser_crontab_reboot = crontab_subparsers.add_parser('reboot',
                                                          help='natrix crontab sub command - reboot.')
    parser_crontab_reboot.add_argument("hours",
                                       type=int,
                                       default=const.CRONTAB_REBOOT_HOURS,
                                       help="The reboot time for every day, "
                                            "if hours=7, minutes=30, "
                                            "means terminal reboot at 7:30 in the morning everyday"
                                            "default is {}:{}"
                                       .format(str(const.CRONTAB_REBOOT_HOURS), const.CRONTAB_REBOOT_MINUTES))
    parser_crontab_reboot.add_argument("minutes",
                                       type=int,
                                       default=const.CRONTAB_REBOOT_MINUTES,
                                       help="The reboot time for every day, "
                                            "if hours=7, minutes=30, "
                                            "means terminal reboot at 7:30 in the morning everyday"
                                            "default is {}:{}"
                                       .format(str(const.CRONTAB_REBOOT_HOURS), const.CRONTAB_REBOOT_MINUTES))
    parser_crontab_reboot.set_defaults(func=parse_crontab_reboot)
    # all
    # including basic/advance/reboot with default value
    crontab_all_help = "Natrix crontab sub command - all.\n " \
                       "Natrix will set basic report to every {} minutes\n" \
                       "Natrix will set advance report to every {} minutes\n" \
                       "Natrix will reboot terminal in every day at {}:{}\n"\
        .format(const.CRONTAB_BASIC_MINUTES, const.CRONTAB_ADVANCE_MINUTES,
                const.CRONTAB_REBOOT_HOURS, const.CRONTAB_REBOOT_MINUTES)
    parser_crontab_all = crontab_subparsers.add_parser('all',
                                                       help=crontab_all_help)
    parser_crontab_all.set_defaults(func=parse_crontab_all)
    # clean
    parser_crontab_clean = crontab_subparsers.add_parser('clean',
                                                         help="clean all natrix crontab")
    parser_crontab_clean.set_defaults(func=parse_crontab_clean)


def parse_service_init(args):
    logger.info("================================================================================================")
    logger.info("initializing natrix client services ......")
    # 提升到root权限
    if os.geteuid():
        logger.error("must be root or have sudo authorization")
        exit(101)
    else:
        # create configuration directory /etc/natrix/
        conf_dir = const.CONFIG_DIR
        logger.info("\n1. creating configuration directory {} ......".format(conf_dir))
        if os.path.isdir(conf_dir):
            logger.info("configuration directory {} exist".format(conf_dir))
        else:
            logger.info("creating configuration directory {}".format(conf_dir))
            os.makedirs(conf_dir)

        # copy configuration files to /etc/natrix
        logger.info("")
        logger.info("\n2. copying sample configuration files to {}......".format(conf_dir))
        sample_dir = os.path.dirname(os.path.realpath(__file__)) + "/conf/etc/natrix/"
        for sample_file in os.listdir(sample_dir):
            conf_path = conf_dir + sample_file
            if os.path.isfile(conf_path):
                logger.info("configuration file {} already exists in {}".format(sample_file, conf_dir))
                bak_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
                bak_conf_path = conf_path + "." + str(bak_time)
                logger.info("backup original configuration file from {} to {}".format(conf_path, bak_conf_path))
                os.rename(conf_path, bak_conf_path)
            sample_path = sample_dir + sample_file
            logger.info("copying configuration sample file from {} to {} ......".format(sample_path, conf_path))
            shutil.copyfile(sample_path, conf_path)

        # create log directory /var/log/natrix
        log_dir = "/var/log/natrix/"
        logger.info("\n3. creating log directory {} ......".format(log_dir))
        if os.path.isdir(log_dir):
            logger.info("log directory {} exist".format(log_dir))
        else:
            logger.info("creating log directory {}".format(log_dir))
            os.makedirs(log_dir)

        # creating systemctl service
        systemd_dir = "/etc/systemd/system/"
        logger.debug("\n4. copying sample systemd files to {}".format(systemd_dir))
        sample_systemd_dir = os.path.dirname(os.path.realpath(__file__)) + "/conf/etc/systemd/system/"
        for sample_systemd_file in os.listdir(sample_systemd_dir):
            systemd_path = systemd_dir + sample_systemd_file
            if os.path.isfile(systemd_path):
                logger.info("systemd file {} already exists in {}".format(sample_systemd_file, systemd_dir))
                bak_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
                bak_systemd_path = systemd_path + "." + str(bak_time)
                logger.info("backup original systemd file from {} to {}".format(systemd_path, bak_systemd_path))
                os.rename(systemd_path, bak_systemd_path)
            sample_systemd_path = sample_systemd_dir + sample_systemd_file
            logger.info("copying systemd sample file from {} to {} ......".format(sample_systemd_path, systemd_path))
            shutil.copyfile(sample_systemd_path, systemd_path)

        # run 'systemctl daemon-reload' to reload units
        logger.debug("\n5. reloading systemd daemon service")
        # must add shell=True
        daemon_reload_command = "systemctl daemon-reload"
        daemon_reload_process = subprocess.Popen(daemon_reload_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        # communicate() returns a tuple (stdout, stderr)
        daemon_reload_result = daemon_reload_process.communicate()
        logger.debug("daemon reload command \"{}\" result: {}".format(daemon_reload_command, daemon_reload_result))

    logger.info("\nsuccessfully initialized natrix client services")
    logger.info("================================================================================================")


def parse_service_start(args):
    logger.info("================================================================================================")
    logger.info("starting natrix client services ......")
    # systemd service files
    logger.info("\n1. checking systemd service files ......")
    systemd_paths = ["/etc/systemd/system/natrixclient.service"]
    for systemd_path in systemd_paths:
        logger.info("checking systemd file {}".format(systemd_path))
        if os.path.isfile(systemd_path):
            logger.debug("systemd file {} exist".format(systemd_path))
        else:
            logger.error("systemd file {} not exist, please execute \"natrix service init\" first!!!")
            exit(201)
    # systemd daemon files
    logger.info("\n2. checking systemd daemon files ......")
    daemon_paths = ["/etc/natrix/natrixclient.daemon"]
    for daemon_path in daemon_paths:
        logger.info("checking natrixclient daamon service file {}".format(daemon_path))
        if os.path.isfile(daemon_path):
            logger.debug("natrixclient daamon service file {} exist".format(daemon_path))
        else:
            logger.error("natrixclient daamon service file {} not exist, "
                         "please execute \"natrix service init\" first!!!".format(daemon_path))
            exit(202)
    # start systemd service
    logger.info("\n3. starting systemd services ......")
    services = ["natrixclient.service"]
    for service in services:
        logger.debug("starting natrix client service {}".format(service))
        # must add shell=True
        service_start_command = "systemctl start " + service
        service_start_process = subprocess.Popen(service_start_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        # communicate() returns a tuple (stdout, stderr)
        service_start_result = service_start_process.communicate()
        logger.debug("service start command \"{}\" result: {}".format(service_start_command, service_start_result))
    # add crontab job
    # add keep alive basic crontab job
    logger.info("\n4. adding keep alive basic crontab job ......")
    basic_minutes = const.CRONTAB_BASIC_MINUTES
    create_crontab_basic(basic_minutes)
    # add keep alive advance crontab job
    logger.info("\n5. adding keep alive advance crontab job ......")
    advance_minutes = const.CRONTAB_ADVANCE_MINUTES
    create_crontab_advance(advance_minutes)
    # add reboot at midnight crontab job
    logger.info("\n6. adding reboot at midnight crontab job ......")
    reboot_hours = const.CRONTAB_REBOOT_HOURS
    reboot_minutes = const.CRONTAB_REBOOT_MINUTES
    create_crontab_reboot(reboot_hours, reboot_minutes)
    logger.info("\nsuccessfully started natrix client services")
    logger.info("================================================================================================")


def parse_service_stop(args):
    logger.info("================================================================================================")
    logger.info("stopping natrix client services ......")
    # stop service
    # start systemd service
    logger.info("\n1. stopping systemd services ......")
    services = ["natrixclient.service"]
    for service in services:
        logger.debug("stopping natrix client service {}".format(service))
        # must add shell=True
        service_stop_command = "systemctl stop " + service
        service_stop_process = subprocess.Popen(service_stop_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        # communicate() returns a tuple (stdout, stderr)
        service_stop_result = service_stop_process.communicate()
        logger.debug("service start command \"{}\" result: {}".format(service_stop_command, service_stop_result))
    # clean crontab
    logger.info("\n2. clean all natrix clit crontab jobs ......")
    parse_crontab_clean(None)
    logger.info("\nsuccessfully stopped natrix client services")
    logger.info("================================================================================================")


def parse_service_enable(args):
    logger.info("================================================================================================")
    logger.info("enabling natrix client services .....")
    # systemd service files
    logger.info("\n1. checking systemd service files ......")
    systemd_paths = ["/etc/systemd/system/natrixclient.service"]
    for systemd_path in systemd_paths:
        logger.info("checking systemd file {}".format(systemd_path))
        if os.path.isfile(systemd_path):
            logger.debug("systemd file {} exist".format(systemd_path))
        else:
            logger.error("systemd file {} not exist, please execute \"natrix service init\" first!!!")
            exit(401)
    # systemd daemon files
    logger.info("\n2. checking systemd daemon files ......")
    daemon_paths = ["/etc/natrix/natrixclient.daemon"]
    for daemon_path in daemon_paths:
        logger.info("checking natrixclient daamon service file {}".format(daemon_path))
        if os.path.isfile(daemon_path):
            logger.debug("natrixclient daamon service file {} exist".format(daemon_path))
        else:
            logger.error("natrixclient daamon service file {} not exist, "
                         "please execute \"natrix service init\" first!!!".format(daemon_path))
            exit(402)
    # start systemd service
    logger.info("\n3. enabling systemd services ......")
    services = ["natrixclient.service"]
    for service in services:
        logger.debug("enabling natrix client service {}".format(service))
        # must add shell=True
        service_enable_command = "systemctl enable " + service
        service_enable_process = subprocess.Popen(service_enable_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        # communicate() returns a tuple (stdout, stderr)
        service_enable_result = service_enable_process.communicate()
        logger.debug("service enable command \"{}\" result: {}".format(service_enable_command, service_enable_result))
    # add crontab job
    # add keep alive basic crontab job
    logger.info("\n4. adding keep alive basic crontab job ......")
    basic_minutes = const.CRONTAB_BASIC_MINUTES
    create_crontab_basic(basic_minutes)
    # add keep alive advance crontab job
    logger.info("\n5. adding keep alive advance crontab job ......")
    advance_minutes = const.CRONTAB_ADVANCE_MINUTES
    create_crontab_advance(advance_minutes)
    # add reboot at midnight crontab job
    logger.info("\n6. adding reboot at midnight crontab job ......")
    reboot_hours = const.CRONTAB_REBOOT_HOURS
    reboot_minutes = const.CRONTAB_REBOOT_MINUTES
    create_crontab_reboot(reboot_hours, reboot_minutes)

    logger.info("\nsuccessfully enabled natrix client services")
    logger.info("================================================================================================")


def parse_service_disable(args):
    logger.info("================================================================================================")
    logger.info("disabling natrix client services ......")
    # stop service
    # start systemd service
    logger.info("\n1. disabling systemd services ......")
    services = ["natrixclient.service"]
    for service in services:
        logger.debug("disabling natrix client service {}".format(service))
        # must add shell=True
        service_disable_command = "systemctl disable " + service
        service_disable_process = subprocess.Popen(service_disable_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        # communicate() returns a tuple (stdout, stderr)
        service_disable_result = service_disable_process.communicate()
        logger.debug("service disable command \"{}\" result: {}".format(service_disable_command, service_disable_result))
    # clean crontab
    logger.info("\n2. clean all natrix clit crontab jobs ......")
    parse_crontab_clean(None)
    logger.info("\nsuccessfully disabled natrix client services")
    logger.info("================================================================================================")


def parse_service_status(args):
    logger.info("================================================================================================")
    logger.info("checking natrix client services status......")
    # systemd service
    logger.info("\n1. checking systemd services status ......")
    services = ["natrixclient.service"]
    for service in services:
        logger.debug("checking natrix client service {} status".format(service))
        service_status_command = "systemctl status " + service
        service_status_process = subprocess.Popen(service_status_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        service_status_result = service_status_process.communicate()
        # logger.debug("service status command \"{}\" result: {}".format(service_status_command, service_status_result))
        service_status_string = service_status_result[0].decode()
        logger.info(service_status_string)
    # crontab -l
    logger.info("\n2. checking crontab jobs status")
    crontab_status_command = "crontab -l"
    crontab_status_process = subprocess.Popen(crontab_status_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE, shell=True)
    crontab_status_result = crontab_status_process.communicate()
    # logger.debug("crontab status command \"{}\" result: {}".format(crontab_status_command, crontab_status_result))
    crontab_status_string = crontab_status_result[0].decode()
    logger.info(crontab_status_string)
    logger.info("\nsuccessfully checking natrix client status")
    logger.info("================================================================================================")


# subcommand - service
def console_service():
    parser_service = subparsers.add_parser("service",
                                           help="Natrix Sub Command - service. "
                                                "Natrix Client Service Operation: init/start/stop/status")
    # 创建子命令项
    service_subparsers = parser_service.add_subparsers(title="Natrix Client service Sub Command",
                                                       help='help information about the service sub command')
    # 创建具体的子命令
    # init
    parser_service_init = service_subparsers.add_parser('init',
                                                         help='natrix service sub command - init')
    parser_service_init.set_defaults(func=parse_service_init)
    # start
    parser_service_start = service_subparsers.add_parser('start',
                                                         help='natrix service sub command - start.')
    parser_service_start.set_defaults(func=parse_service_start)
    # stop
    parser_service_stop = service_subparsers.add_parser('stop',
                                                        help='natrix service sub command - stop.')
    parser_service_stop.set_defaults(func=parse_service_stop)
    # enable
    parser_service_enable = service_subparsers.add_parser('enable',
                                                          help='natrix service sub command - enable.')
    parser_service_enable.set_defaults(func=parse_service_enable)
    # disable
    parser_service_disable = service_subparsers.add_parser('disable',
                                                           help='natrix service sub command - disable.')
    parser_service_disable.set_defaults(func=parse_service_disable)
    # status
    parser_servuce_status = service_subparsers.add_parser('status',
                                                         help="natrix service sub command - status")
    parser_servuce_status.set_defaults(func=parse_service_status)


def console_common():
    # -d, --debug
    parser.add_argument(
        "-d",
        "--debug",
        dest="debug",
        help="set natrix to debug mode.",
        action="store_true"
    )

    # log-file
    # parser.add_argument("--log-file",
    #                     dest="log_file",
    #                     type=str,
    #                     default="/var/log/natrix/natrix.log",
    #                     help="the log file name, default is /var/log/natrix/natrix.log .")


def main():
    # 调用相关函数
    console_common()
    console_ping()
    console_http()
    # console_performance()
    console_dns()
    console_traceroute()
    console_check()
    console_report()
    # console_contab()
    console_service()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    # 提升到root权限
    if os.geteuid():
        args = [sys.executable] + sys.argv
        os.execlp('sudo', 'sudo', *args)
    main()

# -*- coding: utf-8 -*-
"""

"""
import os, time

from natrixclient.common import const
from natrixclient.command.nping import execute as ping_execute

from natrixclient.bin import logger
from natrixclient.bin import ln


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
    response_parameters["storage_type"] = const.StorageMode.CONSOLE
    response_parameters["logger"] = ln
    ping_execute(destination, request_parameters, response_parameters)


# subcommand - ping
def console_ping(subparsers):
    parser_ping = subparsers.add_parser('ping',
                                        help='Natrix Client Sub Command - ping.')
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

    parser_ping.add_argument("-s",
                             "--size",
                             dest="packet_size",
                             type=int,
                             help="Specify the size of the sending packet for Ping")

    parser_ping.set_defaults(func=parse_ping)


# -*- coding: utf-8 -*-
"""

"""

import time

from natrixclient.common import const
from natrixclient.command.ntraceroute import execute as traceroute_execute

from natrixclient.bin import ln
from natrixclient.bin import logger


def parse_traceroute(args):
    destination = args.destination
    request_parameters = dict()
    if args.traceroute_interface:
        request_parameters["interface"] = args.traceroute_interface
    if args.traceroute_icmp:
        request_parameters["protocol"] = const.TracerouteProtocol.ICMP
    elif args.traceroute_tcp:
        request_parameters["protocol"] = const.TracerouteProtocol.ICMP
    elif args.traceroute_udp:
        request_parameters["protocol"] = const.TracerouteProtocol.ICMP
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
    response_parameters["storage_type"] = const.StorageMode.CONSOLE
    # response logger
    response_parameters["logger"] = ln
    traceroute_execute(destination, request_parameters, response_parameters)


# subcommand - traceroute
def console_traceroute(subparsers):
    parser_traceroute = subparsers.add_parser('traceroute',
                                              help='Natrix Client Sub Command - traceroute.')
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


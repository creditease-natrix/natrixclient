# -*- coding: utf-8 -*-
"""      """

import time

from natrixclient.command.ndns import execute as dns_execute
from natrixclient.common import const

from natrixclient.bin import ln


def parse_dns(args):
    destination = args.destination
    request_parameters = dict()
    request_parameters["dns_server"] = args.dns_server
    request_parameters["dns_method"] = args.dns_method
    request_parameters["dns_timeout"] = args.dns_timeout
    request_parameters["terminal_request_receive_time"] = time.time()
    request_parameters["logger"] = ln
    response_parameters = dict()
    response_parameters["storage_type"] = const.StorageMode.CONSOLE
    response_parameters["logger"] = ln
    dns_execute(destination, request_parameters, response_parameters)


# subcommand - dns
def console_dns(subparsers):
    parser_dns = subparsers.add_parser('dns',
                                       help='Natrix Client Sub Command - dns.')
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


# -*- coding: utf-8 -*-
"""

"""

from natrixclient.common import const
from natrixclient.command.ncheck import execute as check_execute

from natrixclient.bin import ln


def parse_check_basic(args):
    request_parameters = {"type": "basic",
                          "logger": ln}
    response_parameters = {"storage_type": const.StorageMode.CONSOLE,
                           "logger": ln}
    check_execute(request_parameters=request_parameters,
                  response_parameters=response_parameters)


def parse_check_advance(args):
    request_parameters = {"type": "advance",
                          "logger": ln}
    response_parameters = {"storage_type": const.StorageMode.CONSOLE,
                           "logger": ln}
    check_execute(request_parameters=request_parameters,
                  response_parameters=response_parameters)


def parse_check_hardware(args):
    request_parameters = {"type": "hardware",
                          "logger": ln}
    response_parameters = {"storage_type": const.StorageMode.CONSOLE,
                           "logger": ln}
    check_execute(request_parameters=request_parameters,
                  response_parameters=response_parameters)


def parse_check_system(args):
    request_parameters = {"type": "system",
                          "logger": ln}
    response_parameters = {"storage_type": const.StorageMode.CONSOLE,
                           "logger": ln}
    check_execute(request_parameters=request_parameters,
                  response_parameters=response_parameters)


def parse_check_network(args):
    request_parameters = {"type": "network",
                          "logger": ln}
    response_parameters = {"storage_type": const.StorageMode.CONSOLE,
                           "logger": ln}
    check_execute(request_parameters=request_parameters,
                  response_parameters=response_parameters)


# subcommand - check
def console_check(subparsers):
    parser_check = subparsers.add_parser(
        "check",
        help="Natrix Client Sub Command - check. "
             "check the information such as system, hardware and so on..."
    )
    # 创建子命令项
    checksubparsers = parser_check.add_subparsers(title="Natrix Client Check Sub Command",
                                                  description="Natrix Client Check Sub Command.",
                                                  help='help information about the natrix client check sub command')

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



# -*- coding: utf-8 -*-
"""

"""

from natrixclient.common import const
from natrixclient.command.nreport import execute as report_execute

from natrixclient.bin import ln



def parse_report_basic(*args):
    request_parameters = {"type": "basic",
                          "logger": ln}
    response_parameters = dict()
    response_parameters["storage_type"] = const.StorageMode.RABBITMQ
    response_parameters["storage_queue"] = const.QUEUE_KEEP_ALIVE_BASIC
    response_parameters["storage_routing"] = const.ROUTING_KEEP_ALIVE_BASIC
    response_parameters["logger"] = ln
    report_execute(request_parameters=request_parameters,
                   response_parameters=response_parameters)


def parse_report_advance(*args):
    request_parameters = {"type": "advance",
                          "logger": ln}
    response_parameters = dict()
    response_parameters["storage_type"] = const.StorageMode.RABBITMQ
    response_parameters["storage_queue"] = const.QUEUE_KEEP_ALIVE_ADVANCE
    response_parameters["storage_routing"] = const.ROUTING_KEEP_ALIVE_ADVANCE
    response_parameters["logger"] = ln
    report_execute(request_parameters=request_parameters,
                   response_parameters=response_parameters)


# subcommand - report
def console_report(subparsers):
    parser_report = subparsers.add_parser("report",
                                          help="Natrix Client Sub Command - Report. "
                                               "report information to AMQP server")
    # 创建子命令项
    report_subparsers = parser_report.add_subparsers(title="Natrix Client Report Sub Command",
                                                     help='help information about the natrix client report sub command')
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


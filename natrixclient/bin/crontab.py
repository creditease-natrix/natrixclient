# -*- coding: utf-8 -*-
"""

"""

from crontab import CronTab

from natrixclient.common import const
from natrixclient.bin import logger


# TODO: think about this module is neccesary

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


def parse_crontab_basic(args):
    basic_minutes = args.minutes
    create_crontab_basic(basic_minutes)


def parse_crontab_advance(args):
    advance_minutes = args.minutes
    create_crontab_advance(advance_minutes)


def parse_crontab_reboot(args):
    reboot_hours = args.hours
    reboot_minutes = args.minutes
    create_crontab_reboot(reboot_hours, reboot_minutes)


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
def console_crontab(subparsers):
    parser_crontab = subparsers.add_parser("crontab",
                                           help="Natrix Client Sub Command - crontab. "
                                                "set crontab job for keepalive information to AMQP server")
    # 创建子命令项
    crontab_subparsers = parser_crontab.add_subparsers(title="Natrix Client Crontab Sub Command",
                                                       help='help information about the natrix client crontab sub command')
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



# -*- coding: utf-8 -*-
"""

"""

import os, subprocess, time, shutil

from natrixclient.common import const

from natrixclient.bin import logger
from natrixclient.bin import SEPARATOR_COUNT
from natrixclient.bin.crontab import parse_crontab_clean, create_crontab_basic, create_crontab_advance, create_crontab_reboot


def init_service_etc():
    conf_dir = const.CONFIG_DIR
    logger.info("\n1. creating configuration directory {} ......".format(conf_dir))
    if os.path.isdir(conf_dir):
        logger.info("configuration directory {} exist".format(conf_dir))
    else:
        logger.info("creating configuration directory {}".format(conf_dir))
        os.makedirs(conf_dir)

    # copy configuration files to /etc/natrixclient
    logger.info("")
    logger.info("\n2. copying sample configuration files to {}......".format(conf_dir))
    sample_dir = os.path.dirname(os.path.realpath(__file__)) + "/../conf/etc/natrixclient/"
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


def init_service_log():
    log_dir = "/var/log/natrixclient/"
    logger.info("\n3. creating log directory {} ......".format(log_dir))
    if os.path.isdir(log_dir):
        logger.info("log directory {} exist".format(log_dir))
    else:
        logger.info("creating log directory {}".format(log_dir))
        os.makedirs(log_dir)


def init_service_systemctl():
    systemd_dir = "/etc/systemd/system/"
    logger.debug("\n4. copying sample systemd files to {}".format(systemd_dir))
    sample_systemd_dir = os.path.dirname(os.path.realpath(__file__)) + "/../conf/etc/systemd/system/"
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

    logger.debug("\n5. reloading systemd daemon service")
    # must add shell=True
    daemon_reload_command = "systemctl daemon-reload"
    daemon_reload_process = subprocess.Popen(daemon_reload_command,
                                             stdin=subprocess.PIPE,
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE,
                                             shell=True)
    # communicate() returns a tuple (stdout, stderr)
    daemon_reload_result = daemon_reload_process.communicate()
    logger.debug("daemon reload command \"{}\" result: {}".format(daemon_reload_command,
                                                                  daemon_reload_result))


def parse_service_init(args):
    logger.info("=" * SEPARATOR_COUNT)
    logger.info("initializing natrixclient services ......")
    # 提升到root权限
    if os.geteuid():
        logger.error("must be root or have sudo authorization")
        exit(101)

    init_service_etc()
    init_service_log()
    init_service_systemctl()

    logger.info("\nsuccessfully initialized natrix client services")
    logger.info("=" * SEPARATOR_COUNT)


def parse_service_start(args):
    logger.info("=" * SEPARATOR_COUNT)
    logger.info("starting natrixclient services ......")
    # systemd service files
    logger.info("\n1. checking natrixclient systemd service files ......")
    systemd_paths = ["/etc/systemd/system/natrixclient.service"]
    for systemd_path in systemd_paths:
        logger.info("checking natrixclient systemd file {}".format(systemd_path))
        if os.path.isfile(systemd_path):
            logger.debug("natrixclient systemd file {} exist".format(systemd_path))
        else:
            logger.error("natrixclient systemd file {} not exist, please execute \"natrixclient service init\" first!!!")
            exit(201)
    # systemd daemon files
    logger.info("\n2. checking natrixclient systemd daemon files ......")
    # TODO: CHANGE
    daemon_paths = ["/etc/natrixclient/natrixclient.daemon"]
    for daemon_path in daemon_paths:
        logger.info("checking natrixclient daemon service file {}".format(daemon_path))
        if os.path.isfile(daemon_path):
            logger.debug("natrixclient daemon service file {} exist".format(daemon_path))
        else:
            logger.error("natrixclient daemon service file {} not exist, "
                         "please execute \"natrixclient service init\" first!!!".format(daemon_path))
            exit(202)
    # start systemd service
    logger.info("\n3. starting natrixclient services ......")
    services = ["natrixclient.service"]
    for service in services:
        logger.debug("starting systemd service {}".format(service))
        # must add shell=True
        service_start_command = "systemctl start " + service
        service_start_process = subprocess.Popen(service_start_command,
                                                 stdin=subprocess.PIPE,
                                                 stdout=subprocess.PIPE,
                                                 stderr=subprocess.PIPE,
                                                 shell=True)
        # communicate() returns a tuple (stdout, stderr)
        service_start_result = service_start_process.communicate()
        logger.debug("service start command: \"{}\" \nresult: \"{}\"".format(service_start_command,
                                                                             service_start_result))
    # # add crontab job
    # # add keep alive basic crontab job
    # logger.info("\n4. adding keep alive basic crontab job ......")
    # basic_minutes = const.CRONTAB_BASIC_MINUTES
    # create_crontab_basic(basic_minutes)
    # # add keep alive advance crontab job
    # logger.info("\n5. adding keep alive advance crontab job ......")
    # advance_minutes = const.CRONTAB_ADVANCE_MINUTES
    # create_crontab_advance(advance_minutes)

    # add reboot at midnight crontab job
    logger.info("\n4. adding reboot at midnight crontab job ......")
    reboot_hours = const.CRONTAB_REBOOT_HOURS
    reboot_minutes = const.CRONTAB_REBOOT_MINUTES
    create_crontab_reboot(reboot_hours, reboot_minutes)

    logger.info("\nsuccessfully started natrix client services")
    logger.info("=" * SEPARATOR_COUNT)


def parse_service_enable(args):
    logger.info("=" * SEPARATOR_COUNT)
    logger.info("enabling natrixclient services .....")
    # systemd service files
    logger.info("\n1. checking systemd service files ......")
    systemd_paths = ["/etc/systemd/system/natrixclient.service"]
    for systemd_path in systemd_paths:
        logger.info("checking systemd file {}".format(systemd_path))
        if os.path.isfile(systemd_path):
            logger.debug("systemd file {} exist".format(systemd_path))
        else:
            logger.error("systemd file {} not exist, please execute \"natrixclient service init\" first!!!")
            exit(401)
    # systemd daemon files
    logger.info("\n2. checking systemd daemon files ......")
    daemon_paths = ["/etc/natrix/natrixclient.daemon"]
    for daemon_path in daemon_paths:
        logger.info("checking natrixclient daemon service file {}".format(daemon_path))
        if os.path.isfile(daemon_path):
            logger.debug("natrixclient daemon service file {} exist".format(daemon_path))
        else:
            logger.error("natrixclient daemon service file {} not exist, "
                         "please execute \"natrixclient service init\" first!!!".format(daemon_path))
            exit(402)
    # start systemd service
    logger.info("\n3. enabling systemd services ......")
    services = ["natrixclient.service"]
    for service in services:
        logger.debug("enabling systemd service {}".format(service))
        # must add shell=True
        service_enable_command = "systemctl enable " + service
        service_enable_process = subprocess.Popen(service_enable_command,
                                                  stdin=subprocess.PIPE,
                                                  stdout=subprocess.PIPE,
                                                  stderr=subprocess.PIPE,
                                                  shell=True)
        # communicate() returns a tuple (stdout, stderr)
        service_enable_result = service_enable_process.communicate()
        logger.debug("service enable command: \"{}\" \nresult: \"{}\"".format(service_enable_command, service_enable_result))

    # # add crontab job
    # # add keep alive basic crontab job
    # logger.info("\n4. adding keep alive basic crontab job ......")
    # basic_minutes = const.CRONTAB_BASIC_MINUTES
    # create_crontab_basic(basic_minutes)
    # # add keep alive advance crontab job
    # logger.info("\n5. adding keep alive advance crontab job ......")
    # advance_minutes = const.CRONTAB_ADVANCE_MINUTES
    # create_crontab_advance(advance_minutes)

    # add reboot at midnight crontab job
    logger.info("\n6. adding reboot at midnight crontab job ......")
    reboot_hours = const.CRONTAB_REBOOT_HOURS
    reboot_minutes = const.CRONTAB_REBOOT_MINUTES
    create_crontab_reboot(reboot_hours, reboot_minutes)

    logger.info("\nsuccessfully enabled natrix client services")
    logger.info("=" * SEPARATOR_COUNT)


def parse_service_stop(args):
    logger.info("=" * SEPARATOR_COUNT)
    logger.info("stopping natrixclient services ......")
    # stop service
    # start systemd service
    logger.info("\n1. stopping systemd service ......")
    services = ["natrixclient.service"]
    for service in services:
        logger.debug("stopping systemd service {}".format(service))
        # must add shell=True
        service_stop_command = "systemctl stop " + service
        service_stop_process = subprocess.Popen(service_stop_command,
                                                stdin=subprocess.PIPE,
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE,
                                                shell=True)
        # communicate() returns a tuple (stdout, stderr)
        service_stop_result = service_stop_process.communicate()
        logger.debug("service stop command: \"{}\" \nresult: \"{}\"".format(service_stop_command, service_stop_result))
    # clean crontab
    logger.info("\n2. clean all natrixclient crontab jobs ......")
    parse_crontab_clean(None)
    logger.info("\nsuccessfully stopped natrixclient services")
    logger.info("=" * SEPARATOR_COUNT)


def parse_service_disable(args):
    logger.info("=" * SEPARATOR_COUNT)
    logger.info("disabling natrixclient services ......")
    # stop service
    # start systemd service
    logger.info("\n1. disabling systemd services ......")
    services = ["natrixclient.service"]
    for service in services:
        logger.debug("disabling systemd service {}".format(service))
        # must add shell=True
        service_disable_command = "systemctl disable " + service
        service_disable_process = subprocess.Popen(service_disable_command,
                                                   stdin=subprocess.PIPE,
                                                   stdout=subprocess.PIPE,
                                                   stderr=subprocess.PIPE,
                                                   shell=True)
        # communicate() returns a tuple (stdout, stderr)
        service_disable_result = service_disable_process.communicate()
        logger.debug("service disable command: \"{}\" \nresult: \"{}\"".format(service_disable_command, service_disable_result))
    # clean crontab
    logger.info("\n2. clean all natrixclient crontab jobs ......")
    parse_crontab_clean(None)
    logger.info("\nsuccessfully disabled natrixclient services")
    logger.info("=" * SEPARATOR_COUNT)


def parse_service_status(args):
    logger.info("=" * SEPARATOR_COUNT)
    logger.info("checking natrixclient services status......")
    # systemd service
    logger.info("\n1. checking systemd services status ......")
    services = ["natrixclient.service"]
    for service in services:
        logger.debug("checking service {} status".format(service))
        service_status_command = "systemctl status " + service
        service_status_process = subprocess.Popen(service_status_command,
                                                  stdin=subprocess.PIPE,
                                                  stdout=subprocess.PIPE,
                                                  stderr=subprocess.PIPE, shell=True)
        service_status_result = service_status_process.communicate()
        # logger.debug("service status command \"{}\" result: {}".format(service_status_command, service_status_result))
        service_status_string = service_status_result[0].decode()
        logger.info(service_status_string)
    # crontab -l
    logger.info("\n2. checking crontab jobs status")
    crontab_status_command = "crontab -l"
    crontab_status_process = subprocess.Popen(crontab_status_command,
                                              stdin=subprocess.PIPE,
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE,
                                              shell=True)
    crontab_status_result = crontab_status_process.communicate()
    # logger.debug("crontab status command \"{}\" result: {}".format(crontab_status_command, crontab_status_result))
    crontab_status_string = crontab_status_result[0].decode()
    logger.info(crontab_status_string)
    logger.info("\nsuccessfully checking natrixclient status")
    logger.info("=" * SEPARATOR_COUNT)


# subcommand - service
def console_service(subparsers):
    parser_service = subparsers.add_parser("service",
                                           help="Natrix Client Sub Command - service. "
                                                "Natrix Client Service Operation: init/start/stop/status/ennable/disable")
    # 创建子命令项
    service_subparsers = parser_service.add_subparsers(title="Natrix Client service Sub Command",
                                                       help='help information about the service sub command')

    # init    sub-command
    parser_service_init = service_subparsers.add_parser('init',
                                                         help='natrix service sub command - init')
    parser_service_init.set_defaults(func=parse_service_init)

    # start   sub-command
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



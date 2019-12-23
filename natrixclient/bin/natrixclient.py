# -*- coding: utf-8 -*-
"""

"""
import os, sys
import argparse

from natrixclient.bin import ping, http, dns, traceroute
from natrixclient.bin import check, report
from natrixclient.bin import service



epilog = """
Natrix Client Command Line Interface.
Natrix - An Open Source Cloud Automation Testing Project.
"""
parser = argparse.ArgumentParser(prog="natrixclient",
                                 epilog=epilog,
                                 description="Natrix Client Command Line Interface")
# subcommand
subparsers = parser.add_subparsers(title="Natrix Client Sub Command",
                                   description="Natrix Client Sub Command.",
                                   help='help information about the natrix client sub command')


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




def main(argv=None):
    try:
        console_common()
        ping.console_ping(subparsers)
        http.console_http(subparsers)
        dns.console_dns(subparsers)
        traceroute.console_traceroute(subparsers)

        check.console_check(subparsers)
        report.console_report(subparsers)

        service.console_service(subparsers)

        args = parser.parse_args()
        args.func(args)
    except KeyboardInterrupt:
        pass



if __name__ == "__main__":
    if os.geteuid():
        args = [sys.executable] + sys.argv
        os.execlp('sudo', 'sudo', *args)

    main()




# -*- coding: utf-8 -*-
"""

"""


def parse_performance():
    pass


# subcommand - performance
def console_performance(subparsers):
    parser_perf = subparsers.add_parser(
        "performance",
        help='Natrix Client Sub Command - performance.'
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



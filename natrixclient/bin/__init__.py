# -*- coding: utf-8 -*-

import logging

from natrixclient.common import const

ln = "natrixclient.console"
logger = logging.getLogger(ln)
logger.setLevel(const.CONSOLE_LEVEL)
logger.propagate = False

# create console handler with a higher log level
ch = logging.StreamHandler()

ch.setLevel(const.CONSOLE_STREAM_LEVEL)
# create formatter and add it to the handlers
ch_fmt = logging.Formatter(fmt=const.CONSOLE_LOGGING_FORMAT)
ch.setFormatter(ch_fmt)
# add the handlers to logger
logger.addHandler(ch)

SEPARATOR_COUNT = 88
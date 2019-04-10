#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging
import threading
from natrixclient.common.const import LOGGING_PATH
from natrixclient.common.const import FILE_MAX_BYTES
from natrixclient.common.const import FILE_BACKUP_COUNTS
from natrixclient.common.const import FILE_LOGGING_DATE_FORMAT
from natrixclient.common.const import THREAD_LOGGING_FORMAT
from natrixclient.command.ncheck import CheckTest
from natrixclient.command.storage import storage


logger = logging.getLogger(__name__)


def add_logger_handler(logger):
    fn = LOGGING_PATH + 'natrixclient_report.log'
    fh = logging.handlers.RotatingFileHandler(filename=fn, maxBytes=FILE_MAX_BYTES, backupCount=FILE_BACKUP_COUNTS)
    fh.setLevel(logging.DEBUG)
    fh_fmt = logging.Formatter(fmt=THREAD_LOGGING_FORMAT, datefmt=FILE_LOGGING_DATE_FORMAT)
    fh.setFormatter(fh_fmt)
    logger.addHandler(fh)


def execute(request_parameters, response_parameters):
    if request_parameters.get("logger"):
        global logger
        logger = logging.getLogger(request_parameters.get("logger"))
        add_logger_handler(logger)
    logger.info("==================REPORT EXECUTE========================")
    ReportThread(request_parameters=request_parameters,
                 response_parameters=response_parameters).start()


class ReportThread(threading.Thread):
    def __init__(self, request_parameters, response_parameters):
        threading.Thread.__init__(self)
        self.request_parameters = request_parameters
        self.response_parameters = response_parameters

    def run(self):
        check_obj = CheckTest(self.request_parameters)
        check_dict = check_obj.check()

        storage(result=check_dict,
                parameters=self.response_parameters)

# -*- coding: utf-8 -*-
import logging
from logging.handlers import WatchedFileHandler

from natrixclient.common.config import NatrixConfig
from natrixclient.common.const import FILE_LOGGING_FORMAT, FILE_LOGGING_DATE_FORMAT, CONSOLE_LOGGING_FORMAT

natrix_config = NatrixConfig()
log_directory = natrix_config.get_value('COMMON', 'log_directory')
log_level = logging.getLevelName(natrix_config.get_value('COMMON', 'log_level').upper())


def add_logger(logger_name,
               file_name=None, parent=None,
               propagate=False,
               log_level='INFO', log_dir='/var/log/natrixclient'):
    """Add a new logger

    :param logger_name:
    :param file_name:
    :param parent:
    :param propagate:
    :param log_level:
    :param log_dir:
    :return:
    """
    logger = logging.getLogger(logger_name)
    logger.propagate = propagate
    logger.parent = parent
    file_name = logger_name if file_name is None else file_name
    log_file_name = '{log_dir}/{file_name}.log'.format(log_dir=log_dir, file_name=file_name)
    handler = WatchedFileHandler(filename=log_file_name)
    handler_fmt = logging.Formatter(fmt=FILE_LOGGING_FORMAT, datefmt=FILE_LOGGING_DATE_FORMAT)
    handler.setLevel(log_level)
    handler.setFormatter(handler_fmt)

    logger.addHandler(handler)


def init_logger():
    add_logger('natrixclient', file_name='natrixclient', log_level=log_level, log_dir=log_directory)

    logger_list = ['natrixclient.backends', 'natrixclient.report']
    for logger_name in logger_list:
        add_logger(logger_name,
                   file_name=logger_name.split('.')[-1],
                   log_level=log_level,
                   log_dir=log_directory)


init_logger()


class NatrixLogging:

    def __init__(self, name=None):
        if name is None:
            self.logger = logging.getLogger('natrixclient')
        else:
            logger = logging.getLogger(name=name)
            if logger.handlers:
                self.logger = logger
            else:
                self.logger = logging.getLogger('natrixclient')

    def debug(self, *args, **kwargs):
        if log_level <= logging.DEBUG:
            self.logger.debug(*args, **kwargs)

    def info(self, *args, **kwargs):
        if log_level <= logging.INFO:
            self.logger.info(*args, **kwargs)

    def error(self, *args, **kwargs):
        if log_level <= logging.ERROR:
            self.logger.error(*args, **kwargs)

    def log(self, *args, **kwargs):
        self.info(*args, **kwargs)

    def print(self, message):
        print(message)


if __name__ == '__main__':
    natrix_logger = NatrixLogging(__name__)
    natrix_logger.info('info')
    natrix_logger.error(('error'))
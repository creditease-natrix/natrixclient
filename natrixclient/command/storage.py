#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import pika
import time
from natrixclient.common.const import LOGGING_PATH
from natrixclient.common.const import FILE_MAX_BYTES
from natrixclient.common.const import FILE_BACKUP_COUNTS
from natrixclient.common.const import FILE_LOGGING_DATE_FORMAT
from natrixclient.common.const import THREAD_LOGGING_FORMAT
from natrixclient.common.const import StorageMode
from natrixclient.common.config import NatrixConfig


logger = logging.getLogger(__name__)


def add_logger_handler(logger):
    fn = LOGGING_PATH + 'natrixclient_storage.log'
    fh = logging.handlers.RotatingFileHandler(filename=fn, maxBytes=FILE_MAX_BYTES, backupCount=FILE_BACKUP_COUNTS)
    fh.setLevel(logging.DEBUG)
    fh_fmt = logging.Formatter(fmt=THREAD_LOGGING_FORMAT, datefmt=FILE_LOGGING_DATE_FORMAT)
    fh.setFormatter(fh_fmt)
    logger.addHandler(fh)


def storage(result, parameters):
    # logger
    if parameters.get("logger"):
        global logger
        logger = logging.getLogger(parameters.get("logger"))
        add_logger_handler(logger)
    # terminal_response_return_time
    if result.get("stamp"):
        result["stamp"]["terminal_response_return_time"] = time.time()
    storage_type = parameters.get("storage_type")
    logger.debug("storage type = {}".format(storage_type))
    if storage_type == StorageMode.CONSOLE:
        logger.debug("natrix result will display in console")
        console(result)
    elif storage_type == StorageMode.RESTFUL:
        logger.debug("natrix result will provide as a restful api")
        restful(result)
    elif storage_type == StorageMode.FILE:
        logger.debug("natrix result will storage in file")
        file(result)
    elif storage_type == StorageMode.RABBITMQ:
        logger.debug("natrix result will save to rabbitmq")
        logger.debug(result)
        rabbitmq(result, parameters)
    else:
        logger.error("do not support storage type {}, will display in console as default")
        console(result)


def console(result):
    # TODO, 对输出格式进行美化
    logger.info(result)
    logger.info("======================================================")


def rabbitmq(result, parameters):
    logger.debug("storage result: {}".format(result))
    config = NatrixConfig()
    host = config.get_value("RABBITMQ", "host")
    port = config.get_value("RABBITMQ", "port")
    username = config.get_value("RABBITMQ", "username")
    password = config.get_value("RABBITMQ", "password")
    vhost = config.get_value("RABBITMQ", "vhost")
    credentials = pika.PlainCredentials(username, password)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host,
            int(port),
            vhost,
            credentials))
    channel = connection.channel()

    queue_name = parameters.get("storage_queue")
    logger.debug("storage queue name: {}".format(queue_name))
    routing_key = parameters.get("storage_routing")
    logger.debug("storage routing key: {}".format(routing_key))

    # 声明queue, 针对需要目标url/ip的命令， 如dns, traceroute, ping, http
    if queue_name:
        channel.queue_declare(queue=queue_name, auto_delete=True)
        # RabbitMQ a message can never be sent directly to the queue, it always needs to go through an exchange.
        channel.basic_publish(exchange='',
                              routing_key=routing_key,
                              body=json.dumps(result))

    # 声明queue, 针对需要目标url/ip的命令，如check
    else:
        logger.error("storage queue name is empty")
    connection.close()


def restful(result):
    logger.info(result)
    return result


def file(result):
    logger.info(result)
    return result


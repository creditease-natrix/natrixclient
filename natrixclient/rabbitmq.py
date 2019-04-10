#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json
import pika
import sys
import time
from logging.handlers import RotatingFileHandler
from natrixclient.common import const
from natrixclient.common.const import RABBITMQ_LEVEL
from natrixclient.common.const import RABBITMQ_FILE_LEVEL
from natrixclient.common.const import RABBITMQ_STREAM_LEVEL
from natrixclient.common.const import FILE_MAX_BYTES
from natrixclient.common.const import FILE_BACKUP_COUNTS
from natrixclient.common.const import Command
from natrixclient.common.const import HttpOperation
from natrixclient.common.config import NatrixConfig
from natrixclient.command.check.network import NetInfo
from natrixclient.command.nping import execute as ping_execute
from natrixclient.command.ntraceroute import execute as traceroute_execute
from natrixclient.command.ndns import execute as dns_execute
from natrixclient.command.nhttp import execute as http_execute


ln = "natrixclient_rabbitmq"
logger = logging.getLogger(ln)
logger.setLevel(RABBITMQ_LEVEL)

# create file handler which logs even debug messages
fn = const.LOGGING_PATH + ln + '.log'
fh = RotatingFileHandler(filename=fn, maxBytes=FILE_MAX_BYTES, backupCount=FILE_BACKUP_COUNTS)
fh.setLevel(RABBITMQ_FILE_LEVEL)
fh_fmt = logging.Formatter(fmt=const.FILE_LOGGING_FORMAT, datefmt=const.FILE_LOGGING_DATE_FORMAT)
fh.setFormatter(fh_fmt)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(RABBITMQ_STREAM_LEVEL)
# create formatter and add it to the handlers
ch_fmt = logging.Formatter(fmt=const.CONSOLE_LOGGING_FORMAT)
ch.setFormatter(ch_fmt)

# add the handlers to logger
logger.addHandler(ch)
logger.addHandler(fh)


# callback function
def queue_callback(_ch, _method, _properties, body):
    # 接收
    logger.debug("Receive request [x]: {}".format(body))
    command = json.loads(body)
    protocol = command["protocol"]
    destination = command["destination"]
    # request_parameters
    request_parameters = dict()
    if command.get("parameters"):
        request_parameters = command.get("parameters")
    # server_request_generate_time
    request_parameters["server_request_generate_time"] = command["generate_timestamp"]
    # terminal_request_receive_time
    request_parameters["terminal_request_receive_time"] = time.time()
    # set logger to request
    request_parameters["logger"] = ln
    # response_parameters
    response_parameters = dict()
    response_parameters["storage_type"] = const.StorageMode.RABBITMQ
    response_parameters["storage_queue"] = const.REQUEST_STORAGE_QUEUE_NAME
    response_parameters["storage_routing"] = const.REQUEST_STORAGE_ROUTING_KEY
    response_parameters["command_uuid"] = command["uuid"]
    response_parameters["command_terminal"] = command["terminal"]
    # set logger to response
    response_parameters["logger"] = ln

    # 分发, 根据command_protocol
    if protocol.lower() == Command.PING.value:
        logger.info("executing ping ......")
        ping_execute(destination, request_parameters, response_parameters)
    elif protocol.lower() == Command.TRACEROUTE.value:
        logger.info("executing traceroute ......")
        traceroute_execute(destination, request_parameters, response_parameters)
    elif protocol.lower() == Command.DNS.value:
        logger.info("executing dns ......")
        dns_execute(destination, request_parameters, response_parameters)
    elif protocol.lower() == Command.HTTP.value:
        operation = request_parameters.get("operation")
        if operation:
            if operation.lower() == HttpOperation.GET.value:
                http_operation = HttpOperation.GET
            elif operation.lower() == HttpOperation.POST.value:
                http_operation = HttpOperation.POST
            elif operation.lower() == HttpOperation.PUT.value:
                http_operation = HttpOperation.PUT
            elif operation.lower() == HttpOperation.DELETE.value:
                http_operation = HttpOperation.DELETE
            else:
                print("ERROR, do not support operation {}, will use get as default".format(protocol.lower()))
                logging.error("ERROR, do not support operation {}, will use get as default".format(protocol.lower()))
            logger.info("executing http {} ......".format(http_operation.value))
            http_execute(http_operation, destination, request_parameters, response_parameters)
        else:
            logger.error("parameter operation is required for HTTP")
    else:
        logger.error("Natrix do not support {}".format(protocol))


def start():
    # 1. check /etc/natrix/natrix.ini, get the AMQP paramters
    config = NatrixConfig()
    host = config.get_value("RABBITMQ", "host")
    port = config.get_value("RABBITMQ", "port")
    vhost = config.get_value("RABBITMQ", "vhost")
    username = config.get_value("RABBITMQ", "username")
    password = config.get_value("RABBITMQ", "password")

    # 4. connect to AQMP queue and consume messages
    credentials = pika.PlainCredentials(username, password)
    parameters = pika.ConnectionParameters(host, int(port), vhost, credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    # 5. get macaddress, create queues based on mac address
    macs = NetInfo().get_macs()
    for mac in macs:
        queue_name = const.QUEUE_COMMAND_PREFIX + mac.lower()
        logger.debug("declare rabbitmq queue: {}".format(queue_name))
        channel.queue_declare(queue=queue_name,
                              durable=True,
                              arguments={
                                  'x-message-ttl': 120000,
                                  'x-dead-letter-exchange': const.EXCHANGE_COMMAND_DEAD,
                                  'x-dead-letter-routing-key': 'dead_command'
                              })
        logger.debug("consume rabbitmq queue: {}".format(queue_name))
        channel.basic_consume(queue_callback, queue_name)
    try:
        logger.debug("start rabbitmq channel consuming")
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.exception("stop rabbitmq channel consuming using KeyboardInterrupt")
        channel.stop_consuming()
    except Exception:
        logger.exception("stop rabbitmq channel consuming by Exception")
        channel.stop_consuming()
    finally:
        connection.close()


def stop():
    logger.info("natrixclient service stop")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("should choose action: start/stop")
        logger.error("should choose action: start/stop")
        exit(1)
    if sys.argv[1].lower() == "start":
        logger.debug("action: start")
        start()
    elif sys.argv[1].lower() == "stop":
        logger.debug("action: stop")
        stop()
    else:
        print("Do not support action {}, please support start/stop".format(sys.argv[1]))
        logger.error("Do not support action {}, please support start/stop".format(sys.argv[1]))
        exit(2)


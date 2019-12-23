#!/usr/bin/env python
"""

"""
import pika, json, threading

from natrixclient.common.config import NatrixConfig
from natrixclient.common import const
from natrixclient.command.check.network import NetInfo
from natrixclient.bin.report import parse_report_basic, parse_report_advance
from natrixclient.backends.base import SingletonService
from natrixclient.backends.command_processor import processor

from .base import logger


config = NatrixConfig()
host = config.get_value("RABBITMQ", "host")
port = config.get_value("RABBITMQ", "port")
vhost = config.get_value("RABBITMQ", "vhost")
username = config.get_value("RABBITMQ", "username")
password = config.get_value("RABBITMQ", "password")


class CommandService(threading.Thread):
    """

    """

    def run(self):
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
            channel.basic_consume(self.queue_callback, queue_name)

        try:
            logger.debug("start rabbitmq channel consuming")
            channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("stop rabbitmq channel consuming using KeyboardInterrupt")
            channel.stop_consuming()
        except Exception:
            logger.info("stop rabbitmq channel consuming by Exception")
            channel.stop_consuming()
        finally:
            connection.close()

    def queue_callback(self, _ch, _method, _properties, body):
        # 接收
        logger.debug("Receive request [x]: {}".format(body))
        try:
            command = json.loads(body.decode('utf-8'))
        except TypeError:
            command = json.loads(body)

        test_data = processor(command)
        self.response(test_data)
        _ch.basic_ack(delivery_tag=_method.delivery_tag)


    def response(self, result):
        credentials = pika.PlainCredentials(username, password)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host,
                int(port),
                vhost,
                credentials))
        channel = connection.channel()
        queue_name = const.REQUEST_STORAGE_QUEUE_NAME
        routing_key = const.REQUEST_STORAGE_ROUTING_KEY

        if queue_name:
            channel.queue_declare(queue=queue_name, durable=True)
            # RabbitMQ a message can never be sent directly to the queue, it always needs to go through an exchange.
            channel.basic_publish(exchange='',
                                  routing_key=routing_key,
                                  body=json.dumps(result))

        else:
            logger.error("storage queue name is empty")
        connection.close()


class DeviceBasicService(threading.Thread):
    """

    """

    def run(self):
        parse_report_basic()

    def publish_info(self, message, parameters):
        credentials = pika.PlainCredentials(username, password)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host, int(port), vhost, credentials))
        channel = connection.channel()

        queue_name = parameters.get("storage_queue")
        logger.debug("storage queue name: {}".format(queue_name))
        routing_key = parameters.get("storage_routing")
        logger.debug("storage routing key: {}".format(routing_key))

        # 声明queue, 针对需要目标url/ip的命令， 如dns, traceroute, ping, http
        if queue_name:
            channel.queue_declare(queue=queue_name, durable=True)
            # RabbitMQ a message can never be sent directly to the queue, it always needs to go through an exchange.
            channel.basic_publish(exchange='',
                                  routing_key=routing_key,
                                  body=json.dumps(message))

        # 声明queue, 针对需要目标url/ip的命令，如check
        else:
            logger.error("storage queue name is empty")
        connection.close()


class DeviceAdvancedService(threading.Thread):
    """

    """
    def run(self):
        parse_report_advance()


def start():
    try:
        main_thread = threading.current_thread()
        # command_service = CommandService()
        # command_service.start()

        single_service = SingletonService()
        single_service.init(main_thread, DeviceBasicService, DeviceAdvancedService)
        single_service.start()

        # device_service = BaseDeviceService(main_thread=main_thread,
        #                                    light_service=DeviceBasicService,
        #                                    heavy_service=DeviceAdvancedService)
        # device_service.start()

        # device_service.join()

    except Exception as e:
        logger.error('Start natrixclient service used rabbitmq with error {}'.format(e))


def stop():
    logger.info("natrixclient service stop")


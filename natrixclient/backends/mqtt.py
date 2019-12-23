# -*- coding: utf-8 -*-
"""

"""
import ssl, threading, json, time
import paho.mqtt.client as mqtt

from natrixclient.common.config import NatrixConfig
from natrixclient.command.ncheck import CheckTest
from natrixclient.command.check.network import NetInfo

from natrixclient.backends.base import SingletonService
from natrixclient.backends.command_processor import processor
from natrixclient.command.check.hardware import HardwareInfo

from natrixclient.backends.base import logger


CONFIG_TOPIC = 'MQTT'
config = NatrixConfig()
host = config.get_value(CONFIG_TOPIC, 'host')
port = int(config.get_value(CONFIG_TOPIC, 'port'))
vhost = config.get_value(CONFIG_TOPIC, 'vhost')
username = HardwareInfo.get_sn()
password = config.get_value(CONFIG_TOPIC, 'password')
client_id = config.get_value(CONFIG_TOPIC, 'client_id')
is_ssl = config.get_value(CONFIG_TOPIC, 'ssl')
keepalive = int(config.get_value(CONFIG_TOPIC, 'keepalive'))

COMMAND_SUBSCRIBE_QOS = 1
COMMAND_RESPONSE_QOS = 1
DEVICE_BASIC_QOS = 0
DEVICE_ADVANCED_QOS = 1


def natrix_mqttclient():
    """Generate a natrix mqtt client.

    This function encapsulates all configurations about natrix mqtt client.

    Include:
    - client_id
      The unique id about mqtt connection.
    - username & password
      Username is device serial number which used to identify who am I;


    :return:
    """

    client = mqtt.Client(client_id=client_id, clean_session=False)
    client.username_pw_set(username, password=password)
    if is_ssl.upper() == 'TRUE':
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        client.tls_set_context(ssl_context)

    # connection break
    will_message = json.dumps({'username': username, 'client_id': client_id})
    client.will_set(topic='natrix/disconnect/{}'.format(username),
                    payload=will_message,
                    retain=False)

    return client


client = natrix_mqttclient()


def publish_result_analyse(res, service=None):

    if res.rc == mqtt.MQTT_ERR_SUCCESS:
        if res.is_published():
            logger.info('Publish({})-mid({}) MQTT_ERR_SUCCESS(successfully)'.format(service, res.mid))
        else:
            if service == 'Device Basic Service':
                logger.info('Reconncting for basic publish error!')
            logger.error('Publish({})-mid({}) MQTT_ERR_SUCCESS, but is_published is False'.format(service, res.mid))
    elif res.rc == mqtt.MQTT_ERR_NO_CONN:
        logger.error('Publish({}) MQTT_ERR_NO_CONN'.format(service))
    elif res.rc == mqtt.MQTT_ERR_QUEUE_SIZE:
        logger.error('Publish({}) MQTT_ERR_QUEUE_SIZE'.format(service))
    else:
        logger.error('Publish({}) operation with an unkown error'.format(service))


class CommandProcessor(threading.Thread):

    def __init__(self, message, client):
        super(CommandProcessor, self).__init__()
        self.message = message
        self.command_info = message.payload
        self.client = client

    def run(self):
        # TODO: add connection checking
        logger.debug('CommandProcessor message : {}'.format(self.message))
        try:
            command = json.loads(str(self.command_info, encoding='utf-8'))
        except TypeError:
            command = json.loads(self.command_info)

        test_data = processor(command)
        if test_data is None:
            logger.error('Process Command with error: {}'.format(command))

        topic = self.message.topic.split('/')
        # TODO: add exception process
        terminal = topic[-1]

        test_data['command'] = {
            'uuid': command.get('uuid', None),
            'terminal': terminal
        }

        logger.debug('Dial test result : {}'.format(test_data))
        res = self.client.publish(topic='natrix/response',
                                  payload=json.dumps(test_data),
                                  qos=COMMAND_RESPONSE_QOS,
                                  retain=False)
        publish_result_analyse(res, 'command response')


class DeviceBasicService(threading.Thread):
    """

    """

    def __init__(self, client=client):
        super(DeviceBasicService, self).__init__()
        self.client = client
        logger.info('Basic Service : client state ({}) | ping_t ({})'.format(client._state, client._ping_t))
        self.topic_str = 'natrix/basic/{}'.format(username)

    def run(self):
        try:
            device_check = CheckTest(request_parameters={'type': 'basic'})
            device_info = device_check.check()

            res = self.client.publish(topic=self.topic_str,
                                      payload=json.dumps(device_info),
                                      qos=DEVICE_BASIC_QOS,
                                      retain=False)

            publish_result_analyse(res, 'Device Basic Service')
        except Exception as e:
            logger.error('There is an exception fro advanced reporter: {}'.format(e))


class DeviceAdvancedService(threading.Thread):
    """

    """

    def __init__(self, client=client):
        super(DeviceAdvancedService, self).__init__()

        self.client = client
        self.topic_str = 'natrix/advanced/{}'.format(username)

    def run(self):
        try:
            device_check = CheckTest(request_parameters={'type': 'advance'})
            device_info = device_check.check()
            res = self.client.publish(topic=self.topic_str,
                                      payload=json.dumps(device_info),
                                      qos=DEVICE_ADVANCED_QOS,
                                      retain=False)
            publish_result_analyse(res, 'Device Advance Service')
        except Exception as e:
            logger.error('There is an exception fro advanced reporter: {}'.format(e))


class CommandSubscribe(threading.Thread):

    def __init__(self, client=client):
        super(CommandSubscribe, self).__init__()

    def run(self):
        time.sleep(5)

        macs = NetInfo().get_macs()
        for mac in macs:
            client.subscribe('natrix/benchmark/{}'.format(mac), qos=COMMAND_SUBSCRIBE_QOS)

        client.message_callback_add('natrix/benchmark/#', SubscribeProcess.benchmark_process)


class SubscribeProcess:
    """Include all subscribe process

    """
    @staticmethod
    def benchmark_process(client, userdata, message):
        try:
            command_processor = CommandProcessor(message, client)
            command_processor.start()
        except Exception as e:
            logger.error('process benchmark command occur an error: {}'.format(e))


def on_connect(client, userdata, flags, rc):
    if rc > 0:
        logger.error(mqtt.connack_string(rc))
        return

    main_thread = threading.current_thread()

    # start to post terminal information
    single_service = SingletonService()
    single_service.init(main_thread, DeviceBasicService, DeviceAdvancedService)
    single_service.start()

    # subscribe pocess
    CommandSubscribe().start()


def disconnect():
    logger.error('occur a Disconnection Action!')


def socket_close_callback(client, userdata, sock):
    logger.error('Socket is closed for reading : {}, will reconnect after!'.format(sock))


def on_socket_unregister_write(client, userdata, sock):
    logger.error('Socket is closed for writing : {}, will  after!'.format(sock))


def on_subscribe(client, userdata, mid, granted_qos):
    logger.info('subscribe ...... {} {}'.format(client, userdata))


def on_publish_callback(client, userdata, mid):
    logger.info('publish data mid({})'.format(mid))


def log_callback(client, userdata, level, buf):
    logger.info('MQTT LOGGER : {}'.format(buf))


def start():
    try:
        client.on_connect = on_connect
        client.disconnect = disconnect
        client.on_subscribe = on_subscribe
        client.on_publish = on_publish_callback
        client.on_socket_close = socket_close_callback
        client.on_log = log_callback
        client.enable_logger()
        client.connect(host, port, keepalive)

        while True:
            rc = client.loop_forever()
            logger.error('loop_forever stop : {}'.format(mqtt.connack_string(rc)))
            client.reconnect()

    except KeyboardInterrupt as e:
        logger.info('Service End!')


def stop():
    pass


if __name__ == '__main__':
    start()
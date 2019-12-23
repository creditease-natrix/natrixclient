# -*- coding: utf-8 -*-
"""

"""
import sys

from natrixclient.common.config import NatrixConfig
from natrixclient.backends import mqtt, rabbitmq

natrix_config = NatrixConfig()


def start():
    backend_type = natrix_config.get_value("SERVICE", "backend").lower()
    if backend_type == "mqtt":
        mqtt.start()
    elif backend_type == "rabbitmq":
        rabbitmq.start()
    else:
        print("Get an unexpective backend type: {}".format(backend_type))


def stop():
    pass


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Should choose action: start/stop")
        exit(1)

    action = sys.argv[1].lower()

    if action== "start":
        start()
    elif action == "stop":
        stop()
    else:
        print("Dont support action {}, please use start/stop".format(action))
        exit(2)
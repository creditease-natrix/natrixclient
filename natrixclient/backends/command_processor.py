# -*- coding: utf-8 -*-
"""     """
import time

from natrixclient.common.const import Command, HttpOperation
from natrixclient.command import PingTest, HttpTest, DnsTest, RouteTest

from .base import ln, logger


def processor(command):
    test_data = None
    try:

        protocol = command['protocol']
        destination = command['destination']
        # request_parameters
        request_parameters = dict()
        if command.get('parameters'):
            request_parameters = command.get('parameters')
        # server_request_generate_time
        request_parameters['server_request_generate_time'] = command['generate_timestamp']
        # terminal_request_receive_time
        request_parameters['terminal_request_receive_time'] = time.time()
        # set logger to request
        request_parameters['logger'] = ln
        logger.info('receive command : {command_id} | {generate_timestamp}'.format(
            command_id=command['uuid'],
            generate_timestamp=command['generate_timestamp']
        ))
        # 分发, 根据command_protocol
        if protocol.lower() == Command.PING.value:
            ping_test = PingTest(destination, request_parameters)
            test_data = ping_test.ping()
        elif protocol.lower() == Command.TRACEROUTE.value:
            route_test = RouteTest(destination, request_parameters)
            test_data = route_test.execute()
        elif protocol.lower() == Command.DNS.value:
            dns_test = DnsTest(destination, request_parameters)
            test_data = dns_test.execute()
        elif protocol.lower() == Command.HTTP.value:
            operation = request_parameters.get('operation')
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
                    logger.error('ERROR, do not support operation {}, will use get as default'.format(protocol.lower()))
                http_test = HttpTest(http_operation, destination, request_parameters)
                test_data = http_test.execute()
            else:
                logger.error('parameter operation is required for HTTP')

        else:
            logger.error('Natrix do not support {}'.format(protocol))
    except Exception as e:
        logger.error('Process command with error: {}'.format(e))

    return test_data
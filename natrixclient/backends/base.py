# -*- coding: utf-8 -*-
"""

"""
import threading, time, logging
from natrixclient.common.natrix_logging import NatrixLogging

ln = 'natrixclient.backends'
logger = NatrixLogging(ln)


class _BaseDeviceService(threading.Thread):

    def __init__(self, main_thread, light_service, heavy_service):
        super(_BaseDeviceService, self).__init__()

        self.main_thread = main_thread
        self.light_service = light_service
        self.heavy_service = heavy_service
        # natrix clock every
        self.clock = 0
        self.slot = 30

    def start(self):
        if self.is_alive():
            logger.info('restart BaseDeviceService ....')
            return
        super(_BaseDeviceService, self).start()

    def run(self):

        while self.main_thread and self.main_thread.is_alive():
            logger.info('Device heartbeat times: {}'.format(int(self.clock / 30)))
            if self.clock % 30 == 0:
                self.light_service().start()

            if self.clock % 60 == 0:
                self.heavy_service().start()

            time.sleep(self.slot)
            self.clock += self.slot


class SingletonService(object):
    """

    """
    _instance_lock = threading.Lock()
    thread_count = 0

    def __new__(cls, *args, **kwargs):

        if not hasattr(SingletonService, '_instance'):
            with SingletonService._instance_lock:
                if not hasattr(SingletonService, '_instance'):
                    SingletonService._instance = object.__new__(cls)

        return SingletonService._instance

    def __init__(self):
        pass

    def init(self, main_thread, light_service, heavy_service):
        with SingletonService._instance_lock:
            if SingletonService.thread_count == 0:
                self.thread_instance = _BaseDeviceService(main_thread=main_thread,
                                                          light_service=light_service,
                                                          heavy_service=heavy_service)
                SingletonService.thread_count += 1
            else:
                logger.info('The thread instance has been created!')


    def start(self):
        self.thread_instance.start()


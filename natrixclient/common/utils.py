#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging

try:
    from subprocess import getstatusoutput
except ImportError:
    from commands import getstatusoutput


logger = logging.getLogger(__name__)


def get_command_output(command):
    status, output = getstatusoutput(command)
    return status, output

#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging
import subprocess


logger = logging.getLogger(__name__)


def get_command_output(command):
    try:
        # python 3
        status, output = subprocess.getstatusoutput(command)
    except AttributeError:
        # python 2
        import commands
        status, output = commands.getstatusoutput(command)
    return status, output

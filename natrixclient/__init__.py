#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os


def version():
    version = "0"
    dirpath = os.path.dirname(os.path.realpath(__file__))
    vfile = dirpath + "/__version__.py"
    with open(vfile, "r") as lines:
        for line in lines:
            # __version__ = '0.0.1'
            line = line.strip()
            if len(line) and line.startswith("__version__"):
                splits = line.split("=")
                version = splits[1].strip().rstrip("\"").lstrip("\"").rstrip("\'").lstrip("\'")
                break
    return version

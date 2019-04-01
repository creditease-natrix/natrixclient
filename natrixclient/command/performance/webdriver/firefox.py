#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from .browser import Browser


logger = logging.getLogger(__name__)


class Firefox(Browser):
    def __init__(self, headless=True):
        super().__init__()
        logger.info("output from firefox")
        self.headless = headless
        if headless:
            # headless mode
            firefox_options = Options()
            firefox_options.add_argument('-headless')
            self.browser = webdriver.Firefox(firefox_options=firefox_options)
        else:
            # common mode
            self.browser = webdriver.Firefox()

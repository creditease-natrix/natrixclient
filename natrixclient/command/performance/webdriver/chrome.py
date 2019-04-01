#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from .browser import Browser


logger = logging.getLogger(__name__)


class Chrome(Browser):
    def __init__(self, headless=True):
        super().__init__()
        logger.info('output from chrome')
        self.headless = headless
        if headless:
            # headless mode
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            self.browser = webdriver.Chrome(chrome_options=chrome_options)
        else:
            # common mode
            self.browser = webdriver.Chrome()

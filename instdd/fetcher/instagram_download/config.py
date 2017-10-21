#!/usr/bin/env python
import logging
import os

PROXIES = ""

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'

# logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
LOGGER = logging.getLogger('instagram-download')

BASE_DIR = os.path.dirname(__file__)

TIMEZONE = 'Asia/Shanghai'

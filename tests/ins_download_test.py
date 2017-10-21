#!/usr/bin/env python
from instdd.fetcher import InsDownload
from pprint import pprint

# url = "https://www.instagram.com/p/BSQ-Xm9hGsK/?taken-by=ruiazhou"

# https://www.instagram.com/p/BSbV7OUBU1a/

# https://www.instagram.com/ruiazhou/

# url = "https://www.instagram.com/p/BSbV7OUBU1a/"
# url = "https://www.instagram.com/ruiazhou/"
url = "https://www.instagram.com/p/BUwSt3FF0ku/?taken-by=errer_"
ins_down = InsDownload('data', url)
a = ins_down.test_start()
pprint(a)

# from urllib.parse import urlparse
#
#
# print(urlparse("https://www.instagram.com/p/BSQ-Xm9hGsK/?taken-by=ruiazhou"))

#!/usr/bin/env python
from instdd.fetcher import InsBestNine
import re
from pprint import pprint


ins_down = InsBestNine('best', 'instagram')
a = ins_down.test_start()
print(a)


def get_original_image(url):
    # remove dimensions to get largest image
    url = re.sub(r'/s\d{3,}x\d{3,}/', '/', url)
    # get non-square image if one exists
    url = re.sub(r'/c\d{1,}.\d{1,}.\d{1,}.\d{1,}/', '/', url)
    return url


# a = get_original_image(
#     "https://scontent.cdninstagram.com/t51.2885-15/s640x640/sh0.08/e35/14449150_206552643098150_470256884067074048_n.jpg")
#
# print(a)
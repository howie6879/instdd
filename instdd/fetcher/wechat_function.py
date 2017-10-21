#!/usr/bin/env python
import requests
import json
from configparser import ConfigParser

from pprint import pprint
from instdd.fetcher.function import get_timestamp
from instdd.config import AES_KEY, APP_ID, APP_SECRET, BASE_DIR, TIMEZONE, LOGGER


# =================================微信开发的一些接口==================================
# 1.get_access_token        获取微信access_token
# 2.custom_send_text        客服接口发送文字消息
#
#
# ===================================================================================

def get_access_token():
    """
    获取 access_token
    :return: token
    """
    cf = ConfigParser()
    file_name = BASE_DIR + "/fetcher/access_token.conf"
    cf.read(file_name)
    this_timestamp = int(cf.get("access_token", "timestamp"))
    curr_timestamp = get_timestamp()
    if curr_timestamp - this_timestamp <= 6720:
        token = cf.get("access_token", "token")
        return token
    else:
        url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APP_ID}&secret={APP_SECRET}".format(
            APP_ID=APP_ID,
            APP_SECRET=APP_SECRET,
        )
        try:
            result = requests.get(url).json()
            token = result['access_token']
            cf.set("access_token", "token", token)
            cf.set("access_token", "timestamp", str(get_timestamp()))
            cf.write(open(file_name, "w"))
        except Exception as e:
            LOGGER.exception(e)
            token = ''
        return token


def custom_send_text(user_id, text) -> bool:
    """
    客服接口发送文字消息 
    :param user_id: 用户唯一id
    :param text: 发送的文本
    :return: True or False
    """
    access_token = get_access_token()
    if access_token:
        url = "https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={access_token}".format(
            access_token=access_token)
        data = {
            "touser": user_id,
            "msgtype": "text",
            "text":
                {
                    "content": text
                }
        }
        json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        _r = requests.post(url, json_data)
        print(_r.content)
        if _r.status_code == 200 and 'errcode' not in _r.json():
            LOGGER.info('客服文本消息发送成功{0}'.format(text))
            return True
        else:
            LOGGER.info('客服文本消息发送失败{0}'.format(text))
            return False
    else:
        return False


# custom_send_text('oKJJBsyn8I6bWPFlTh24GjUY_Jxw', '22')

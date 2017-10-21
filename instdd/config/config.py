#!/usr/bin/env python
import logging
import os

# logging
logging_format = "[%(asctime)s] %(process)d-%(levelname)s "
logging_format += "%(module)s::%(funcName)s():l%(lineno)d: "
logging_format += "%(message)s"

logging.basicConfig(
    format=logging_format,
    level=logging.DEBUG
)
LOGGER = logging.getLogger()

WEBSITE = "https://www.instdd.com"
DEFAULT_IMG = "/static/images/all_media.jpg"

TOKEN = ""


AES_KEY = ''
APP_SECRET = ""
APP_ID = ""

WX_WELCOME = """
您好😍，欢迎关注图图推，我们为您提供最有爱❤️的服务：

    1.粘贴ins图片或者视频链接即可下载
    
    2.<a href="http://mp.weixin.qq.com/mp/homepage?__biz=MzI2NzY2NDk5Nw==&hid=1&sn=ad05690c560e92fe6794a5db478df49f#wechat_redirect">精选图片推荐</a>
    
    3.<a href="http://mp.weixin.qq.com/s/XaraDbtQtBKOSkpJOoH_IA">图片下载教程</a>
    
    4.<a href="http://mp.weixin.qq.com/s/3AIYYiiCUdt7pt4VRgz7NQ">视频下载教程</a>
    
    5.网站:http://www.instdd.com
    
最后祝您生活愉快💑，输入？获取帮助。
"""

WX_HELP = """
😍 图图推目前提供功能如下：

    1.粘贴ins图片或者视频链接即可下载
    
    2.<a href="http://mp.weixin.qq.com/mp/homepage?__biz=MzI2NzY2NDk5Nw==&hid=1&sn=ad05690c560e92fe6794a5db478df49f#wechat_redirect">精选图片推荐</a>
    
    3.<a href="http://mp.weixin.qq.com/s/XaraDbtQtBKOSkpJOoH_IA">图片下载教程</a>
    
    4.<a href="http://mp.weixin.qq.com/s/3AIYYiiCUdt7pt4VRgz7NQ">视频下载教程</a>
    
    5.网站:https://www.instdd.com
    
更多功能等您发掘。
"""

WX_RETURN_HELP = ['?', '？', '帮助', 'help']

WX_RETURN_REVIEW = ['review', '往期', '回顾', '历史', '时光机']

WX_URL = {
    "template": "{website}/static/{dir}/{target_name}",
    "review": "http://mp.weixin.qq.com/mp/homepage?__biz=MzI2NzY2NDk5Nw==&hid=1&sn=ad05690c560e92fe6794a5db478df49f#wechat_redirect",
    "pic": "http://mp.weixin.qq.com/s/XaraDbtQtBKOSkpJOoH_IA",
    "history": "https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MzI2NzY2NDk5Nw==&scene=124#wechat_redirect",
    "video": "http://mp.weixin.qq.com/s/3AIYYiiCUdt7pt4VRgz7NQ",
}

# HOST = ['instdd.com', 'www.instdd.com', '127.0.0.1:8001', 'www.owllook.la', 'owllook.la']

HOST = ['127.0.0.1:8001']

TIMEZONE = 'Asia/Shanghai'

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

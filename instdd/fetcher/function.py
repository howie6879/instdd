#!/usr/bin/env python
import arrow
import os
import PIL.Image as Image
from PIL import ImageDraw, ImageFont
from instdd.config import TIMEZONE, BASE_DIR, LOGGER

LOGO = BASE_DIR + "/static/images/logo.jpeg"
TEXT = {
    'zh': {
        "img_name": "图图推|",
        "img_pro": "在2016年共po图{post_nums}次，获得{all_likes}个喜欢 ^_^",
        "img_weibo": "#instagram年度热图",
        "img_footer": "专属于{username}的2016年度热图",
        "img_by": "@by 图图推 - instdd.com"
    }
}


def get_time() -> str:
    utc = arrow.utcnow()
    local = utc.to(TIMEZONE)
    time = local.format("YYYY-MM-DD HH:mm:ss")
    return time


def get_timestamp() -> int:
    """
    返回该时区时间戳
    :param timezone: 时区
    :return: 时间戳
    """
    utc = arrow.utcnow()
    local = utc.to(TIMEZONE).timestamp
    return int(local)


def get_best_nine_img(username, post_nums, all_likes, lang='zh'):
    _dir = BASE_DIR + "/static/ins_best/" + username + "_2016/"
    name = username + '_2016.jpg'
    if not os.path.exists(_dir + name):
        mw = 240
        ms = 3

        msize = mw * ms

        img_pre = username
        toImage = Image.new('RGBA', (msize, 850), 'white')

        try:
            for x in range(0, 3):
                for y in range(0, 3):
                    media_name = _dir + "/{pre}_{index}.jpg".format(
                        username=username,
                        pre=img_pre,
                        index=ms * x + y)
                    fromImage = Image.open(media_name)
                    fromImage = fromImage.resize((mw, mw), Image.ANTIALIAS)
                    toImage.paste(fromImage, (y * mw, 70 + x * mw))

            best_nine_name = _dir + username + '_2016.jpg'
            # 添加logo
            toImage.paste(Image.open(LOGO), (5, 5))
            # 添加文字水印
            draw = ImageDraw.Draw(toImage)
            my_font_01 = ImageFont.truetype(BASE_DIR + '/fetcher/wryh.ttf', size=18)

            if lang == 'zh':
                img_name = TEXT['zh']['img_name'] + username,
                img_pro = TEXT['zh']['img_pro'].format(
                    post_nums=post_nums,
                    all_likes=all_likes,
                )
                img_weibo = TEXT['zh']['img_weibo']
                img_footer = TEXT['zh']['img_footer'].format(username=username)
                img_by = TEXT['zh']['img_by']

            draw.text((65, 3), img_name[0], font=my_font_01, fill="#e46060")
            draw.text((65, 30), img_pro, font=my_font_01, fill="#777")
            draw.text((530, 3), img_weibo, font=my_font_01, fill="#041927")
            draw.text((8, 810), img_footer, font=my_font_01, fill="#041927")
            draw.text((500, 810), img_by, font=my_font_01, fill="#e46060")
            toImage.save(best_nine_name)
        except Exception as e:
            LOGGER.exception(e)
            name = ''
        return name
    else:
        return name

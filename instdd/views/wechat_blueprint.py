#!/usr/bin/env python
from sanic import Blueprint
from sanic.response import text, html, redirect
from sanic.exceptions import NotFound
from wechatpy import parse_message, create_reply
from wechatpy.utils import check_signature
from wechatpy.replies import ArticlesReply
from urllib.parse import urlparse
from jinja2 import Environment, PackageLoader, select_autoescape

from instdd.fetcher import InsDownload, InsBestNine
from instdd.fetcher.function import get_time, get_best_nine_img
from instdd.database.motorbase import MotorBase
from instdd.config import LOGGER, TOKEN, WX_URL, WX_WELCOME, WEBSITE, DEFAULT_IMG, WX_HELP, WX_RETURN_HELP, \
    WX_RETURN_REVIEW

wechat_bp = Blueprint('wechat_blueprint')

# jinjia2 config
env = Environment(
    loader=PackageLoader('views.wechat_blueprint', '../templates/wechat'),
    autoescape=select_autoescape(['html', 'xml', 'tpl']))


def template(tpl, **kwargs):
    template = env.get_template(tpl)
    return html(template.render(kwargs))


@wechat_bp.route('/instdd_wechat', methods=['POST', 'GET'])
async def instdd_wechat(request):
    LOGGER.info('hello')
    signature = request.args.get('signature', '')
    timestamp = request.args.get('timestamp', '')
    nonce = request.args.get('nonce', '')
    encrypt_type = request.args.get('encrypt_type', 'raw')
    msg_signature = request.args.get('msg_signature', '')
    try:
        check_signature(TOKEN, signature, timestamp, nonce)
    except Exception as e:
        LOGGER.exception(e)
        return NotFound
    if request.method == 'GET':
        echo_str = request.args.get('echostr', '')
        return text(echo_str)
    # POST request
    LOGGER.info(encrypt_type)
    if encrypt_type == 'raw':
        # 明文模式
        msg = parse_message(request.body)
        if msg.type == 'text':
            try:
                receive_text = msg.content
                print(receive_text)
                # 回复图片视频链接下载
                netloc = urlparse(receive_text).netloc
                if "instagram.com" in netloc:
                    is_down = await wechat_down_ins(receive_text)
                    if is_down:
                        reply = ArticlesReply(message=msg, articles=is_down['article'])
                    else:
                        reply_text = "下载失败，请确认链接是否正确^_^"
                        reply = create_reply(reply_text, msg)
                    return text(reply.render())
                # 回复帮助
                is_help = is_reply_help(receive_text)
                if is_help:
                    reply = create_reply(WX_HELP, msg)
                    return text(reply.render())
                # 回复历史文章
                is_review = is_reply_review(receive_text)
                if is_review:
                    reply = ArticlesReply(message=msg, articles=reply_review())
                    return text(reply.render())
                # 测试
                # if '宇哥' in receive_text:
                #     reply_text = str(msg.source)
                #     reply = create_reply(reply_text, msg)
                #     return text(reply.render())
                # 回复热图
                if receive_text.replace(' ', '').startswith('热图2016'):
                    username = receive_text.replace(' ', '').split('2016')[-1]
                    if username:
                        hot_2016 = await wechat_ins_best(username)
                        if hot_2016['status'] == 1:
                            reply = ArticlesReply(message=msg, articles=hot_2016['article'])
                        else:
                            reply_text = hot_2016['msg']
                            reply = create_reply(reply_text, msg)
                    else:
                        reply_text = "热图获取格式，热图2016用户名"
                        reply = create_reply(reply_text, msg)
                    return text(reply.render())
                # 回复热图下载帮助
                if "2016" in receive_text or '热图' in receive_text:
                    reply_text = "热图获取格式，热图2016用户名"
                    reply = create_reply(reply_text, msg)
                    return text(reply.render())
                # 回复下载帮助
                if "下载" in receive_text or '图片' in receive_text or '保存' in receive_text or "视频" in receive_text:
                    reply = ArticlesReply(message=msg, articles=reply_down())
                    return text(reply.render())
                # reply_text = '输入您想下载的图片或者视频链接就可以下载啦，单张下载不需要vpn哟'
                reply_text = ""
            except Exception as e:
                LOGGER.exception(e)
                reply_text = '哎哟，小糊涂出错了，请重试'
        elif msg.type == 'event':
            reply_text = WX_WELCOME
        else:
            reply_text = "^……^"
        reply = create_reply(reply_text, msg)
        return text(reply.render())


# 微信网页页面展示
@wechat_bp.route('/wechat_down')
async def wechat_down(request):
    url = request.args.get('url', None)
    if url:
        url = url.replace(WEBSITE, '')
        return template('wechat_down.html', title="图图推 - 最有爱图片公众号", img_url=url)
    else:
        return redirect('/')


@wechat_bp.route('/wechat_2016_ins_best')
async def wechat_2016_ins_best(request):
    username = request.args.get('username', None)
    post_nums = request.args.get('post_nums', None)
    all_likes = request.args.get('all_likes', None)
    if username and post_nums and all_likes:
        try:
            motor_db = MotorBase().db
            is_exist = await motor_db.best_nine_media.find_one({'data.username': username})
        except Exception as e:
            LOGGER.exception(e)
            is_exist = {}
        if is_exist:
            items = is_exist['data']
            source_urls = items['source_urls']
            post_nums = items['post_nums']
            all_likes = items['all_likes']
            best_nine_url = WEBSITE + '/static/ins_best/' + username + "_2016" + "/" + username + "_2016.jpg"
            return template(
                'wechat_2016_ins_best.html',
                title="图图推 - {user}的2016年度热图".format(user=username),
                source_urls=source_urls,
                post_nums=post_nums,
                all_likes=all_likes,
                best_nine_url=best_nine_url
            )
        else:
            return text('资源已经被删除，请在公众号重新下载，或者访问网页{website}'.format(website=WEBSITE))
    else:
        return redirect('/')


@wechat_bp.route('/wechat_down_video')
async def wechat_down_video(request):
    url = request.args.get('url', None)
    if url:
        return template('wechat_down_video.html', title="图图推 - 最有爱图片公众号", video_url=url)
    else:
        return redirect('/')


@wechat_bp.route('/wechat_all_media')
async def wechat_all_media(request):
    url = request.args.get('url', None)
    if url and "ig.com" in url:
        url = url.replace('ig.com', 'instagram.com')
        try:
            motor_db = MotorBase().db
            is_exist = await motor_db.media_mess.find_one({'data.media_link': url})
            if is_exist:
                media_data = is_exist['data']
                return template('wechat_all_media.html', title="图图推 - 最有爱图片公众号", pic_urls=media_data['pic_urls'],
                                video_urls=media_data['video_urls'])
            else:
                return text('url错误或者原资源已经被删除，您可以访问https://instdd.com进行下载')
        except Exception as e:
            LOGGER.exception(e)
            return redirect('/')
    else:
        return redirect('/')


################  功能函数  ####################



def reply_down():
    article = [
        {
            'title': "instagram下载图片教程 - 小糊涂",
            'description': "复制链接即可下载，具体点这里❤️笔芯",
            'url': WX_URL['pic'],
            'image': WX_URL['template'].format(
                website=WEBSITE,
                dir='images',
                target_name="dp01.jpeg")
        },
        {
            'title': 'instagram下载视频教程 - 小糊涂',
            'description': '复制链接即可下载，具体点这里❤️笔芯',
            'url': WX_URL['video'],
            'image': WX_URL['template'].format(
                website=WEBSITE,
                dir='images',
                target_name="dv01.jpeg")
        }
    ]
    return article


def reply_review():
    article = [
        {
            'title': "小糊涂的历史文章",
            'description': "所有好玩好看的文章都在这里啦，点这里❤️笔芯",
            'url': WX_URL['history'],
            'image': WX_URL['template'].format(
                website=WEBSITE,
                dir='images',
                target_name="review.jpeg")
        },
        {
            'title': "instagram下载图片教程 - 小糊涂",
            'description': "复制链接即可下载，具体点这里❤️笔芯",
            'url': WX_URL['pic'],
            'image': WX_URL['template'].format(
                website=WEBSITE,
                dir='images',
                target_name="dp01.jpeg")
        },
        {
            'title': 'instagram下载视频教程 - 小糊涂',
            'description': '复制链接即可下载，具体点这里❤️笔芯',
            'url': WX_URL['video'],
            'image': WX_URL['template'].format(
                website=WEBSITE,
                dir='images',
                target_name="dv01.jpeg")
        }
    ]
    return article


def is_reply_review(receive_text):
    for i in WX_RETURN_REVIEW:
        if i in receive_text:
            return True
    return False


def is_reply_help(receive_text):
    for i in WX_RETURN_HELP:
        if i == receive_text:
            return True
    return False


async def wechat_ins_best(username, year=2016):
    """
    返回生成的图片
    :param request: 
    :return: 1  成功 
             0  用户不存在或者私密账户
             -1 获取失败
             -2 网络原因
             -3 生成图片失败
    """
    try:
        try:
            motor_db = MotorBase().db
            is_exist = await motor_db.best_nine_media.find_one({'data.username': username})
        except Exception as e:
            LOGGER.exception(e)
            is_exist = {}
        ins_best = InsBestNine(dir='static/ins_best/' + username + "_" + str(year), user_name=username, year=year)
        best_nine_name = ''
        if is_exist:
            items = is_exist['data']
            source_urls = items['source_urls']
            post_nums = items['post_nums']
            all_likes = items['all_likes']
            # 下载前九张图
            urls = source_urls[:9] if len(source_urls) >= 9 else source_urls
            target_names = await ins_best.start(option='save_source', source_urls=urls)
            if target_names:
                best_nine_name = get_best_nine_img(username, post_nums, all_likes)
        else:
            items = await ins_best.start(option='get_best_nine')
            if items[0] is not None:
                items = items[0]
                post_nums = len(items)
                image_items, source_urls = [], []
                all_likes = 0
                for item in items:
                    # 所有喜欢数
                    all_likes += item['likes']
                    if item["type"] == "image":
                        # 获取本年份所有图片media
                        url = item['images']['low_resolution']['url']
                        if url:
                            image_items.append(item)
                            source_urls.append(url)
                # 下载前九张图
                urls = source_urls[:9] if len(source_urls) >= 9 else source_urls
                target_names = await ins_best.start(option='save_source', source_urls=urls)
                if target_names:
                    # 缓存进数据库
                    data = {
                        'username': username,
                        'items': items,
                        'post_nums': post_nums,
                        "all_likes": all_likes,
                        'source_urls': source_urls[:9],
                    }
                    await motor_db.best_nine_media.update_one(
                        {'data.username': username},
                        {'$set': {'data': data, "updated_at": get_time()}},
                        upsert=True)
                    # WEBSITE = "http://127.0.0.1:8001"
                    # target_urls = map(lambda i: urljoin(WEBSITE, i), target_names)
                    best_nine_name = get_best_nine_img(username, post_nums, all_likes)
                else:
                    # 可能是网络问题
                    data = {
                        'status': -2,
                        'msg': "可能是网络问题哟，请稍后再试^……^",
                    }
                    return data
            else:
                # 获取不到图片
                LOGGER.info('私密账户或者2016年没有po图')
                data = {
                    'status': 0,
                    'msg': "如果账号正确的话，那么这是私密账户或者2016年没有po图^……^",
                }
                return data

        if best_nine_name:
            article = [
                {
                    'title': "图图推|{username}的年度热图".format(username=username),
                    'description': "{username}在{year}年在ins共po图{post_nums}次，获得喜欢{all_likes}，快来关注图图推，获取你的年度热图吧".format(
                        username=username,
                        year=year,
                        post_nums=post_nums,
                        all_likes=all_likes),
                    'url': "{website}/wechat_{year}_ins_best?username={username}&post_nums={post_nums}&all_likes={all_likes}".format(
                        website=WEBSITE,
                        year=year,
                        username=username,
                        post_nums=post_nums,
                        all_likes=all_likes,
                    ),
                    'image': WEBSITE + '/static/ins_best/' + username + "_" + str(year) + "/" + best_nine_name
                }
            ]
            data = {
                'status': 1,
                'post_nums': post_nums,
                'all_likes': all_likes,
                'best_nine_name': '/static/ins_best/' + username + "_" + str(year) + "/" + best_nine_name,
                'article': article,
                'msg': 'ok',
            }
            return data
        else:
            LOGGER.info('图片发布少于九张')
            data = {
                'status': -3,
                'msg': "去年发布的图太少了^……^",
            }
            return data

    except Exception as e:
        LOGGER.exception(e)
        data = {
            'status': -1,
            'msg': "获取失败，请重试^_^",
        }
        return data


async def wechat_down_ins(url):
    ins = InsDownload('static/ins_photos', url)
    try:
        motor_db = MotorBase().db
        is_exist = await motor_db.media_mess.find_one({'data.media_link': url})

        # 定义原始抓取函数
        async def ini_start():
            """
            原始数据抓取函数
            :return: 返回数据字典
            """
            start_result = {}
            data = await ins.start(option="get_url")
            if data[0]:
                start_result = data[0]
                time = get_time()
                await motor_db.media_mess.update_one(
                    {'data.media_link': url},
                    {'$set': {'data': start_result, "updated_at": time}},
                    upsert=True)
            return start_result

        # 定义多图情况
        def media_group(media_data):
            media_link = media_data['media_link']
            page_url = WEBSITE + "/wechat_all_media?url=" + media_link.replace('instagram.com', 'ig.com')
            image = WEBSITE + DEFAULT_IMG
            description = "笔芯：该链接带有多张图片或视频，需要跨越长城，开启vpn吧，小糊涂带你飞^_^，若小宝贝需要下载某用户所有图片视频，请在后台召唤小糊涂❤️"
            result = {
                'is_group': True,
                'article': [
                    {
                        'title': "需要VPN|@by_{url}".format(url=media_link),
                        'description': description,
                        'url': page_url,
                        'image': image
                    }
                ]
            }
            return result

        try:
            if is_exist:
                path = urlparse(url).path
                # 当该链接是个人主页
                if '/p/' not in path:
                    start_result = await ini_start()
                    # 判断是否是多张图片
                    is_group = start_result.get('is_group', False)
                    if is_group:
                        return media_group(media_data=start_result)
                # 当数据库中存在该链接信息
                data = is_exist["data"]
                # 判断是否是多张图片
                is_group = data.get('is_group', False)
                if is_group:
                    return media_group(media_data=data)
                # 单张图片情况
                source_url = data["source_url"]
                target_name = await ins.start(option="save_source", source_url=source_url)
                # 获取media名称
                if target_name[0]:
                    target_name = target_name[0]
                # 获取失败后再次进行获取
                else:
                    start_result = await ini_start()
                    # 判断是否是多张图片
                    is_group = start_result.get('is_group', False)
                    if is_group:
                        return media_group(media_data=start_result)
                    target_name = start_result.get('target_name', '')
            else:
                # 数据库中不存在 重新获取
                start_result = await ini_start()
                # 判断是否是多张图片
                is_group = start_result.get('is_group', False)
                if is_group:
                    return media_group(media_data=start_result)
                target_name = start_result.get('target_name', '')
        except Exception as e:
            LOGGER.exception(e)
            # 抛出异常 重新获取
            start_result = await ini_start()
            # 判断是否是多张图片
            is_group = start_result.get('is_group', False)
            if is_group:
                return media_group(media_data=start_result)
            target_name = start_result.get('target_name', '')

        target_url = WX_URL['template'].format(
            website=WEBSITE,
            dir="ins_photos",
            target_name=target_name)
        if "mp4" in target_url:
            description = '小糊涂❤️笔芯：点击即可观看视频，建议安卓用户复制链接到手机任意浏览器即可下载，ios用户将网址复制到PC打开即可下载。'
            image = WEBSITE + DEFAULT_IMG
            page_url = WEBSITE + "/wechat_down_video?url=" + target_url
        else:
            description = '小糊涂❤️笔芯：点击进入，长按即可下载高清原图'
            image = target_url
            page_url = WEBSITE + "/wechat_down?url=" + target_url
        result = {
            'is_group': False,
            'article': [
                {
                    'title': "@by_{url}".format(url=url),
                    'description': description,
                    'url': page_url,
                    'image': image
                }
            ]
        }
        return result

    except Exception as e:
        LOGGER.exception(e)
        return False

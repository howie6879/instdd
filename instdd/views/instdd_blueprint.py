#!/usr/bin/env python
from sanic import Blueprint
from sanic.response import html, redirect, json
from jinja2 import Environment, PackageLoader, select_autoescape
from urllib.parse import urlparse, parse_qs
from pprint import pprint

from instdd.fetcher import InsDownload, InsBestNine
from instdd.database.motorbase import MotorBase
from instdd.fetcher.function import get_time, get_best_nine_img
from instdd.config import LOGGER, WEBSITE

instdd_bp = Blueprint('instdd_main')

# jinjia2 config
env = Environment(
    loader=PackageLoader('views.instdd_blueprint', '../templates/instdd_main'),
    autoescape=select_autoescape(['html', 'xml', 'tpl']))


def template(tpl, **kwargs):
    template = env.get_template(tpl)
    return html(template.render(kwargs))


@instdd_bp.route('/', methods=['GET'])
async def instdd_index(request):
    return template('en_index.html', title="Instagram photos and videos downloader online - instdd.com")
    # return template('index.html', title="Instagram - 图片保存 - 视频保存 - 在线下载 - instdd.com")


@instdd_bp.route('/2016', methods=['GET'])
async def instdd_2016(request):
    lang = request.args.get('l', '')
    if lang == "zh":
        return template('zh_2016.html', title="instdd - 你的ins年度热门图 - 2016 - instdd.com")
    else:
        return template('zh_2016.html', title="instdd - 你的ins年度热门图 - 2016 - instdd.com")


@instdd_bp.route('/ins_best', methods=['POST'])
async def instdd_ins_best(request):
    username = request.form.get('username', None)
    lang = request.form.get('lang', None)
    if username:
        if lang == "zh":
            tem = "zh_ins_best.html"
            title = username + " - 2016年度热图"
        else:
            tem = "en_ins_best.html"
            title = username + " - 2016年度热图"
        return template(tem, title=title, target_url='', username=username)
    else:
        redirect('/')


@instdd_bp.route('/ajax_ins_best', methods=['POST'])
async def instdd_ajax_ins_best(request):
    """
    返回生成的图片
    :param request: 
    :return: 1  成功 
             0  用户不存在或者私密账户
             -1 获取失败
             -2 网络原因
             -3 生成图片失败
    """
    post_data = parse_qs(str(request.body, encoding='utf-8'))
    username = post_data.get('username', [None])[0]
    year = 2016
    if username:
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
                    data = {
                        'status': -2,
                        'msg': "可能是网络问题哟，请稍后再试^……^",
                    }
                    return json(data)
            else:
                # 获取不到图片
                LOGGER.info('私密账户或者{year}年没有po图'.format(year=year))
                data = {
                    'status': 0,
                    'msg': "如果账号正确的话，那么这是私密账户或者{year}年没有po图^……^".format(year=year),
                }
                return json(data)
        if best_nine_name:
            data = {
                'status': 1,
                'post_nums': post_nums,
                'all_likes': all_likes,
                'best_nine_name': '/static/ins_best/' + username + "_" + str(year) + "/" + best_nine_name,
                'msg': 'ok',
            }
            return json(data)
        else:
            LOGGER.info('图片发布少于九张')
            data = {
                'status': -3,
                'msg': "去年发布的图太少了^……^",
            }
            return json(data)
    data = {
        'status': -1,
        'msg': "您输入的信息不对哟",
    }
    return json(data)


@instdd_bp.route('/home', methods=['GET'])
async def instdd_home(request):
    return template('index.html', title="Instagram - 图片保存 - 视频保存 - 在线下载 - instdd.com")
    # return template('home_photos.html', title="每日精美图片 - instagram图片精选 - 在线下载 - instdd.com")


@instdd_bp.route('/tututui', methods=['GET'])
async def instdd_tututui(request):
    return template('tututui.html', title="图图推 - 给你最有爱的服务 - 在线图片视频下载 - instdd.com")


@instdd_bp.route('/zh', methods=['GET'])
async def instdd_zh(request):
    return template('zh_index.html', title="Instagram - 图片保存 - 视频保存 - 在线下载 - instdd.com")


@instdd_bp.route('/en', methods=['GET'])
async def instdd_en(request):
    return template('en_index.html', title="Instagram photos and videos downloader online - instdd.com")


@instdd_bp.route('/photo', methods=['POST'])
async def instdd_photo(request):
    url = request.form.get('url', None)
    lang = request.form.get('lang', None)
    if url and 'instagram.com' in urlparse(url).netloc:
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

            # 处理多张图片情况
            def media_group(media_data):
                """
                处理多图情况
                :param media_data: 原始数据集
                :return: 返回html
                """
                # 判断中英文
                if lang == "zh":
                    tem = "zh_photo_group.html"
                    title = "Instagram - 图片保存 - 在线下载 - instdd.com"
                else:
                    tem = "en_photo_group.html"
                    title = "Instagram photo and video downloader online - instdd.com"
                return template(tem, title=title, pic_urls=media_data['pic_urls'],
                                video_urls=media_data['video_urls'])

            try:
                # 判断media是否存在
                if is_exist:
                    data = is_exist["data"]
                    path = urlparse(url).path
                    # 当该链接是个人主页
                    if '/p/' not in path:
                        start_result = await ini_start()
                        # 判断是否是多张图片
                        is_group = start_result.get('is_group', False)
                        if is_group:
                            return media_group(media_data=start_result)
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
                    start_result = await ini_start()
                    # 判断是否是多张图片
                    is_group = start_result.get('is_group', False)
                    if is_group:
                        return media_group(media_data=start_result)
                    target_name = start_result.get('target_name', '')
            except Exception as e:
                LOGGER.exception(e)
                start_result = await ini_start()
                # 判断是否是多张图片
                is_group = start_result.get('is_group', False)
                if is_group:
                    return media_group(media_data=start_result)
                target_name = start_result.get('target_name', '')
            target_url = ""
            if target_name:
                target_url = "static/ins_photos/{target_name}".format(target_name=target_name)
            is_img = False if 'mp4' in target_url else True
            # 判断中英文
            if lang == "zh":
                tem = "zh_photo.html"
                title = "Instagram - 图片保存 - 在线下载 - instdd.com"
            else:
                tem = "en_photo.html"
                title = "Instagram photo and video downloader online - instdd.com"
            return template(tem, title=title, target_url=target_url, is_img=is_img)
        except Exception as e:
            LOGGER.exception(e)
            return redirect('/')
    else:
        return redirect('/')


@instdd_bp.route('/faq', methods=['GET'])
async def instdd_faq(request):
    return template('faq.html', title="问答 - Instagram 保存图片 保存视频 - instdd.com")

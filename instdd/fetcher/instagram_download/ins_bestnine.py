#!/usr/bin/env python
import os
import async_timeout
import random
import asyncio
import aiohttp
import ujson
import re
import arrow
from operator import itemgetter

from pprint import pprint
from .config import USER_AGENT, PROXIES, LOGGER, BASE_DIR, TIMEZONE


class InsBestNine():
    """
    This async script can help you to download Instagram photos.
    """

    def __init__(self, dir, user_name, year=2016):
        self.user_name = user_name
        self.year = year
        self._dir = dir + "/"
        if not os.path.exists(self._dir):
            os.makedirs(self._dir)

    async def fetch(self, client, url) -> bytes:
        """
        fetch url
        :param client: aiohttp client
        :param url: request url
        :return: response.read()
        """
        with async_timeout.timeout(30):
            try:
                headers = {'user-agent': self.get_random_user_agent()}
                proxy = PROXIES if PROXIES else None
                async with client.get(url, headers=headers, proxy=proxy) as response:
                    assert response.status == 200
                    LOGGER.info('Task url: {}'.format(response.url))
                    text = await response.read()
                    return text
            except Exception as e:
                LOGGER.exception(e)
                return None

    async def get_media_urls(self):
        urls = []
        try:
            items = await self.get_media_info()
            for item in items:
                if item['type'] == 'carousel':
                    for carousel_item in item['carousel_media']:
                        url = carousel_item[carousel_item['type'] + 's']['standard_resolution']['url'].split('?')[0]
                        urls.append(self.get_original_image(url))
                else:
                    url = item[item['type'] + 's']['standard_resolution']['url'].split('?')[0]
                    urls.append(self.get_original_image(url))
        except Exception as e:
            LOGGER.exception(e)
        return urls

    async def get_best_nine(self):
        # 获取该年份所有media
        async def get_year_media_info(items=[], max_id=None):
            url = 'http://instagram.com/' + self.user_name + '/media' + (
                '?&max_id=' + max_id if max_id is not None else '')
            async with aiohttp.ClientSession(loop=None) as client:
                asyncio.sleep(2)
                try:
                    html = await self.fetch(client=client, url=url)
                    media = ujson.loads(html)
                except Exception as e:
                    LOGGER.exception(e)
                    asyncio.sleep(10)
                    html = await self.fetch(client=client, url=url)
                    media = ujson.loads(html)
                if not media['items']:
                    raise ValueError('User {0} is private'.format(self.user_name))
                max_time = media['items'][0]['created_time']
                min_time = media['items'][-1]['created_time']
                max_year = self.get_year(int(max_time))
                min_year = self.get_year(int(min_time))
                if max_year == self.year or min_year == self.year:
                    for current_item in media['items']:
                        item_data = {}
                        current_item['year'] = self.get_year(current_item['created_time'])
                        if current_item['year'] == self.year:
                            item_data['id'] = current_item['id']
                            item_data['type'] = current_item['type']
                            item_data['link'] = current_item['link']
                            if item_data['type'] == "carousel":
                                item_data['is_carousel'] = True
                                # list
                                item_data['carousel_media'] = current_item['carousel_media']
                            else:
                                item_data['is_carousel'] = False
                                # dict
                                item_data[current_item['type'] + 's'] = current_item[current_item['type'] + 's']
                            item_data['likes'] = current_item['likes'].get('count', 0)
                            item_data['comments'] = current_item['comments'].get('count', 0)
                            item_data['caption'] = current_item['caption']
                            item_data['year'] = self.year
                            items.append(item_data)
                    if 'more_available' not in media or media['more_available'] is False:
                        return items
                    else:
                        # 每个item的media个数为20
                        max_id = media['items'][-1]['id']
                        return await get_year_media_info(items, max_id)
                elif min_year < self.year:
                    return items
                else:
                    if 'more_available' not in media or media['more_available'] is False:
                        return items
                    else:
                        # 每个item的media个数为20
                        max_id = media['items'][-1]['id']
                        return await get_year_media_info(items, max_id)

        try:
            items = await get_year_media_info()
            if items:
                # 根据喜欢数进行排序 喜欢数相同就按照评论数目排序
                result_sorted = sorted(items, reverse=True, key=itemgetter('likes', 'comments'))
                return result_sorted
            else:
                return None
        except Exception as e:
            LOGGER.exception(e)
            return None

    async def get_media_info(self, items=[], max_id=None):
        """
        Fetches the user's media data
        :param items: 
        :param max_id: 
        :return: 
        """
        url = 'http://instagram.com/' + self.user_name + '/media' + (
            '?&max_id=' + max_id if max_id is not None else '')
        async with aiohttp.ClientSession(loop=None) as client:
            asyncio.sleep(1)
            html = await self.fetch(client=client, url=url)
            media = ujson.loads(html)
            if not media['items']:
                raise ValueError('User {0} is private'.format(self.user_name))
            items.extend([current_item for current_item in media['items']])
            if 'more_available' not in media or media['more_available'] is False:
                return items
            else:
                # 每个item的media个数为20
                max_id = media['items'][-1]['id']
                return await self.get_media_info(items, max_id)

    async def save_source(self, source_url, index):
        source_url = source_url.split('?')[0]
        # 拼接图片url
        target_name = self.user_name + '_' + str(index) + "." + source_url.split('.')[-1]
        if not os.path.exists(self._dir + target_name):
            async with aiohttp.ClientSession(loop=None) as client:
                target_result = await self.fetch(client=client, url=source_url)
                if target_result:
                    LOGGER.info("Downloading {source_url}".format(source_url=source_url))
                else:
                    asyncio.sleep(5)
                    target_result = await self.fetch(client=client, url=source_url)
                try:
                    with open(self._dir + target_name, 'wb') as file:
                        file.write(target_result)
                        LOGGER.info(
                            'File downloaded successfully at {dir}'.format(dir=self._dir + target_name))
                    return self._dir + target_name
                except Exception as e:
                    LOGGER.exception(e)
                    return False
        else:
            return self._dir + target_name

    def get_original_image(self, url):
        # remove dimensions to get largest image
        url = re.sub(r'/s\d{3,}x\d{3,}/', '/', url)
        # get non-square image if one exists
        url = re.sub(r'/c\d{1,}.\d{1,}.\d{1,}.\d{1,}/', '/', url)
        return url

    def get_random_user_agent(self) -> str:
        """
        Get a random user agent string.
        :return: Random user agent string.
        """
        try:
            with open(BASE_DIR + '/user_agents.txt') as fp:
                data = [_.strip() for _ in fp.readlines()]
        except:
            data = [USER_AGENT]
        return random.choice(data)

    def get_year(self, timestamp):
        year = arrow.get(timestamp).year
        return year

    async def start(self, option="get_best_nine", source_urls=None):
        """
        start crawling ins url
        :return:
        """
        if option == "get_best_nine":
            tasks = self.get_best_nine()
            return await asyncio.gather(tasks)
        if option == "save_source":
            tasks = [asyncio.ensure_future(self.save_source(source_url, index)) for index, source_url in
                     enumerate(source_urls)]
            return await asyncio.gather(*tasks)

    def test_start(self):
        """
        start crawling ins url
        :return:
        """
        loop = asyncio.get_event_loop()
        task = asyncio.ensure_future(self.get_best_nine())
        loop.run_until_complete(task)
        return task.result()

#!/usr/bin/env python
import os
import aiohttp
import async_timeout
import asyncio
import random
import re
from bs4 import BeautifulSoup
from pprint import pprint
from .config import USER_AGENT, PROXIES, LOGGER, BASE_DIR


class InsDownload():
    """
    This async script can help you to download Instagram photos.
    """

    def __init__(self, dir, single_url):
        self.single_url = single_url
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

    async def get_url(self, loop):
        """
        Get user photo's url
        :return: True or False
        """
        async with aiohttp.ClientSession(loop=None) as client:
            asyncio.sleep(1)
            html = await self.fetch(client=client, url=self.single_url)
            try:
                if html:
                    data = {}

                    # 获取用户id
                    html_soup = BeautifulSoup(html, 'lxml')
                    soup = html_soup.head
                    user_id = soup.select('meta[property="instapp:owner_user_id"]')
                    user_id = user_id[0].get('content', None) if user_id else None
                    if not user_id:
                        ins_id = re.findall(r'\"owner\":\s*\{\"id\":\s*\"(\d{1,})\"\}', str(html))
                        try:
                            user_id = ins_id[0]
                        except Exception as e:
                            LOGGER.exception(e)
                            user_id = None

                    # 获取用户描述以及media_id
                    target_des = soup.select('meta[property="og:description"]')
                    target_des = target_des[0].get('content', None) if target_des else None
                    media_id = soup.select('meta[property="al:ios:url"]')
                    media_id = media_id[0].get('content', None) if media_id else None

                    # 多张图片
                    is_group = re.findall(r'\"display_url\":\s*\"(.*?)\"', str(html)) or re.findall(
                        r'\"display_src\":\s*\"(.*?)\"', str(html))

                    if is_group and len(is_group) > 1:
                        video_group = re.findall(r'\"video_url\":\s*\"(.*?)\"', str(html))
                        data.update({
                            "user_id": user_id,
                            "media_link": self.single_url,
                            "media_id": media_id,
                            'pic_urls': list(set(is_group)),
                            "video_urls": list(set(video_group)),
                            'target_des': target_des,
                            "is_group": True,
                        })
                        return data
                    # 单张图片
                    file_type = soup.select('meta[property="og:type"]')
                    file_type = file_type[0].get('content', None) if file_type else None
                    if file_type:
                        if file_type == "video":
                            source_url = soup.select('meta[property="og:video"]')[0].get('content', None)
                        else:
                            source_url = soup.select('meta[property="og:image"]')[0].get('content', None)
                            source_url = self.get_original_image(source_url)
                        source_url = source_url or None
                        target_name = await self.save_source(source_url)
                        if target_name:
                            data.update({
                                "user_id": user_id,
                                "media_link": self.single_url,
                                "media_id": media_id,
                                "source_url": source_url,
                                'type': file_type,
                                'target_name': target_name,
                                'target_des': target_des,
                                'is_group': False,
                            })
                    return data
                else:
                    return False
            except Exception as e:
                LOGGER.exception(e)
                return False

    async def save_source(self, source_url):
        source_url = source_url.split('?')[0]
        target_name = source_url[-25:].replace('/', '-')
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
                    return target_name
                except Exception as e:
                    LOGGER.exception(e)
                    return False
        else:
            return target_name

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

    async def start(self, option="get_url", source_url=None):
        """
        start crawling ins url
        :return:
        """
        if option == "get_url":
            tasks = self.get_url(loop=None)
        if option == "save_source":
            tasks = self.save_source(source_url)
        return await asyncio.gather(tasks)

    def test_start(self):
        """
        start crawling ins url
        :return:
        """
        loop = asyncio.get_event_loop()
        task = asyncio.ensure_future(self.get_url(loop=loop))
        loop.run_until_complete(task)
        return task.result()

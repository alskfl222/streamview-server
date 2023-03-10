#!/usr/bin/env python
# coding: utf-8

import traceback
import time
from playwright.async_api import async_playwright


class Finder():
    def __init__(self):
        self.video_base_url = 'https://www.youtube.com/watch?v='
        self.search_base_url = 'https://www.youtube.com/results?search_query='
        self.initiated = False

    async def init(self):
        if not self.initiated:
            playwright = await async_playwright().start()
            browser = await playwright.chromium.launch()
            context = await browser.new_context()
            await context.route('**/*', lambda route: route.continue_())
            page = await context.new_page()
            self.playwright = playwright
            self.page = page
            self.initiated = True

    async def find_song(self, query):
        if not self.initiated:
            print('init Finder first!')
            return
        try:
            # print(f"{self.video_base_url}{query}")
            print("TRY ID URI")
            await self.page.goto(f"{self.video_base_url}{query}")

            retry = 0
            while retry < 3:
                time.sleep(1)
                title_el = self.page.locator(
                    'div#title h1 yt-formatted-string')
                title_count = await title_el.count()
                if title_count:
                    item_title_raw = await title_el.nth(0).text_content()
                    item_title = item_title_raw.split('/')[-1]
                    item_id = query
                    channel_info = self.page.locator(
                        "div#owner div#text-container.ytd-channel-name a")
                    channel = await channel_info.nth(0).text_content()
                    channel_id_raw = await channel_info.nth(0).get_attribute('href')
                    channel_id = channel_id_raw[1:] if channel_id_raw[0] == "@" else channel_id_raw.split(
                        '/')[-1]
                    item = {
                        "title": item_title,
                        "id": item_id,
                        "channel": channel,
                        "channel_id": channel_id,
                        "available": True,
                    }
                    return item
                retry += 1
            print("CANNOT FOUND BY ID")
            print("TRY SEARCH QUERY")
            await self.page.goto(f"{self.search_base_url}{query}")
            items_el = self.page.locator('div#contents > ytd-video-renderer')
            items_count = await items_el.count()
            if items_count:
                target_item = items_el.nth(0)
                item_title = await target_item.locator('a#video-title > yt-formatted-string').text_content()
                item_id_raw = await target_item.locator('a#video-title').get_attribute('href')
                item_id = item_id_raw.split("=")[-1]
                channel = await target_item.locator('div#channel-info div.ytd-channel-name a').text_content()
                channel_id_raw = await target_item.locator('div#channel-info div.ytd-channel-name a').get_attribute('href')
                channel_id = channel_id_raw[1:] if channel_id_raw[0] == "@" else channel_id_raw.split(
                    '/')[-1]
                item = {
                    "title": item_title,
                    "id": item_id,
                    "channel": channel,
                    "channel_id": channel_id,
                    "available": True,
                }
                return item
            else:
                print('error?')
                traceback.print_exc()
                return None
        except:
            print('check error!')
            traceback.print_exc()
            return None

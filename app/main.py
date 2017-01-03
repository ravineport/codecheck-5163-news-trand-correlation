#!/usr/bin/env python

import urllib.request, urllib.parse
import json
import asyncio
import aiohttp


end_point = "http://54.92.123.84/search?"
api_key = "869388c0968ae503614699f99e09d960f9ad3e12"
params = {
    "q": "",
    "wt": "json",
    "ackey": api_key
}


def parse_args(argv):
    keywords = argv[0][1:-1].replace('"', '').replace(', ', ',').split(',')
    start_date = argv[1]
    end_date = argv[2]
    return {'keywords': keywords, 'start_date': start_date, 'end_date': end_date}


def generate_url(keyword):
    '''
    keywordを含む記事を検索するAPIを生成
    '''
    params["q"] = "Body:" + str(keyword)
    return end_point + urllib.parse.urlencode(params)


async def get_response(keyword, url):
    '''
    keywordとそれに対応するAPIのURLを叩いて結果をいい感じのJSONにする
    '''
    response = await aiohttp.get(url)
    data = await response.text()
    json_data = json.loads(data)
    return json_data


def main(argv):
    print(parse_args(argv))

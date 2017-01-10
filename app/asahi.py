#!/usr/bin/env python

import urllib.request, urllib.parse
import json
import asyncio
import aiohttp
import datetime
import math

asahi_end_point = 'http://54.92.123.84/search?'
asahi_api_key = '869388c0968ae503614699f99e09d960f9ad3e12'


def str2date(date_str):
    '''
    date_str(string型，'2016-01-01')からdate型へ変換
    '''
    return datetime.date(*[int(a) for a in date_str.split('-')])


async def get_response_by_get(url):
    '''
    URLをGETで叩いて結果をJSONにして返す（非同期）
    '''
    async with aiohttp.get(url) as response:
        data = await response.text()
        json_data = json.loads(data)
        return json_data


class Asahi:

    def __init__(self, keyword, start_date_str=None, end_date_str=None):
        self.keyword = keyword
        self.api_params = {
            'q': "Body:" + keyword + " AND ReleaseDate:[" + start_date_str + " TO " + end_date_str + "]",
            'wt': 'json',
            'rows': '100',
            'ackey': asahi_api_key
        }
        # date_str(string型，'2016-01-01')からdate型へ変換
        self.start_date = str2date(start_date_str)
        self.end_date = str2date(end_date_str)

    def generate_asahi_url(self):
        '''
        keywordを含む記事を日付の範囲を指定して検索するAPIを生成
        '''
        return asahi_end_point + urllib.parse.urlencode(self.api_params)

    async def get_response_of_asahi(self):
        '''
        朝日新聞APIを叩いて，結果から週毎の記事の数のリストへ変換
        '''
        url = self.generate_asahi_url()
        res = await get_response_by_get(url)

        doc_num = int(res['response']['result']['numFound']) # 取得すべきdocの数
        # getted_doc_num = 0 # 取得できたdocの数
        # while  doc_num > 100: # 100以上見つかったとき残りを取りに行く処理
        #     getted_doc_num += 100
        #     self.api_params['start'] = getted_doc_num
        #     doc_num -= 100
        #     url2 = self.generate_asahi_url()
        #     res2 = await get_response_by_get(url2)
        #     res['response']['result']['doc'].extend(res2['response']['result']['doc'])

        return {'keyword': self.keyword, 'doc_num_per_week': self.parse_response2week_num_list(res)}

    def parse_response2week_num_list(self, res):
        '''
        レスポンス(json)から週毎の記事の数のリストへ変換
        '''
        # TODO
        # numFoundが100を超えていた場合の処理
        week_num_lst = self.init_week_num_lst()
        if res['response']['result']['numFound'] == '0':
            return week_num_lst

        docs = res['response']['result']['doc']
        for doc in docs:
            release_date = str2date(doc['ReleaseDate'])
            idx = self.date2week_num_index(self.start_date, release_date)
            if idx < len(week_num_lst):
                week_num_lst[idx] += 1
        return week_num_lst

    def init_week_num_lst(self):
        '''
        start_date ~ end_dateまでの週数個の要素を持つ0で初期化されたリスト(端数の日数は含まない)
        '''
        lst_size = math.floor((self.end_date - self.start_date).days / 7)
        return [0] * lst_size

    def date2week_num_index(self, start_date, date):
        '''
        dateを何週目かを表すインデックスに変換
        '''
        return math.floor((date - start_date).days / 7)

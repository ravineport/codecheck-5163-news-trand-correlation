#!/usr/bin/env python

import urllib.request, urllib.parse
import json
import asyncio
import aiohttp
import datetime
import numpy as np
import math


end_point = "http://54.92.123.84/search?"
api_key = "869388c0968ae503614699f99e09d960f9ad3e12"
params = {
    "q": "",
    "wt": "json",
    "rows": "100",
    "ackey": api_key
}


def parse_args(argv):
    keywords = argv[0][1:-1].replace('"', '').replace(', ', ',').split(',')
    start_date = argv[1]
    end_date = argv[2]
    return {'keywords': keywords, 'start_date': start_date, 'end_date': end_date}


def generate_url(keyword, start_date, end_date):
    '''
    keywordを含む記事を日付の範囲を指定して検索するAPIを生成
    '''
    params["q"] = "Body:" + keyword + " AND ReleaseDate:[" + start_date + " TO " + end_date + "]"
    return end_point + urllib.parse.urlencode(params)


async def get_response(url):
    '''
    keywordとそれに対応するAPIのURLを叩いて結果をJSONにして返す
    '''
    response = await aiohttp.get(url)
    data = await response.text()
    json_data = json.loads(data)
    return json_data


def parse_response2week_num_list(res, start_date, end_date):
    '''
    レスポンス(json)から週毎の記事の数のリストへ変換
    '''
    # TODO
    # numFoundが100を超えていた場合の処理
    docs = res['response']['result']['doc']
    print(res['response']['result']['numFound'])
    week_num_lst = init_week_num_lst(start_date, end_date)
    for doc in docs:
        release_date = str2date(doc['ReleaseDate'])
        idx = date2week_num_index(start_date, release_date)
        print(str(release_date) + ' ' + str(idx))
        week_num_lst[idx] += 1
    return week_num_lst


async def url2week_num_dict(url, start_date_str, end_date_str):
    res = await get_response(url)
    start_date = str2date(start_date_str)
    end_date = str2date(end_date_str)
    return parse_response2week_num_list(res, start_date, end_date)


def str2date(date_str):
    '''
    date_str(string型，'2016-01-01')からdate型へ変換
    '''
    return datetime.date(*[int(a) for a in date_str.split('-')])


def init_week_num_lst(start_date, end_date):
    '''
    start_date ~ end_dateまでの週数個の要素を持つ0で初期化されたリスト(端数の日数も含む)
    '''
    lst_size = math.ceil((end_date - start_date).days / 7)
    return [0] * lst_size


def date2week_num_index(start_date, date):
    '''
    dateを何週目かを表すインデックスに変換
    '''
    return math.floor((date - start_date).days / 7)


def pearson_correlation_coefficient(lst1, lst2):
    x = np.array(lst1)
    y = np.array(lst2)
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    xx = x - x_mean
    yy = y - y_mean
    numerator = np.sum(xx * yy)
    denominator = np.sqrt(np.sum(xx ** 2) * np.sum(yy ** 2))
    return numerator / denominator


def main(argv):
    args = parse_args(argv)
    urls = []

    for keyword in args['keywords']:
        url = generate_url(keyword, args['start_date'], args['end_date'])
        urls.append(url)

    futures = [url2week_num_dict(url, args['start_date'], args['end_date']) for url in urls]
    loop = asyncio.get_event_loop()
    tasks = loop.run_until_complete(asyncio.wait(futures))[0]

    results = [task.result()[:-1] for task in tasks]
    for i in results:
        print(i)

    print(pearson_correlation_coefficient(results[0], results[1]))


    # print(pearson_correlation_coefficient([2.8, 3.4, 3.6, 5.8, 7.0, 9.5, 10.2, 12.3, 13.2, 13.4],
    #                                       [0.6, 3.0, 0.4, 1.5, 15.0, 13.4, 7.6, 19.8, 18.3, 18.9]))

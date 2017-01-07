#!/usr/bin/env python

import urllib.request, urllib.parse
import json
import asyncio
import aiohttp
import datetime
import numpy as np


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
    week_num_dict = init_week_num_dict(convert_str2date(start_date), convert_str2date(end_date))
    for doc in docs:
        release_date = doc['ReleaseDate']
        week_num_dict[convert_str2date(release_date).isocalendar()[:-1]] += 1
    return week_num_dict2lst(week_num_dict)


async def url2week_num_dict(url, start_date, end_date):
    res = await get_response(url)
    return parse_response2week_num_list(res, start_date, end_date)


def convert_str2date(date_str):
    '''
    date_str(string型，'2016-01-01')からdate型へ変換
    '''
    return datetime.date(*[int(a) for a in date_str.split('-')])


def week_num_dict2lst(week_num_dict):
    sored_dict = sorted(week_num_dict.items(), key=lambda x: x[0])
    return [d[1] for d in sored_dict]


def init_week_num_dict(start_date, end_date):
    '''
    (年, 週番号)をkeyとするdictionaryを生成
    valueはすべて0
    '''
    start_week_num_tpl = start_date.isocalendar()[:-1]
    end_week_num_tpl = end_date.isocalendar()[:-1]

    week_num_dict = {}
    key_year = start_week_num_tpl[0]
    key_week_num = start_week_num_tpl[1]

    # 週番号を1ずつ増やしてkeyとして，valueを0に初期化する処理
    # 週番号が52になったとき，次の年の1週目に行くか，53週目があるのかを判定
    while((key_year, key_week_num) != end_week_num_tpl):
        week_num_dict[(key_year, key_week_num)] = 0
        if key_week_num == 53 or \
            (key_week_num == 52 and datetime.date(key_year, 12, 31).isocalendar()[1] != 53):
            key_year += 1
            key_week_num = 1
            continue

        key_week_num += 1
    week_num_dict[end_week_num_tpl] = 0
    return week_num_dict


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

    results = [task.result() for task in tasks]

    print(pearson_correlation_coefficient(results[0], results[1]))


    # print(pearson_correlation_coefficient([2.8, 3.4, 3.6, 5.8, 7.0, 9.5, 10.2, 12.3, 13.2, 13.4],
    #                                       [0.6, 3.0, 0.4, 1.5, 15.0, 13.4, 7.6, 19.8, 18.3, 18.9]))

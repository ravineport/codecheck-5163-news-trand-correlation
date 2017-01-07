#!/usr/bin/env python

import urllib.request, urllib.parse
import json
import asyncio
import aiohttp
import datetime
import numpy as np
import math
import itertools

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
    if res['response']['result']['numFound'] == '0':
        return init_week_num_lst(start_date, end_date)

    docs = res['response']['result']['doc']
    week_num_lst = init_week_num_lst(start_date, end_date)
    for doc in docs:
        release_date = str2date(doc['ReleaseDate'])
        idx = date2week_num_index(start_date, release_date)
        if idx < len(week_num_lst):
            week_num_lst[idx] += 1
    return week_num_lst


async def url2week_num_dict(keyword, url, start_date_str, end_date_str):
    res = await get_response(url)
    start_date = str2date(start_date_str)
    end_date = str2date(end_date_str)
    return {'keyword': keyword, 'doc_num_per_week': parse_response2week_num_list(res, start_date, end_date)}


def str2date(date_str):
    '''
    date_str(string型，'2016-01-01')からdate型へ変換
    '''
    return datetime.date(*[int(a) for a in date_str.split('-')])


def init_week_num_lst(start_date, end_date):
    '''
    start_date ~ end_dateまでの週数個の要素を持つ0で初期化されたリスト(端数の日数は含まない)
    '''
    lst_size = math.floor((end_date - start_date).days / 7)
    return [0] * lst_size


def date2week_num_index(start_date, date):
    '''
    dateを何週目かを表すインデックスに変換
    '''
    return math.floor((date - start_date).days / 7)


def pearson_correlation_coefficient(lst1, lst2):
    if all([x == 0 for x in lst1]) or all([x == 0 for x in lst2]):
        return None
    x = np.array(lst1)
    y = np.array(lst2)
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    xx = x - x_mean
    yy = y - y_mean
    numerator = np.sum(xx * yy)
    denominator = np.sqrt(np.sum(xx ** 2) * np.sum(yy ** 2))
    return numerator / denominator


def calc_all_combinations(keywords, results):
    combinations = []
    for comb in itertools.combinations(keywords, 2):
        week_num_lsts = list(map(lambda x: x['doc_num_per_week'], filter(lambda r: r['keyword'] in comb, results)))
        pcc = pearson_correlation_coefficient(*week_num_lsts)
        if pcc != None:
            pcc = float(str(round(pcc, 3)))
        combinations.append({'comb': comb, 'correlation_coefficient': pcc})
    return combinations


def print_result(keywords, cc_result):
    cc_mat = np.diag([1] * len(keywords)).tolist()
    cc_result.reverse()

    for i in range(0, len(keywords)):
        for j in range(i+1, len(keywords)):
            cc_mat[i][j] = cc_result.pop()['correlation_coefficient']

    for i in range(0, len(keywords)):
        for j in range(i+1, len(keywords)):
            cc_mat[j][i] = cc_mat[i][j]

    # print(json.dumps({"coefficients": cc_mat, "posChecker": True}))
    print_for_test({"coefficients": cc_mat, "posChecker": True})


def print_for_test(ans):
    '''
    ans(Dict型)をテストで求められる形式に変換
    '''
    coefficients = '['
    for lst in ans['coefficients']:
        lst_str = '['
        for e in lst:
            if e != None:
                lst_str += str(e)
            else:
                lst_str += 'null'
            lst_str += ','
        lst_str = lst_str[:-1] + ']'
        coefficients += lst_str + ','
    coefficients = coefficients[:-1] + ']'

    posChecker = 'true' if ans['posChecker'] == True else 'false'

    print("{\"coefficients\":" + coefficients + ",\"posChecker\":" + posChecker + "}")


def main(argv):
    args = parse_args(argv)
    keyword_and_urls = []

    for keyword in args['keywords']:
        url = generate_url(keyword, args['start_date'], args['end_date'])
        keyword_and_urls.append({'keyword': keyword, 'url': url})

    futures = [url2week_num_dict(k_and_u['keyword'], k_and_u['url'], args['start_date'], args['end_date']) for k_and_u in keyword_and_urls]
    loop = asyncio.get_event_loop()
    tasks = loop.run_until_complete(asyncio.wait(futures))[0]

    results = [task.result() for task in tasks]
    cac = calc_all_combinations(args['keywords'], results)
    print_result(args['keywords'], cac)

    # print(pearson_correlation_coefficient(results[0]['doc_num_per_week'], results[1]['doc_num_per_week']))


    # print(pearson_correlation_coefficient([2.8, 3.4, 3.6, 5.8, 7.0, 9.5, 10.2, 12.3, 13.2, 13.4],
    #                                       [0.6, 3.0, 0.4, 1.5, 15.0, 13.4, 7.6, 19.8, 18.3, 18.9]))

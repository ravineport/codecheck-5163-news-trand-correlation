#!/usr/bin/env python

import urllib.request, urllib.parse
import json
import asyncio
import aiohttp
import datetime
import numpy as np
import math
import itertools
import os
from .parts_of_speech import PartsOfSpeech

asahi_end_point = 'http://54.92.123.84/search?'
asahi_api_key = '869388c0968ae503614699f99e09d960f9ad3e12'

goo_morph_end_point = 'https://labs.goo.ne.jp/api/morph'
goo_morph_api_key = os.environ['GOO_MORPH_API_KEY']


###
# Utility
###
def flatten_with_any_depth(nested_list):
    '''
    入れ子のリストをフラットにする関数
    '''
    flat_list = []
    fringe = [nested_list]

    while len(fringe) > 0:
        node = fringe.pop(0)
        if isinstance(node, list):
            fringe = node + fringe
        else:
            flat_list.append(node)

    return flat_list


def parse_args(argv):
    '''
    入力をいい感じにパース
    '''
    keywords = argv[0][1:-1].replace('"', '').replace(', ', ',').split(',')
    start_date = argv[1]
    end_date = argv[2]
    return {'keywords': keywords, 'start_date': start_date, 'end_date': end_date}


async def get_response_by_get(url):
    '''
    URLをGETで叩いて結果をJSONにして返す（非同期）
    '''
    async with aiohttp.get(url) as response:
        data = await response.text()
        json_data = json.loads(data)
        return json_data


def str2date(date_str):
    '''
    date_str(string型，'2016-01-01')からdate型へ変換
    '''
    return datetime.date(*[int(a) for a in date_str.split('-')])


###
# 朝日新聞APIと相関係数の計算
###
def generate_asahi_url(keyword, start_date, end_date):
    '''
    keywordを含む記事を日付の範囲を指定して検索するAPIを生成
    '''
    asahi_params = {
        'q': "Body:" + keyword + " AND ReleaseDate:[" + start_date + " TO " + end_date + "]",
        'wt': 'json',
        'rows': '100',
        'ackey': asahi_api_key
    }
    return asahi_end_point + urllib.parse.urlencode(asahi_params)


async def get_response_of_asahi(keyword, url, start_date_str, end_date_str):
    '''
    朝日新聞APIを叩いて，結果から週毎の記事の数のリストへ変換
    '''
    res = await get_response_by_get(url)
    start_date = str2date(start_date_str)
    end_date = str2date(end_date_str)
    return {'keyword': keyword, 'doc_num_per_week': parse_response2week_num_list(res, start_date, end_date)}


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
    '''
    ピアソンの積相関係数を計算
    '''
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


def calc_all_combinations(keywords, asahi_results):
    '''
    すべてのkeyword間で相関係数を計算
    '''
    combinations = []
    for comb in itertools.combinations(keywords, 2):
        week_num_lsts = list(map(lambda x: x['doc_num_per_week'], filter(lambda r: r['keyword'] in comb, asahi_results)))
        pcc = pearson_correlation_coefficient(*week_num_lsts)
        if pcc != None:
            pcc = float(str(round(pcc, 3)))
        combinations.append({'comb': comb, 'correlation_coefficient': pcc})
    return combinations


###
# goo 形態素解析API
###
async def get_response_of_goo_morph(keyword):
    '''
    gooの形態素解析APIをPOSTで叩いて結果をJSONにして返す（非同期）
    '''
    goo_morph_data = {
        'app_id': goo_morph_api_key,
        'sentence': keyword,
        'info_filter': 'pos'
    }
    async with aiohttp.post(goo_morph_end_point, data=goo_morph_data) as response:
        data = await response.text()
        json_data = json.loads(data)
        return json_data


def parse_goo_response(res):
    '''
    goo 形態素解析APIの結果から必要な部分を整形して返す
    '''
    return flatten_with_any_depth(res['word_list'])


def check_pos(responses):
    '''
    goo 形態素解析APIの結果からすべてのkeywordの品詞が一致しているかを計算
    '''
    results = [PartsOfSpeech.parts_of_speech(parse_goo_response(res)) for res in responses]
    if -1 in results:
        return False
    return all([e == results[0] for e in results[1:]])


###
# 結果出力まわり
###
def print_result(keywords, cc_result, pos_result):
    '''
    結果をJSONにして出力
    '''
    cc_mat = np.diag([1] * len(keywords)).tolist()
    cc_result.reverse()

    for i in range(0, len(keywords)):
        for j in range(i+1, len(keywords)):
            cc_mat[i][j] = cc_result.pop()['correlation_coefficient']

    for i in range(0, len(keywords)):
        for j in range(i+1, len(keywords)):
            cc_mat[j][i] = cc_mat[i][j]

    print_for_test({'coefficients': cc_mat, 'posChecker': pos_result})


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

    asahi_futures = []
    morph_futures = []
    for keyword in args['keywords']:
        url = generate_asahi_url(keyword, args['start_date'], args['end_date'])
        asahi_futures.append(get_response_of_asahi(keyword, url, args['start_date'], args['end_date']))
        morph_futures.append(get_response_of_goo_morph(keyword))

    asahi_loop = asyncio.get_event_loop()
    asahi_tasks = asahi_loop.run_until_complete(asyncio.wait(asahi_futures))[0]
    asahi_results = [task.result() for task in asahi_tasks]
    cac = calc_all_combinations(args['keywords'], asahi_results)

    morph_loop = asyncio.get_event_loop()
    morph_tasks = morph_loop.run_until_complete(asyncio.wait(morph_futures))[0]
    morph_results = [task.result() for task in morph_tasks]
    pos_result = check_pos(morph_results)

    print_result(args['keywords'], cac, pos_result)

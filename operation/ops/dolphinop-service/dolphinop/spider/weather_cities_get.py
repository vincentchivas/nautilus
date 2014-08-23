# -*- coding:UTF-8 -*-
'''
Created on Dec 25, 2013

@author: qhuang
'''
import urllib2
import logging
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'dolphinop.settings'
from django.utils import simplejson
from datetime import datetime
from dolphinop.service.models import weathers
from dolphinop.spider.weather import _request_url, _crawl_city_weather, _RETRY, _TIME_OUT
from dolphinop.spider.pm import PM_URL, crawl_pm

MAIN_AREA_URL = 'http://www.weather.com.cn/data/city3jdata/provshi/%s.html'
DETAIL_AREA_URL = 'http://www.weather.com.cn/data/city3jdata/station/%s%s.html'
PROVIN_INFO = [
    {"name": "北京", "id": "10101"}, {"name": "上海", "id": "10102"}, {"name": "天津",
                                                                   "id": "10103"}, {"name": "重庆", "id": "10104"}, {"name": "黑龙江", "id": "10105"},
    {"name": "吉林", "id": "10106"}, {"name": "辽宁", "id": "10107"}, {"name": "内蒙古",
                                                                   "id": "10108"}, {"name": "河北", "id": "10109"}, {"name": "山西", "id": "10110"},
    {"name": "陕西", "id": "10111"}, {"name": "山东", "id": "10112"}, {"name": "新疆",
                                                                   "id": "10113"}, {"name": "西藏", "id": "10114"}, {"name": "青海", "id": "10115"},
    {"name": "甘肃", "id": "10116"}, {"name": "宁夏", "id": "10117"}, {"name": "河南",
                                                                   "id": "10118"}, {"name": "江苏", "id": "10119"}, {"name": "湖北", "id": "10120"},
    {"name": "浙江", "id": "10121"}, {"name": "安徽", "id": "10122"}, {"name": "福建",
                                                                   "id": "10123"}, {"name": "江西", "id": "10124"}, {"name": "湖南", "id": "10125"},
    {"name": "贵州", "id": "10126"}, {"name": "四川", "id": "10127"}, {"name": "广东",
                                                                   "id": "10128"}, {"name": "云南", "id": "10129"}, {"name": "广西", "id": "10130"},
    {"name": "海南", "id": "10131"}, {"name": "香港", "id": "10132"}, {"name": "澳门", "id": "10133"}, {"name": "台湾", "id": "10134"}]
DELETE_CITY = [{'id': '101200905'}, {'id': '101300607'}]
WRONG_ID_CITY = [{'cityName': u'金山', 'id': '101020700'},
                 {'cityName': u'万州', 'id': '101041300'}, {'cityName': u'松江', 'id': '101020900'}]
WRONG_SPE_CITY = [{'cityName': u'朝阳', 'province': u'北京', 'id': '101010300'},
                  {'cityName': u'通州', 'province': u'北京', 'id': '101010600'}]
REPEAT_EN_CITY = [{'id': '101191201', 'city_en': 'taizhoushi'},
                  {'id': '101010300', 'city_en': 'chaoyangqu'}]
NEW_NAME_CITY = [
    {'cityName': '浦东南汇', 'id': '101020600'}, {'cityName': '札囊',
                                              'id': '101140303'}, {'cityName': '庆阳', 'id': '101160401'},
    {'cityName': '黄山', 'id': '101221001'}, {'cityName': '南沙', 'id': '101310220'}]
logger = logging.getLogger('dolphinop.service')
_db = weathers._db


def del_invalid__cities():
    id_lists = ['101090919', '101140215', '101160402', '101181504']
    if _db.weathers.find_one():
        for item in id_lists:
            _db.weathers.remove({'id': item})


def get_all_cities():
    prov_info = PROVIN_INFO
    other = []
    suc_cities = []
    timestamp = 1000000000000
    if prov_info:
        try:
            for item in prov_info:
                main_url = MAIN_AREA_URL % item['id']
                try:
                    res = _request_url(main_url)
                    stations = simplejson.loads(res)
                except Exception:
                    continue
                for key_s in stations:
                    sta_url = DETAIL_AREA_URL % (item['id'], key_s)
                    try:
                        src = _request_url(sta_url)
                        details = simplejson.loads(src)
                    except Exception:
                        continue
                    for key_d, value in details.items():
                        if key_d == '101081108' or key_d == '101201406' or item['id'] + key_s == '1013101':
                            city_id = key_d
                        elif item['id'] == '10101' or item['id'] == '10102' or item['id'] == '10103' or item['id'] == '10104':
                            city_id = item['id'] + key_d + key_s
                        else:
                            city_id = item['id'] + key_s + key_d
                        cityName = value
                        suc_cities.append(
                            {'id': city_id, 'cityName': cityName, 'pubDate': timestamp, 'province': item['name']})
                        if len(city_id) != 9:
                            other.append(cityName)
        except Exception, e:
            logger.exception(e)
            return None
    for item in other:
        print item
    for index, item in enumerate(suc_cities):
        for del_item in DELETE_CITY:
            if item['id'] == del_item['id']:
                del suc_cities[index]
                continue
        for errId_item in WRONG_ID_CITY:
            if item['cityName'] == errId_item['cityName']:
                suc_cities[index]['id'] = errId_item['id']
                continue
        for spe_item in WRONG_SPE_CITY:
            if item['cityName'] == spe_item['cityName'] and item['province'] == spe_item['province'].encode('utf-8'):
                suc_cities[index]['id'] = spe_item['id']
                continue
        for new_item in NEW_NAME_CITY:
            if item['id'] == new_item['id']:
                suc_cities[index]['cityName'] = new_item['cityName']
    sums = 0
    for index, item in enumerate(suc_cities):
        city_weather = _crawl_city_weather(item['id'])
        for re_item in REPEAT_EN_CITY:
            if re_item['id'] == item['id']:
                city_weather['city_en'] = re_item['city_en']
        suc_cities[index]['city_en'] = city_weather['city_en']
        weathers.update('weathers', {'id': item['id']}, {'cityName': item['cityName'], 'province': item[
                        'province'], 'pubDate': item['pubDate'], 'city_en': city_weather['city_en']}, True)
        del item['province']
        _db.cityInfos.save(item)
        sums += 1
        print 'sum is', sums


def update_pm_cities():
    logger.info('update cities which have pm data start')
    cities = weathers.get_cities()
    store = []
    for item in cities:
        url = PM_URL % item['city_en']
        pm_info = crawl_pm(url)
        if pm_info and 'AQI' in pm_info:
            if pm_info['CityName'] == item['cityName']:
                store.append(item['id'])
                print item['id']
                weathers.update('cityInfos',
                                {'id': item['id']}, {'aqi': True}, True)
                weathers.update(
                    'weathers', {'id': item['id']}, {'aqi': True}, True)
    weathers_cities = weathers.get_weathers_cities({'aqi': True})
    if weathers_cities:
        for we_city in weathers_cities:
            if we_city['id'] not in store:
                weathers.update(
                    'weathers', {'id': we_city['id']}, {'aqi': False})
                weathers.update('cityInfos',
                                {'id': we_city['id']}, {'aqi': False})
    stop_cities = weathers.get_weathers_cities({'aqi': False})
    if stop_cities:
        for st_city in stop_cities:
            _db.weathers.update(
                {'id': st_city['id']}, {'$unset': {'pm2d5': 1}})
    logger.info('update cities which have pm data finished')

if __name__ == '__main__':
    del_invalid__cities()
    get_all_cities()
    update_pm_cities()

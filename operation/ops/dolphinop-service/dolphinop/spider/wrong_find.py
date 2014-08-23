# -*- coding:UTF-8 -*-
'''
Created on Dec 27, 2013

@author: qhuang
'''
import time
import datetime
from dolphinop.utils import datetime2timestamp
from dolphinop.service.models import weathers
from dolphinop.utils import report

DAYS = 3
TIME_GAP = DAYS * 24 * 60 * 60 * 1000
WEATHER_WARN_COUNT = 20
PM_WARN_COUNT = 10


def weather_cities_check():
    basis = datetime2timestamp(datetime.datetime.now())
    cur = weathers._db.cityInfos.find(
        {'weather_update': False}, {'id': 1, 'cityName': 1, 'pubDate': 1})
    city_list = [i for i in cur]
    stall = []
    if city_list:
        for city in city_list:
            if basis - city['pubDate'] > TIME_GAP:
                stall.append(
                    {'id': city['id'], 'cityName': city['cityName'], 'pubDate': city['pubDate']})
    if len(stall) > WEATHER_WARN_COUNT:
        message = u'wrong cities about weather have been too much! <br><br>'
        for item in stall:
            message += "%s %s %s <br>" % (item['id'],
                                          item['cityName'], get_time(item['pubDate']))
        report(message)


def pm_cities_check():
    basis = datetime.datetime.now()
    cities = weathers.get_cities({'aqi': True})
    stall = []
    if cities:
        for city in cities:
            if 'pm_time' in city:
                update_time = datetime.datetime.strptime(
                    city['pm_time'], '%Y-%m-%d %H:%M')
                if basis - update_time > datetime.timedelta(DAYS):
                    stall.append(
                        {'id': city['id'], 'cityName': city['cityName'], 'pm_time': city['pm_time']})
    if len(stall) > PM_WARN_COUNT:
        mes = u'wrong cities about pm have been too much! <br><br>'
        for item in stall:
            mes += "%s %s %s <br>" % (item['id'],
                                      item['cityName'], item['pm_time'])
        report(mes)
    if weathers._db.cityInfos.find_one({'pm_workstate': False}):
        mes = u'the pm2.5 api had stopped working!'
        report(mes)


def get_time(value):
    format = '%Y-%m-%d'
    value = time.localtime(value / 1000)
    dt = time.strftime(format, value)
    return dt

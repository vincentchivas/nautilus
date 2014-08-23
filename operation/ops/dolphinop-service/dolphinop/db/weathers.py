'''
Created on Mar 5, 2013

@author: fli
'''
import logging
from pymongo import DESCENDING, ASCENDING
from dolphinop.db import cursor_to_array

logger = logging.getLogger('dolphinop.db')

_db = None

_INDEXES = {
    'cityInfos': [
        'id',
    ],
    'weathers': [
        [('cityName', DESCENDING), ('pubDate', DESCENDING)]
    ],
    'weathers': [
        'id',
    ],
}

WEATHER_FIELDS = {
    '_id': 0,
    'cityName': 1,
    'temLow': 1,
    'temHigh': 1,
    'temNow': 1,
    'pubDate': 1,
    'state': 1,
    'windState': 1,
    'windPower': 1,
    'windDir': 1,
    'humidity': 1,
    'pm2d5': 1,
    'future': 1,
}

CITY_FIELDS = {
    '_id': 0,
    'id': 1,
    'cityName': 1,
    'city_en': 1,
    'pubDate': 1,
    'pm_time': 1,
    'province': 1,
}

DISPLAY_FIELDS = {
    '_id': 0,
    'state': 1,
    'cityName': 1,
    'des': 1,
    'icon': 1,
    'bg': 1,
    'begin': 1,
    'end': 1,
}

_CITY_ORDER = [('id', ASCENDING)]
_WEATHER_ORDER = [('pubDate', DESCENDING)]
CITY_DIC = {'id': {'$exists': True}}


def get_weather(cond):
    colls = _db.weathers.find(cond, fields=WEATHER_FIELDS, sort=_WEATHER_ORDER)
    return cursor_to_array(colls)


def get_weather_display(cond):
    return _db.weather_display.find_one(cond, fields=DISPLAY_FIELDS)


def get_weather_displays(cond):
    colls = _db.weather_display.find(cond, fields=DISPLAY_FIELDS)
    return cursor_to_array(colls)


def get_cities(cond=CITY_DIC):
    cur = _db.cityInfos.find(cond, fields=CITY_FIELDS, sort=_CITY_ORDER)
    return cursor_to_array(cur)


def get_weathers_cities(cond={}):
    cur = _db.weathers.find(cond, fields=CITY_FIELDS, sort=_CITY_ORDER)
    return cursor_to_array(cur)


def update(table, cond, data, upsert=False):
    update = {'$set': data}
    eval('_db.%s.update' % table)(cond, update, upsert)

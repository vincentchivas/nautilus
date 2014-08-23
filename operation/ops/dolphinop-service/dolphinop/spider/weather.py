# -*- coding:UTF-8 -*-
'''
Created on Mar 5, 2013

@author: fli
'''
import urllib2
import logging
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'dolphinop.settings'
from django.utils import simplejson
from datetime import datetime
from dolphinop.utils import datetime2timestamp
from dolphinop.service.models import weathers

logger = logging.getLogger('dolphinop.service')


#_WEATHER_URL = 'http://m.weather.com.cn/data/%s.html'
_WEATHER_URL = 'http://www.weather.com.cn/data/cityinfo/%s.html'
_WEATHER_URL_INSTANT = 'http://www.weather.com.cn/data/sk/%s.html'
_RETRY = 3
_TIME_OUT = 30


def update_cities_weather():
    logger.info('update cities weather start')
    for city in weathers.get_cities():
        city_weather = _crawl_city_weather(city['id'])
        if city_weather:
            if city_weather['pubDate'] > city['pubDate']:
                city_weather['last_modified'] = datetime.now()
                weathers.update(
                    'weathers', {'id': city['id']}, city_weather, True)
                weathers.update('cityInfos', {'id': city['id']}, {'pubDate': city_weather[
                                'pubDate'], 'weather_update': True}, True)
                continue
        weathers.update('cityInfos',
                        {'id': city['id']}, {'weather_update': False}, True)
    logger.info('update cities weather done')


def _generate_pub_date(time_str):
    base = datetime.now()
    try:
        items = time_str.split(':')
        time_hour = int(items[0])
        time_minute = int(items[1])
        if base.hour < time_hour:
            base = base.replace(day=base.day - 1, hour=time_hour,
                                minute=time_minute, second=0, microsecond=0)
        else:
            base = base.replace(
                hour=time_hour, minute=time_minute, second=0, microsecond=0)
    except:
        pass
    return datetime2timestamp(base)


def _request_url(url):
    retry = 0
    f = None
    while retry < _RETRY and f is None:
        try:
            f = urllib2.urlopen(url, timeout=_TIME_OUT)
        except urllib2.URLError:
            retry += 1
    if f is None or f.url != url:
        logger.warn("[Weather Spider] Failed to crawl url %s with %d retry." %
                    (url, retry))
    else:
        return f.read()

def _tempstr2int(temp_str):
    try:
        return temp_str.replace(u'\u2103','')
    except:
        return None

def _crawl_city_weather(cityid):
    try:
        url = _WEATHER_URL % cityid
        content = _request_url(url)
        instant_url = _WEATHER_URL_INSTANT % cityid
        instant_content = _request_url(instant_url)
        weather = simplejson.loads(content)['weatherinfo']
        instant_weather = simplejson.loads(instant_content)['weatherinfo']
        weather_info = {
            #'city_en': weather['city_en'],
            'state': weather['weather'],
            'temNow': instant_weather['temp'],
            'pubDate': _generate_pub_date(instant_weather['time']),
            'windDir': instant_weather['WD'],
            'windState': instant_weather['WS'],
            'windPower': instant_weather['WS'],
            'humidity': instant_weather['SD'],
        }
        tempH = _tempstr2int(weather['temp1'])
        tempL = _tempstr2int(weather['temp2'])
        if tempH and tempL:
            weather_info.update({
                'temHigh': tempH,
                'temLow': tempL,
            })

        #weather_info['temHigh'], weather_info[
        #    'temLow'] = get_temp(weather['temp1'])
        #temp1 = {'state': weather['weather2']}
        #temp1['temHigh'], temp1['temLow'] = get_temp(weather['temp2'])
        #temp2 = {'state': weather['weather3']}
        #temp2['temHigh'], temp2['temLow'] = get_temp(weather['temp3'])
        #temp3 = {'state': weather['weather4']}
        #temp3['temHigh'], temp3['temLow'] = get_temp(weather['temp4'])
        #weather_info['future'] = [temp1, temp2, temp3]
        logger.debug(instant_weather['city'])
        logger.debug(weather_info)
        return weather_info
    except Exception, e:
        logger.exception(e)
        return None


def get_temp(temp):
    t1, t2 = temp.split('~')
    t1 = t1[:-1]
    t2 = t2[:-1]
    if int(t1) > int(t2):
        return t1, t2
    else:
        return t2, t1


if __name__ == '__main__':
    update_cities_weather()
    #_crawl_city_weather('101340101')
    print 'done'

#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2013 Baina Info Inc. All rights reserved.
# Created On Apr 7, 2013
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import urllib2
import logging
import datetime
import os
import simplejson

os.environ['DJANGO_SETTINGS_MODULE'] = 'dolphinop.settings'

from dolphinop.service.models import weathers
#from dolphinop.utils import report

logger = logging.getLogger('dolphinop.service')

_RETRY = 3
_TIME_OUT = 30
PM_URL = 'http://appapi.cnpm25.cn/TopInfoWeb.aspx?u=%s'


def crawl_pm(url):
    try:
        res = None
        retry = 0
        while retry < _RETRY and res is None:
            try:
                res = urllib2.urlopen(url, timeout=_TIME_OUT)
                content = res.read()
            except urllib2.URLError:
                retry += 1
        if content is '' or None:
            logger.warn(
                "[PM2.5 Spider] Failed to crawl url %s with %d retry." %
                (url, retry))
            return None
        return simplejson.loads(content)
    except Exception, e:
        logger.exception(e)
        return None


def update_cities_pm():
    logger.info('update cities aqi start')
    cities = weathers.get_cities({'aqi': True})
    #count = 0
    nums = 0
    for city_info in cities:
        url = PM_URL % city_info['city_en']
        pm_info = crawl_pm(url)
        if pm_info and 'AQI' in pm_info and 'UpDateTime' in pm_info:
            aqi = int(pm_info['AQI'].split('_')[0])
            if 'pm_time' in city_info:
                up_time = datetime.datetime.strptime(
                    pm_info['UpDateTime'], '%Y-%m-%d %H:%M')
                query_time = datetime.datetime.strptime(
                    city_info['pm_time'], '%Y-%m-%d %H:%M')
                if up_time <= query_time:
                    continue
            # count+=1;print count, city_info['cityName'], aqi
            weathers.update('weathers',
                            {'id': city_info['id']}, {'pm2d5': aqi}, True)
            weathers.update(
                'cityInfos', {'id': city_info['id']}, {'pm_time': pm_info['UpDateTime']}, True)
        else:
            nums += 1
    if nums == len(cities):
            weathers.update('cityInfos', {'pm_workstate': False},
                            {'break_time': datetime.datetime.now()}, True)
    logger.info('update cities aqi finished')


if __name__ == '__main__':
    update_cities_pm()
    print 'done'

# -*- coding:UTF-8 -*-
'''
Created on Mar 6, 2013

@author: fli
'''
import sys
import logging
from datetime import datetime
from django.views.decorators.http import require_GET
from dolphinop.service.views import response_json
from dolphinop.service.errors import internal_server_error, resource_not_exist, parameter_error, resource_not_modified
from dolphinop.service.models import weathers
from dolphinop.service.utils.iptable import get_ip_info

logger = logging.getLogger('dolphinop.service')

_DEFAULT = 'default'
_DEFAULT_ICON = 'http://opscn.dolphin-browser.com/resources/weather/icon/default.png'
_DEFAULT_BACKGROUND = ''
_DEFAULT_PACKAGE = 'com.dolphin.browser.xf'
_MAIN_WEATHERS = [u'雪', u'雹', u'雷', u'雨', u'霾', u'阴']


@require_GET
def get_weather(request):
    try:
        city = request.GET.get('city', None)
        package = request.GET.get('pn', _DEFAULT_PACKAGE)
        pubDate = int(request.GET.get('mt', 0))
    except Exception, e:
        logger.warnning(e)
        return parameter_error(request, e)
    if city is None:
        ip = request.META['REMOTE_ADDR']
        city = _get_city_name(ip)
        if city is None:
            return resource_not_exist(request, 'city', ip=ip)
    try:
        weather_info = weathers.get_weather({'cityName': city})
        if len(weather_info) > 1:
            ip = request.META['REMOTE_ADDR']
            ipinfo = get_ip_info(ip)
            if ipinfo and 'province' in ipinfo:
                weather_info = get_weather(
                    {'cityName': city, 'province': ipinfo['province']})
                if weather_info:
                    weather_info = _weather_adapter(
                        weather_info[0], package, city)
                    return response_json(weather_info)
        elif len(weather_info) == 1:
            weather_info = _weather_adapter(weather_info[0], package, city)
            return response_json(weather_info)
        return resource_not_exist(request, 'weather', city=city, city_type=type(city))
    except Exception, e:
        return internal_server_error(request, e, sys.exc_info())


def _get_city_name(ip):
    try:
        ipinfo = get_ip_info(ip)
        if ipinfo and 'city' in ipinfo:
            return ipinfo['city']
    except Exception, e:
        logger.exception(e)
    return None


def _get_display(state, package, city):
    now = datetime.now().hour
    cond = {
        'state': {'$in': [state, _DEFAULT]},
        'begin': {'$lte': now},
        'end': {'$gte': now},
        'cityName': {'$in': [city, _DEFAULT]},
    }
    if package:
        cond['package'] = package

    displays = weathers.get_weather_displays(cond)
    display = None
    dis_list = [None for i in range(4)]
    for dis in displays:
        if state == dis['state'] and city == dis['cityName']:
            dis_list[0] = dis
            break
        elif city == dis['cityName']:
            dis_list[1] = dis
        elif state == dis['state']:
            dis_list[2] = dis
        else:
            dis_list[3] = dis
    for dis in dis_list:
        if dis:
            display = dis
    return display


def _get_relevant_display(state, package, city):
    relevant_weather = None
    logger.debug(state)
    for weather in _MAIN_WEATHERS:
        if state.find(weather) >= 0:
            if relevant_weather is None:
                relevant_weather = weather
            else:
                if _MAIN_WEATHERS.index(relevant_weather) > _MAIN_WEATHERS.index(weather):
                    relevant_weather = weather
    logger.debug(relevant_weather)
    if relevant_weather is not None:
        display = _get_display(relevant_weather, package, city)
        logger.debug(display)
        return display
    return None


def _weather_adapter(weather_info, package, city):
    display = _get_display(weather_info['state'], package, city)
    if display is None:
        display = _get_relevant_display(weather_info['state'], package, city)
    logger.debug(display)
    if display is not None:
        weather_info['des'] = display['des']
        weather_info['icon'] = display['icon']
        weather_info['bg'] = display['bg']
    else:
        weather_info['des'] = ''
        weather_info['icon'] = _DEFAULT_ICON
        weather_info['bg'] = _DEFAULT_BACKGROUND
    weather_info['alert'] = weather_info['state']
    if 'future' not in weather_info:
        weather_info['future'] = []
    for future_weather in weather_info['future']:
        display = _get_display(future_weather['state'], package, city)
        if display:
            future_weather['icon'] = display['icon']
        else:
            future_weather['icon'] = _DEFAULT_ICON
    return weather_info

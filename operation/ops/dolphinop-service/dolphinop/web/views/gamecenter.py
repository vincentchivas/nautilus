# -*- coding:utf-8 -*-
# Copyright (c) 2011 Baina Info Inc. All rights reserved.
# @author: Chen Qi
# date:2011-11-20
# email:qchen@bainainfo.com

import time
import logging
from django.shortcuts import render_to_response
from django.template import RequestContext
from dolphinop.service.views import response_json
from dolphinop.decorator import auto_match_locale
from dolphinop.web.models import gamecenter
from dolphinop.web.user_agent import package_request_infos

logger = logging.getLogger("dolphinop.web")


_PLATFORM = {
    ('android', 'zh_CN'): 'AndroidCN',
    ('android', 'en_US'): 'AndroidEN',
    ('iphone', 'zh_CN'): 'iPhoneCN',
    ('iphone', 'en_US'): 'iPhoneEN',
    ('ipad', 'zh_CN'): 'iPadCN',
    ('ipad', 'en_US'): 'iPadEN',
    ('wphone', 'zh_CN'): 'WphoneCN',
    ('wphone', 'en_US'): 'WphoneEN'
}


_DEFAULT_PLATFORM = 'AndroidEN'


def get_user_infos(request):
    os = request.GET.get('os', 'android').lower()
    local = request.GET.get('l', 'en_US')

    platform = _DEFAULT_PLATFORM
    if (os, local) in _PLATFORM:
        platform = _PLATFORM[(os, local)]

    return platform


@auto_match_locale
@package_request_infos
def hotapps(request):

    return render_to_response('hotapps/addon.html',
                              {}, context_instance=RequestContext(request))


def show_features(request):
    user_infos = get_user_infos(request)
    cond = {'platform': user_infos}
    page_no = request.GET.get('page', '1')

    time_now = int(time.time())
    cond['online_time'] = {'$lt': time_now}
    cond['$or'] = [{'offline_time': {'$gt': time_now}}, {'offline': False}]
    feature_apps = gamecenter.get_features(cond, page_no, 8)
    return response_json(feature_apps)


def show_hotings(request):
    user_infos = get_user_infos(request)
    cond = {'platform': user_infos}
    page_no = request.GET.get('page', '1')

    time_now = int(time.time())
    cond['online_time'] = {'$lt': time_now}
    cond['$or'] = [{'offline_time': {'$gt': time_now}}, {'offline': False}]
    hoting_app_list = gamecenter.get_hoting_apps(cond, page_no, 5)
    return response_json(hoting_app_list)


def show_detail(request):
    user_infos = get_user_infos(request)
    try:
        cond = {'platform': user_infos, 'id': int(request.GET.get('id'))}
        fields = request.GET.get('fields', 'all')
    except Exception, e:
        logger.error('%s %s' % (request.build_absolute_uri(), e))
        return response_json([])

    app_datails = gamecenter.get_application_detail(cond, fields)
    return response_json(app_datails)


def search(request):
    cond = {'platform': get_user_infos(request)}
    try:
        title = request.GET.get('title', None)
        cond['title'] = {'$regex': title, '$options': 'i'}
    except Exception, e:
        logger.error(e)
        return response_json([])
    apps = gamecenter.get_search(cond)
    return response_json(apps)

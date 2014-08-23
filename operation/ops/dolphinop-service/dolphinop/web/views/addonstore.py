# -*- coding:utf-8 -*-
# Copyright (c) 2011 Baina Info Inc. All rights reserved.
# @author: Chen Qi
# date:2011-11-20
# email:qchen@bainainfo.com

import time
import logging
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from dolphinop.service.views import response_json
from dolphinop.decorator import auto_match_locale
from dolphinop.web import models
from dolphinop.web.user_agent import package_request_infos
from django.utils import translation

logger = logging.getLogger("dolphinop.web")

_CLIENT_ARGS = settings.CLIENT_ARGS

_OS = {
    'android': 'Android',
    'ipad': 'iPad',
    'iphone': 'iPhone',
    'unknown': 'unknown',
    'pc': 'PC',
    'wphone': 'Wphone',
}

_PLATFORM = {
    ('Android', 'zh_CN'): 'Android_CN',
    ('Android', 'en_US'): 'Android_EN',
    ('iPhone', 'zh_CN'): 'iPhone_CN',
    ('iPhone', 'en_US'): 'iPhone_EN',
    ('iPad', 'zh_CN'): 'iPad_CN',
    ('iPad', 'en_US'): 'iPad_EN',
    ('Wphone', 'zh_CN'): 'Wphone',
}

_GA_ACCOUNTS = {
    'Android_CN': 'UA-32930060-2',
    'Android_EN': 'UA-32930060-1',
    'iPhone_CN': 'UA-25901043-4',
    'iPhone_EN': 'UA-25901043-6',
    'iPad_CN': 'UA-25901043-7',
    'iPad_EN': 'UA-25901043-8',
}
_SHARE_LINKS = {
    'Android_CN':  'sina',
    'Android_EN':  'facebook',
    'iPhone_CN':  'sina',
    'iPhone_EN':  'facebook',
    'iPad_CN':  'sina',
    'iPad_EN':  'facebook',

}


_DEFAULT_PLATFORM = 'Wphone'


def get_user_infos(request):
    user_infos = []
    try:
        os = request.GET.get('os', 'android').lower()
        os = _OS[os]
        local = request.GET.get('l', 'zh_CN')
    except Exception, e:
        logger.error('%s %s' % (request.build_absolute_uri(), e))
    translation.activate(local)

    if (os, local) in _PLATFORM:
        platform = _PLATFORM[(os, local)]
    else:
        platform = _DEFAULT_PLATFORM
    user_infos = [os, local, platform]

    return user_infos


@auto_match_locale
@package_request_infos
def hotapps(request):
    user_infos = get_user_infos(request)
    settings = {
        'platform': user_infos[0],
        'language': user_infos[1],
        'ga_account': _GA_ACCOUNTS[user_infos[2]],
        'share_link': _SHARE_LINKS[user_infos[2]],
    }

    return render_to_response('hotapps/addon.html',
                              settings, context_instance=RequestContext(request))


def show_category(request):
    user_infos = get_user_infos(request)
    try:
        cond = {'platform': user_infos[2]}
    except KeyError, e:
        logger.debug('%s %s' % (request.build_absolute_uri(), e))

    time_now = int(time.time())
    cond['online_time'] = {'$lt': time_now}
    cond['$or'] = [{'offline_time': {'$gt': time_now}}, {'offline': False}]
    cate_list = models.get_category(cond)
    return response_json(cate_list)


def show_category_apps(request):
    user_infos = get_user_infos(request)
    try:
        cond = {'platform': user_infos[2]}
        page_no = request.GET.get('page', '1')
        cond['category'] = int(request.GET.get('id'))
        type = request.GET.get('type')
    except Exception, e:
        logger.debug('%s %s' % (request.build_absolute_uri(), e))
        return render_to_response('404.html')

    time_now = int(time.time())
    cond['online_time'] = {'$lt': time_now}
    cond['$or'] = [{'offline_time': {'$gt': time_now}}, {'offline': False}]

    if type == 'ranking':
        category_app_list = models.get_category_apps_ranking(cond, page_no, 24)
    elif type == 'webapp':
        category_app_list = models.get_category_apps_webapp(cond, page_no, 24)
    else:
        category_app_list = []

    return response_json(category_app_list)


def show_feature(request):
    user_infos = get_user_infos(request)
    cond = {'platform': user_infos[2]}
    try:
        page_no = request.GET.get('page', '1')
    except KeyError, e:
        logger.debug('%s %s' % (request.build_absolute_uri(), e))

    time_now = int(time.time())
    cond['online_time'] = {'$lt': time_now}
    cond['$or'] = [{'offline_time': {'$gt': time_now}}, {'offline': False}]
    feature_apps = models.get_feature_apps(cond, page_no, 24)
    return response_json(feature_apps)


def show_hoting(request):
    user_infos = get_user_infos(request)
    cond = {'platform': user_infos[2]}
    try:
        page_no = request.GET.get('page', '1')
    except KeyError, e:
        logger.debug('%s %s' % (request.build_absolute_uri(), e))

    time_now = int(time.time())
    cond['online_time'] = {'$lt': time_now}
    cond['$or'] = [{'offline_time': {'$gt': time_now}}, {'offline': False}]
    hoting_app_list = models.get_hoting_apps(cond, page_no, 24)
    return response_json(hoting_app_list)


def show_subject(request):
    user_infos = get_user_infos(request)
    cond = {'platform': user_infos[2]}

    time_now = int(time.time())
    cond['online_time'] = {'$lt': time_now}
    cond['$or'] = [{'offline_time': {'$gt': time_now}}, {'offline': False}]
    subject_list = models.get_subject(cond)
    return response_json(subject_list)


def show_subject_apps(request):
    user_infos = get_user_infos(request)
    try:
        cond = {'platform': user_infos[2]}
        page_no = request.GET.get('page', '1')
        cond['id'] = int(request.GET.get('id'))
    except Exception, e:
        logger.debug('%s %s' % (request.build_absolute_uri(), e))
        return render_to_response('404.html')

    category_app_list = models.get_subject_apps(cond, page_no, 24)
    return response_json(category_app_list)


def show_webapp(request):
    user_infos = get_user_infos(request)
    try:
        cond = {'platform': user_infos[2]}
        page_no = request.GET.get('page', '1')
    except Exception, e:
        logger.debug('%s %s' % (request.build_absolute_uri(), e))
        return render_to_response('404.html')

    webapp_list = models.get_webapps(cond, page_no, 24)
    return response_json(webapp_list)


def show_detail(request):
    user_infos = get_user_infos(request)
    try:
        cond = {'platform': user_infos[2], 'id': int(request.GET.get('id'))}
        fields = request.GET.get('fields', 'all')
    except Exception, e:
        logger.debug('%s %s' % (request.build_absolute_uri(), e))

    app_datails = models.get_application_detail(cond, fields)
    return response_json(app_datails)


def show_relevant_apps(request):
    cond = {'platform': get_user_infos(request)[2]}
    try:
        cond['id'] = int(request.GET.get('id', 1))
    except Exception, e:
        logger.error('%s %s' % (request.build_absolute_uri(), e))
    apps = models.get_relevant_addons(cond)
    return response_json(apps)


def search(request):
    cond = {'platform': get_user_infos(request)[2]}
    try:
        title = request.GET.get('title', None)
        cond['application.title'] = {'$regex': title, '$options': 'i'}
    except Exception, e:
        logger.error(e)
    apps = models.get_search(cond)
    return response_json(apps)


def appcache(request):
    return render_to_response('hotapps/addons.appcache',
                              mimetype="text/cache-manifest",
                              context_instance=RequestContext(request))

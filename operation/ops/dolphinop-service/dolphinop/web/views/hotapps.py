# -*- coding:utf-8 -*-
# Copyright (c) 2011 Baina Info Inc. All rights reserved.
# @author: Chen Qi
# date:2011-11-20
# email:qchen@bainainfo.com

import time
import logging
import random
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from dolphinop.service.views import response_json
from dolphinop.service.views.z import get_list
from dolphinop.decorator import auto_match_locale, match_location
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
    'pc': 'PC'
}

_PLATFORM = {
    #        ('Android', 'zh_CN'): 'Android_CN',
    ('Android', 'en_US'): 'Android_EN',
    ('Android', 'ja_JP'): 'Android_JP',
    ('iPhone', 'zh_CN'): 'iPhone_CN',
    ('iPhone', 'en_US'): 'iPhone_EN',
    ('iPad', 'zh_CN'): 'iPad_CN',
    ('iPad', 'en_US'): 'iPad_EN'
}

_GA_ACCOUNTS = {
    'Android_CN': 'UA-25901043-3',
    'Android_EN': 'UA-25901043-5',
    'Android_JP': 'UA-38033608-1',
    'iPhone_CN': 'UA-49196431-1',
    'iPhone_EN': 'UA-49196431-2',
    'iPad_CN': 'UA-49196431-3',
    'iPad_EN': 'UA-49196431-4',
}

_SEARCH_KEYWORDS = {
    'Android_CN': [u'热门游戏', u'流量监控', u'输入法', u'Go桌面', u'微信', u'PPTV', u'相机', u'塔防', u'极品飞车'],
    'Android_EN': ['Find more apps'],
    'Android_JP': [''],
    'iPhone_CN': [''],
    'iPhone_EN': [''],
    'iPad_CN': [''],
    'iPad_EN': ['Search Apps'],
}

_SEARCH_TEMPLATES = {
    'Android_CN': 'hotapps/wandoujia.html',
    'Android_EN': 'hotapps/chomp.html',
    'Android_JP': '',
    'iPhone_CN': '',
    'iPhone_EN': '',
    'iPad_CN': '',
    'iPad_EN': 'hotapps/chomp_ipad.html',
}

_TOUCH_SUPPORT = {
    'Android_CN': 1,
    'Android_EN': 0,
    'Android_JP': 0,
    'iPhone_CN': 1,
    'iPhone_EN': 1,
    'iPad_CN': 1,
    'iPad_EN': 1,
}

_TREND_API = {
    'Android_CN': 0,
    'Android_EN': 0,
    'Android_JP': 0,
    'iPhone_CN': 0,
    'iPhone_EN': 0,
    'iPad_CN': 0,
    'iPad_EN': 0,
}

_AD_TRACKING = {
    'Android_CN': 0,
    'Android_EN': 1,
    'Android_JP': 0,
    'iPhone_CN': 0,
    'iPhone_EN': 0,
    'iPad_CN': 0,
    'iPad_EN': 0,
}

_NEW_VERSION = {
    'Android_CN': 0,
    'Android_EN': 1,
    'Android_JP': 1,
    'iPhone_CN': 0,
    'iPhone_EN': 0,
    'iPad_CN': 0,
    'iPad_EN': 0,
}

_AD_PUBLISHER_ID = {
    'Android_CN': '',
    'Android_EN': 'a14ef9b1f32fa17',
    'Android_JP': '',
    'iPhone_CN': '',
    'iPhone_EN': '',
    'iPad_CN': '',
    'iPad_EN': '',
}

_AUTO_LOADING = {
    'Android_CN': 0,
    'Android_EN': 0,
    'Android_JP': 0,
    'iPhone_CN': 0,
    'iPhone_EN': 0,
    'iPad_CN': 0,
    'iPad_EN': 0,
}

_DEFAULT_PLATFORM = 'Android_EN'
_HOME_PAGE_NO = '1'


def get_user_infos(request):
    user_infos = []
    try:
        os = request.GET.get('os').lower()
        os = _OS['android'] if os.find('android') != -1 else _OS[os]
        local = request.GET.get('l')

    except KeyError, e:
        logger.debug('%s %s' % (request.build_absolute_uri(), e))
    translation.activate(local)

    if (os, local) in _PLATFORM:
        platform = _PLATFORM[(os, local)]
    else:
        platform = _DEFAULT_PLATFORM
    user_infos = [os, local, platform]

    return user_infos


#@match_location
@auto_match_locale
@package_request_infos
def hotapps(request, country=None):
    user_infos = get_user_infos(request)
    settings = {
        'platform': user_infos[0],
        'language': user_infos[1],
        'ga_account': _GA_ACCOUNTS[user_infos[2]],
        'keyword': random.choice(_SEARCH_KEYWORDS[user_infos[2]]),
        'touch_support': _TOUCH_SUPPORT[user_infos[2]],
        'search_template': _SEARCH_TEMPLATES[user_infos[2]],
        'trend_api': _TREND_API[user_infos[2]],
        'ad_tracking': _AD_TRACKING[user_infos[2]],
        'ad_publisher_id': _AD_PUBLISHER_ID[user_infos[2]],
        'auto_loading': _AUTO_LOADING[user_infos[2]],
    }

    cond = {'platform': user_infos[2]}
    if _NEW_VERSION[user_infos[2]]:
        format = request.GET.get('format', 'html')
        if format == 'json':
            return response_json(settings)

        #if country == 'USA':
        #    return HttpResponseRedirect('https://dolphin.studio.quixey.com/promoted?ref=dolphinhome')
        return render_to_response('hotapps/phone2.html',
                                  settings, context_instance=RequestContext(request))

    top_featured_list = models.get_top_featured(cond)
    try:
        page_no = request.GET.get('page', '1')
    except KeyError, e:
        logger.debug('%s %s' % (request.build_absolute_uri(), e))
    page_size = 10 if user_infos[0] != 'iPad' else 18
    featured_app_list = models.get_featured_apps(cond, page_no, page_size)
    settings['app_list'] = featured_app_list
    settings['top_list'] = top_featured_list

    if user_infos[0] == 'iPad':
        return render_to_response('hotapps/ipad.html',
                                  settings, context_instance=RequestContext(request))

    return render_to_response('hotapps/phone.html',
                              settings, context_instance=RequestContext(request))


@auto_match_locale
@package_request_infos
def show_featured(request):
    user_infos = get_user_infos(request)
    cond = {'platform': user_infos[2]}
    try:
        page_no = request.GET.get('page', '1')
        format = request.GET.get('format', 'html')
    except KeyError, e:
        logger.debug('%s %s' % (request.build_absolute_uri(), e))

    if _NEW_VERSION[user_infos[2]]:
        #time_now = int(time.time())
        #cond['online_time'] = {'$lt':time_now}
        #cond['$or'] = [{'offline_time':{'$gt':time_now}},{'offline':False}]
        home_page = models.get_home_page(cond)
        del home_page['top_feature']
        logger.info(len(home_page['apps']))
        ad_list = get_list(request, 'featured')
        ad_len = len(ad_list)
        if int(page_no) == 1 and ad_len:
            #ad_list = ad_list[0:ad_len/2]
            for i, item in enumerate(ad_list):
                tmp_order = item.get('display_order')
                if not tmp_order:
                    continue
                try:
                    home_page['apps'].insert(int(tmp_order), item)
                    del item['display_order']
                except Exception, e:
                    logger.info(e)
                    continue
        logger.info(len(home_page['apps']))

        return response_json(home_page)

    page_size = 10 if user_infos[0] != 'iPad' else 18
    featured_app_list = models.get_featured_apps(cond, page_no, page_size)

    if format == 'json':
        return render_to_response('hotapps/applist.json', {'app_list':
                                                           featured_app_list})

    if user_infos[0] == 'iPad':
        return render_to_response('hotapps/applist_ipad.html', {'app_list':
                                                                featured_app_list}, context_instance=RequestContext(request))

    return render_to_response('hotapps/applist.html', {'app_list':
                                                       featured_app_list}, context_instance=RequestContext(request))


@auto_match_locale
@package_request_infos
def show_trend(request):
    user_infos = get_user_infos(request)
    cond = {'platform': user_infos[2]}
    try:
        page_no = request.GET.get('page', '1')
        format = request.GET.get('format', 'html')
    except KeyError, e:
        logger.debug('%s %s' % (request.build_absolute_uri(), e))

    if _NEW_VERSION[user_infos[2]]:
        #time_now = int(time.time())
        #cond['online_time'] = {'$lt':time_now}
        #cond['$or'] = [{'offline_time':{'$gt':time_now}},{'offline':False}]
        trend_app_list = models.get_trend_apps_new(cond, page_no, 30)
        ad_list = get_list(request, 'trend')
        ad_len = len(ad_list)
        logger.info(ad_len)
        if int(page_no) == 1 and ad_len:
            #ad_list = ad_list[0:ad_len/2]
            for i, item in enumerate(ad_list):
                tmp_order = item.get('display_order')
                if not tmp_order:
                    continue
                try:
                    trend_app_list.insert(int(tmp_order), item)
                    del item['display_order']
                except Exception, e:
                    logger.info(e)
                    continue

        logger.info(len(trend_app_list))

        # if page_no == _HOME_PAGE_NO:
            #home_page = models.get_home_page(cond)
            # result = {
                    #'top_feature': home_page['top_feature'],
                    #'apps': trend_app_list
                    #}
        # else:
        result = {
            'apps': trend_app_list
        }

        if format == 'json':
            return response_json(result)
        return response_json(result)

    page_size = 10 if user_infos[0] != 'iPad' else 18
    trend_app_list = models.get_trend_apps(cond, page_no, page_size)

    if format == 'json':
        return render_to_response('hotapps/applist.json', {'app_list':
                                                           trend_app_list})

    if user_infos[0] == 'iPad':
        return render_to_response('hotapps/applist_ipad.html', {'app_list':
                                                                trend_app_list}, context_instance=RequestContext(request))

    return render_to_response('hotapps/applist.html', {'app_list':
                                                       trend_app_list}, context_instance=RequestContext(request))


@auto_match_locale
@package_request_infos
def show_category_apps(request):
    user_infos = get_user_infos(request)
    try:
        cond = {'platform': user_infos[2]}
        page_no = request.GET.get('page', '1')
        category_id = int(request.GET.get('id'))
        format = request.GET.get('format', 'html')
    except Exception, e:
        logger.debug('%s %s' % (request.build_absolute_uri(), e))
        return render_to_response('404.html')

    if _NEW_VERSION[user_infos[2]]:
        cond['id'] = category_id
        category_app_list = models.get_category_apps_new(cond, page_no, 24)
        if format == 'json':
            return response_json(category_app_list)
        return response_json(category_app_list)

    cond['category'] = category_id
    category_app_list = models.get_category_apps(cond, page_no, 10)

    if format == 'json':
        return render_to_response('hotapps/applist.json', {'app_list':
                                                           category_app_list})

    if user_infos[0] == 'iPad':
        return render_to_response('hotapps/applist_ipad.html', {'app_list':
                                                                category_app_list}, context_instance=RequestContext(request))

    return render_to_response('hotapps/applist.html', {'app_list':
                                                       category_app_list}, context_instance=RequestContext(request))


@auto_match_locale
@package_request_infos
def show_categories(request):
    user_infos = get_user_infos(request)
    cond = {'platform': user_infos[2]}
    try:
        format = request.GET.get('format', 'html')
    except KeyError, e:
        logger.debug('%s %s' % (request.build_absolute_uri(), e))

    if _NEW_VERSION[user_infos[2]]:
        #time_now = int(time.time())
        #cond['online_time'] = {'$lt':time_now}
        #cond['$or'] = [{'offline_time':{'$gt':time_now}},{'offline':False}]
        cate_list = models.get_categories_new(cond)
        if format == 'json':
            return response_json(cate_list)
        return response_json(cate_list)

    cate_list = models.get_categories(cond)
    if format == 'json':
        return render_to_response('hotapps/catelist.json', {'cate_list':
                                                            cate_list})

    return render_to_response('hotapps/catelist.html', {'cate_list':
                                                        cate_list}, context_instance=RequestContext(request))


@auto_match_locale
@package_request_infos
def show_top_featured(request):
    user_infos = get_user_infos(request)
    cond = {'platform': user_infos[2]}
    top_featured_list = models.get_top_featured(cond)

    if _NEW_VERSION[user_infos[2]]:
        #time_now = int(time.time())
        #cond['online_time'] = {'$lt':time_now}
        #cond['$or'] = [{'offline_time':{'$gt':time_now}},{'offline':False}]

        home_page = models.get_home_page(cond)
        return response_json(home_page['top_feature'])

    if user_infos[0] == 'iPad':
        return render_to_response('hotapps/scrollview_ipad.html', {'top_list':
                                                                   top_featured_list}, context_instance=RequestContext(request))

    return render_to_response('hotapps/scrollview.html', {'top_list':
                                                          top_featured_list}, context_instance=RequestContext(request))


@auto_match_locale
@package_request_infos
def show_type_apps(request):
    user_infos = get_user_infos(request)
    try:
        app_type = request.GET.get('type', 'game').lower()
        cond = {'platform': user_infos[2], 'app_type': app_type.capitalize()}
        page_no = request.GET.get('page', '1')
    except KeyError, e:
        logger.debug('%s %s' % (request.build_absolute_uri(), e))
    apps_list = models.get_applications(cond, page_no, 35)

    format = request.GET.get('format', 'html')
    if format == 'json':
        return render_to_response('hotapps/applist.json', {'app_list':
                                                           apps_list})

    if user_infos[0] == 'iPad':
        return render_to_response('hotapps/applist_icon.html', {'app_list':
                                                                apps_list}, context_instance=RequestContext(request))

    return render_to_response('hotapps/applist.html', {'app_list':
                                                       apps_list}, context_instance=RequestContext(request))


@auto_match_locale
@package_request_infos
def show_details(request):
    user_infos = get_user_infos(request)
    try:
        cond = {'platform': user_infos[2], 'id': int(request.GET.get('id'))}
    except Exception, e:
        logger.debug('%s %s' % (request.build_absolute_uri(), e))
    settings = {}
    settings['platform'] = user_infos[0]
    settings['language'] = user_infos[1]
    settings['ga_account'] = _GA_ACCOUNTS[user_infos[2]]

    if _NEW_VERSION[user_infos[2]]:
        app_datails = models.get_application_details_new(cond)
        return response_json(app_datails)

    application = models.get_application_details(cond)
    settings['app_details'] = application
    if user_infos[0] == 'iPad':
        return render_to_response('hotapps/details_ipad.html',
                                  settings, context_instance=RequestContext(request))

    return render_to_response('hotapps/details.html',
                              settings, context_instance=RequestContext(request))


@auto_match_locale
@package_request_infos
def show_ads(request):
    cond = {'platform': get_user_infos(request)[2]}
    ads_list = models.get_advertisements(cond)
    daily_recommend_app = models.get_daily_recommend_app(cond)

    return render_to_response('hotapps/ads.html', {'ads_list': ads_list,
                                                   'recommend_list': daily_recommend_app}, context_instance=RequestContext(request))


@package_request_infos
def get_lovecount(request):
    cond = {'platform': get_user_infos(request)[2]}
    try:
        cond['id'] = int(request.GET.get('id', 1))
    except KeyError, e:
        logger.debug('%s %s' % (request.build_absolute_uri(), e))
    models.set_lovecount(cond)
    return response_json({})


@package_request_infos
def show_relevant_apps(request):
    cond = {'platform': get_user_infos(request)[2]}
    try:
        cond['application.id'] = int(request.GET.get('id', 1))
    except Exception, e:
        logger.error('%s %s' % (request.build_absolute_uri(), e))
    apps = models.get_relevant_apps(cond)
    format = request.GET.get('format', 'html')
    if format == 'json':
        return response_json(apps)
    return response_json(apps)


def appcache(request):
    return render_to_response('hotapps/phone2.appcache',
                              mimetype="text/cache-manifest",
                              context_instance=RequestContext(request))


def get_json_data(request):
    temp_request = request.GET.copy()
    temp_request['format'] = 'json'
    request.GET = temp_request

    type = request.GET.get('type', 'featured')

    if type == 'featured':
        return show_featured(request)
    elif type == 'trend':
        return show_trend(request)
    elif type == 'categories':
        return show_categories(request)
    elif type == 'cateapps':
        return show_category_apps(request)

    return render_to_response('404.html')

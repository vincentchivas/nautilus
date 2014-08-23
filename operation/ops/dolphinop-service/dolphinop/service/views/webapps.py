#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2013 Baina Info Inc. All rights reserved.
# Created On Apr 18, 2013
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import sys
import logging
import operator
from pymongo import ASCENDING
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from dolphinop.service.views import response_json
from dolphinop.service.errors import internal_server_error
from dolphinop.service.models import webappsdb
from dolphinop.service.utils import get_parameter_GET

PAGE_SIZE = 20
logger = logging.getLogger('dolphinop.service')


def _generate_result(result, extend=False):
    if isinstance(result, list):
        results = []
        for item in result:
                results.append(item['_meta'])
        return results
    elif isinstance(result, dict):
        if extend:
            return result
        else:
            return result['_meta']
    else:
        return result


def get_common_params(request):
    package_name = get_parameter_GET(request, 'pn')
    page = get_parameter_GET(request, 'page', default='0', convert_func=int)
    return {
        "package_name": package_name,
        "page": page
    }


def _get_webapps_rawdatas(coll, cond={}, args={}, sort=None, page_size=PAGE_SIZE):
    cond['_rule.packages'] = {'$in': [args['package_name']]}
    logger.debug(coll)
    logger.debug(cond)
    results = webappsdb.get_list(
        coll, cond, sort=sort, page=args['page'], page_size=page_size)
    logger.debug(results)
    results = _generate_result(results)
    logger.debug(results)
    return results


def _get_webapps_rawdata(coll, cond, args, extend=False):
    cond['_rule.packages'] = {'$in': [args['package_name']]}
    result = webappsdb.get_obj(coll, cond)
    logger.debug(type(result))
    result = _generate_result(result, extend)
    return result


@require_GET
def show_cats(request):
    args = get_common_params(request)
    for key in ('package_name', 'page'):
        if isinstance(args[key], HttpResponse):
            return args[key]
    try:
        cats = _get_webapps_rawdatas(
            'webapps_category', args=args, sort=[('_meta.order', ASCENDING)])
        return response_json({'categories': cats})
    except Exception, e:
        logger.error(e)
        return internal_server_error(request, e, sys.exc_info())


@require_GET
def show_subjects(request):
    args = get_common_params(request)
    args['banner'] = get_parameter_GET(request, 'banner', required=False)
    for key in ('package_name', 'page'):
        if isinstance(args[key], HttpResponse):
            return args[key]
    try:
        cond = {}
        sort = [('_meta.order', ASCENDING)]
        if args['banner'] and ['banner'] == 'true':
            cond['_meta.banner'] = True
        subjects = _get_webapps_rawdatas(
            'webapps_subject', args=args, sort=sort)
        return response_json({'subjects': subjects})
    except Exception, e:
        logger.error(e)
        return internal_server_error(request, e, sys.exc_info())


@require_GET
def show_apps(request):
    args = get_common_params(request)
    args['cid'] = get_parameter_GET(
        request, 'cid', required=False, convert_func=int)
    args['sid'] = get_parameter_GET(
        request, 'sid', required=False, convert_func=int)
    args['q'] = get_parameter_GET(request, 'q', required=False)
    for key in ('package_name', 'page'):
        if isinstance(args[key], HttpResponse):
            return args[key]
    try:
        result_dict = _get_apps(args)
        return response_json(result_dict)
    except Exception, e:
        logger.error(e)
        return internal_server_error(request, e, sys.exc_info())


def _get_apps(args):
    cond = {}
    result_dict = {}
    sort = None
    if args['cid'] is not None:
        cond['_meta.cid'] = args['cid']
        sort = [('_meta.cat_order', ASCENDING)]
        category = _get_webapps_rawdata(
            'webapps_category', {'_meta.id': args['cid']}, args=args)
        if category:
            result_dict['name'] = category['name']
    elif args['sid'] is not None:
        subject = _get_webapps_rawdata(
            'webapps_subject', {'_meta.id': args['sid']}, args=args, extend=True)
        if subject:
            result_dict['name'] = subject['_meta']['name']
            sub_apps = subject['_meta_extend']['apps']
            sub_apps.sort(key=operator.itemgetter('order'))
            start = args['page'] * PAGE_SIZE
            end = (args['page'] + 1) * PAGE_SIZE
            sub_apps = sub_apps[start:end]
            app_ids = [app['id'] for app in sub_apps]
            cond['_meta.id'] = {'$in': app_ids}
            app_list = _get_webapps_rawdatas('webapps_application', cond, args)
            app_list.sort(key=operator.itemgetter('id'), cmp=lambda x,
                          y: cmp(app_ids.index(x), app_ids.index(y)))
            result_dict['apps'] = app_list
        else:
            result_dict['apps'] = []
        return result_dict
    elif args['q'] is not None:
        if args['q']:
            cond['_meta.name'] = {'$regex': args['q'], '$options': 'i'}
        else:
            result_dict['apps'] = []
            return result_dict
    else:
        sort = [('_meta.order', ASCENDING)]
        cond['_meta.promote'] = True

    apps = _get_webapps_rawdatas(
        'webapps_application', cond, args=args, sort=sort)
    result_dict['apps'] = apps
    return result_dict

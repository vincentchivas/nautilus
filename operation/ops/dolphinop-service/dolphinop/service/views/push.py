#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On Dec 30, 2012
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import sys
#import time
import logging
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from dolphinop.service.views import response_json, ALL_FLAG, OTHER, OPERATORS
from dolphinop.service.utils import get_parameter_GET
from dolphinop.service.utils.common_op import dup_by_key, normalize_result, rule_parse, filter_sdk, filter_gray_level
from dolphinop.service.utils.content import ALL_FLAG, now
from dolphinop.service.errors import parameter_error, internal_server_error, resource_not_modified
from dolphinop.service.models import searchdb

logger = logging.getLogger('dolphinop.service')

MAX_MESSAGES = 10

SEARCH_FIELDS = {
    '_id': 0,
}


def get_common_params(request):
    package_name = get_parameter_GET(request, 'pn', alternative_name='pname')
    source = get_parameter_GET(request, 'src', default='ofw')
    version = get_parameter_GET(request, 'vn', default=0, convert_func=int)

    return {
        "package_name": package_name,
        "source": source,
        "version": version,
    }


def _filter_items(items, t):
    results = []
    for item in items:
        if item['last_modified'] <= t and item['icon']['last_modified'] <= t:
            item = {'id': item['id']}
        elif item['icon']['last_modified'] <= t:
            del item['icon']
        results.append(item)
    return results


def _adapt_items(items):
    results = []
    for item in items:
        item['icon'] = item['icon_url']
        del item['last_modified']
        del item['icon_url']
        results.append(item)
    return results


def _get_search_rawdata(request, args, db, func_name):

    #now_t = now()
    cond = {
        '_rule.packages': {'$in': [args['package_name']]},
        '_rule.sources.include': {'$in': [args['source'], ALL_FLAG]},
        '_rule.sources.exclude': {'$ne': args['source']},
        '_rule.max_version': {'$gte': args['version']},
        '_rule.min_version': {'$lte': args['version']},
        #'_rule.end_time': {'$gte': now_t},
        #'_rule.start_time': {'$lte': now_t},
        '_rule.operators': {'$in': [args['operator'], ALL_FLAG]},
    }
    # for push only
    cond.update({'_key.message_id': {'$gt': args['message_id']}})

    logger.info(cond)
    section_infos = db.__getattribute__(func_name)(cond, fields=SEARCH_FIELDS)
    logger.debug(section_infos)
    if not section_infos:
        return resource_not_modified(request, 'search')
    section_infos = rule_parse(
        section_infos, args, rules=["locales", "locations", "sources"])
    logger.debug(section_infos)
    result_section = dup_by_key(section_infos, sort=True, cmp_func=None)
    logger.debug(result_section)
    return result_section


def _option_choices(cond, args, choices):
    for key, arg_key, sign, extra_args in choices:
        if arg_key in args:
            cond['_rule.%s' % key] = {'$%s' %
                                      sign: extra_args.append(args[arg_key])}


def _get_pushmessages(request, args, db, func_name):
    cond = {
        '_rule.packages': {'$in': [args['package_name']]},
        '_rule.sources.exclude': {'$ne': args['source']},
        '_rule.sources.include': {'$in': [args['source'], ALL_FLAG]},
        '_rule.max_version': {'$gte': args['version']},
        '_rule.min_version': {'$lte': args['version']},
        '_rule.operators': {'$in': [args['operator'], ALL_FLAG]},
        '_meta.id': {'$gt': args['message_id']},
        #'_rule.target_engine': {'$in': [args['es']]}
    }
    #_option_choices(cond,args,option_choices)
    section_infos = db.__getattribute__(func_name)(cond, fields=SEARCH_FIELDS)
    logger.debug(section_infos)
    if not section_infos:
        return resource_not_modified(request, 'search')
    results = rule_parse(section_infos, args,
                         rules=["locales", "locations", "sources"])
    logger.debug(results)
    return results


def filter_es(sections, es):
    result = []
    for section in sections:
        target_es = section["_rule"].get('target_engine')
        if target_es is None or es in target_es:
            result.append(section)
    return result


def sort_by_id(list_dict):
    return list_dict['id']


@require_GET
def push_messages2(request):
    args = get_common_params(request)
    request_get = request.GET
    args['locales'] = request_get.get('lc')
    args['message_id'] = int(request_get.get('msgid', 0))
    args['operator'] = request_get.get('op', OTHER)
    args['sdk'] = request_get.get('avn')
    args['mark'] = request_get.get('mark')
    if args['operator'] not in OPERATORS:
        args['operator'] = OTHER
    args['es'] = request_get.get('es')
    if args['es']:
        try:
            args['es'] = int(args['es'])
        except:
            args['es'] = None

    for q in (args['package_name'],):
        if isinstance(q, HttpResponse):
            return q
    try:
        results = []
        sections = _get_pushmessages(
            request, args, searchdb, "get_push_messages_new")
        if isinstance(sections, HttpResponse):
            return sections
        sections = filter_sdk(sections, args['sdk'])
        sections = filter_gray_level(sections, args['mark'])
        sections = filter_es(sections, args['es'])
        if len(sections) == 0:
            return resource_not_modified(request, 'search')
        for r in sections:
            meta = r.get('_meta')
            if meta:
                results.append(meta)
        results = sorted(results, key=sort_by_id)
        return response_json(results)

    except Exception, e:
        logger.error(e)
        return internal_server_error(request, e, sys.exc_info())


@require_GET
def push_messages(request):
    args = get_common_params(request)
    args['locales'] = get_parameter_GET(request, 'lc')
    # int(query.get('mt', 0))
    args['message_id'] = get_parameter_GET(
        request, 'msgid', default=0, convert_func=int)
    # query.get('op', OTHER)
    args['operator'] = get_parameter_GET(request, 'op', default=OTHER)
    if args['operator'] not in OPERATORS:
        args['operator'] = OTHER
    for q in (args['package_name'], args['locales']):
        if isinstance(q, HttpResponse):
            return q
    try:
        result_section = []
        section_infos = _get_search_rawdata(
            request, args, searchdb, "get_push_messages")
        if isinstance(section_infos, HttpResponse):
            return section_infos
        for r in section_infos:
            result_section.append(
                normalize_result(r, ["message_id", "push_type", "content1", "content2"]))

    except Exception, e:
        logger.error(e)
        return internal_server_error(request, e, sys.exc_info())
    return response_json(result_section[:MAX_MESSAGES])

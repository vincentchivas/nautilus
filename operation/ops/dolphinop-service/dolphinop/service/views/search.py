#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import time
import logging
import json
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from dolphinop.service.views import response_json, OTHER, OPERATORS
from dolphinop.service.utils import get_parameter_GET
from dolphinop.service.utils.common_op import dup_by_key, normalize_result, rule_parse
from dolphinop.service.utils.content import now, ALL_FLAG
from dolphinop.service.errors import internal_server_error, resource_not_modified
from dolphinop.service.models import searchdb

logger = logging.getLogger('dolphinop.service')

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


def _adapt_extend(items):
    results = []
    for item in items:
        if "extend" in item:
            try:
                extend = json.loads(item['extend'])
                item.update(extend)
            except Exception, e:
                logger.info(e)
            del item['extend']
        results.append(item)
    return results


def _adapt_time(items, time):
    flag = False
    for item in items:
        if item['last_modified'] > time:
            flag = True

    return items if flag else []


def _get_search_rawdata(request, args, db, func_name):

    #now_t = now()
    cond = {
        '_rule.packages': {'$in': [args['package_name']]},
        '_rule.sources.include': {'$in': [args['source'], ALL_FLAG]},
        '_rule.sources.exclude': {'$ne': args['source']},
        '_meta.last_modified': {'$gt': args['t']},
        '_rule.max_version': {'$gte': args['version']},
        '_rule.min_version': {'$lte': args['version']},
        #            '_rule.end_time': {'$gte': now_t},
        #            '_rule.start_time': {'$lte': now_t},
        '_rule.operators': {'$in': [args['operator'], ALL_FLAG]},
    }
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


def _get_cats(request, icon_format, extra_filter=None):
    args = get_common_params(request)
    # int(query.get('mt', 0))
    args['t'] = get_parameter_GET(
        request, 'mt', default=0, convert_func=int, alternative_name='t')
    # query.get('op', OTHER)
    args['operator'] = get_parameter_GET(request, 'op', default=OTHER)
    args['locales'] = get_parameter_GET(
        request, 'lc', required=False,  default=None)
    if args['operator'] not in OPERATORS:
        args['operator'] = OTHER
    logger.debug(args)
    if extra_filter == 'filter_time':
        time_flag = args['t']
        args['t'] = 0

    for q in (args['package_name'], args['source'], args['version'], args['t'],):
        if isinstance(q, HttpResponse):
            return q
    try:
        section_infos = _get_search_rawdata(
            request, args, searchdb, "get_search_categories")
        if isinstance(section_infos, HttpResponse):
            return section_infos
        result_section = []
        for r in section_infos:
            result_section.append(
                normalize_result(r, ["searches", "last_modified", "layout", "order", "title"]))
        logger.debug(result_section)
        if icon_format == 'base64':
            for section in result_section:
                section['searches'] = _filter_items(
                    section['searches'], args['t'])
                section['searches'] = _adapt_extend(section['searches'])
            if not len(result_section):
                return response_json("")
        elif icon_format == 'url':
            for section in result_section:
                section['searches'] = _adapt_items(section['searches'])
                section['searches'] = _adapt_extend(section['searches'])
        result_section = _adapt_time(
            result_section, time_flag) if extra_filter == 'filter_time' else result_section

    except Exception, e:
        logger.error(e)
        return internal_server_error(request, e, sys.exc_info())
    return resource_not_modified(request, 'search') if len(result_section) == 0 else response_json(result_section)


@require_GET
def show_cats(request):
    return _get_cats(request, 'base64')


@require_GET
def show_cats2(request):
    return _get_cats(request, 'url')


@require_GET
def show_cats3(request):
    return _get_cats(request, 'url', 'filter_time')


@require_GET
def show_hotwords(request):

    args = get_common_params(request)
    # int(query.get('mt', 0))
    args['t'] = get_parameter_GET(request, 'mt', default=0, convert_func=int)
    # query.get('op', OTHER)
    args['operator'] = get_parameter_GET(request, 'op', default=OTHER)
    args['locales'] = request.GET.get('lc', '')
    if args['operator'] not in OPERATORS:
        args['operator'] = OTHER
    for q in (args['package_name'], args['source'], args['version'], args['t'],):
        if isinstance(q, HttpResponse):
            return q
    try:
        result_section = []
        section_infos = _get_search_rawdata(
            request, args, searchdb, "get_search_categories")
        if isinstance(section_infos, HttpResponse):
            return section_infos
        for r in section_infos:
            result_section.append(normalize_result(r, ["hotwords", "layout"]))

    except Exception, e:
        logger.error(e)
        return internal_server_error(request, e, sys.exc_info())
    return response_json({'categories': result_section, 'last_modified': int(time.time())})


@require_GET
def show_tracks(request):
    args = get_common_params(request)
    # int(query.get('mt', 0))
    args['t'] = get_parameter_GET(request, 'mt', default=0, convert_func=int)
    # query.get('op', OTHER)
    args['operator'] = get_parameter_GET(request, 'op', default=OTHER)
    args['locales'] = get_parameter_GET(
        request, 'lc', required=False, default=None)
    if args['operator'] not in OPERATORS:
        args['operator'] = OTHER
    for q in (args['package_name'], args['source'], args['version'], args['t'],):
        if isinstance(q, HttpResponse):
            return q
    try:
        result_section = []
        section_infos = _get_search_rawdata(
            request, args, searchdb, "get_search_keywords")
        if isinstance(section_infos, HttpResponse):
            return section_infos
        for r in section_infos:
            result_section.append(
                normalize_result(r, ["keyword", "tracks", "replace"]))

    except Exception, e:
        logger.error(e)
        return internal_server_error(request, e, sys.exc_info())
    return response_json({'tracks': result_section, 'last_modified': int(time.time())})

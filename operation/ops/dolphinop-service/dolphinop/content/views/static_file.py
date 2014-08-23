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
from dolphinop.service.utils.common_op import dup_by_key, normalize_result, rule_parse, now
from dolphinop.service.errors import internal_server_error, resource_not_modified
from dolphinop.content.models import content

DefaultSidList = [1, 2, 3, 4]

logger = logging.getLogger('dolphinop.service')
COMMON_FIELDS = {
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


def _get_rawdata(request, args, dbmodule, func_name):

    now_t = now()
    cond = {
        '_rule.packages': {'$in': [args['package_name']]},
        '_rule.sources.include': {'$in': [args['source'], None]},
        '_rule.sources.exclude': {'$ne': args['source']},
        '_meta.last_modified': {'$gt': args['t']},
        '_rule.max_version': {'$gte': args['version']},
        '_rule.min_version': {'$lte': args['version']},
        #            '_rule.end_time': {'$gte': now_t},
        #            '_rule.start_time': {'$lte': now_t},
        '_rule.operators': {'$in': [args['operator'], []]},
    }
    extend_cond = {
        '_key.cid': args['cid'],
    }
    if args["sid"]:
        extend_cond['_key.sid'] = args["sid"]
    cond.update(extend_cond)
    logger.info(cond)
    section_infos = dbmodule.__getattribute__(
        func_name)(cond, fields=COMMON_FIELDS)
    logger.debug(section_infos)
    if not section_infos:
        return resource_not_modified(request, 'search')
    section_infos = rule_parse(
        section_infos, args, rules=["locales", "locations", "sources"])
    logger.debug(section_infos)
#    result_section = dup_by_key(section_infos, sort=True, cmp_func=None)
#    logger.debug(result_section)
    return section_infos


def _caculate_total_screens(result_section):
    l = []
    for r in result_section:
        if r["sid"] not in l:
            l.append(r["sid"])
    return len(l)


def _dict_cmp(a, b):
    if a['sid'] > b['sid']:
        return 1
    elif a['sid'] < b['sid']:
        return -1
    elif a['order'] > b['order']:
        return 1
    elif a['order'] < b['order']:
        return -1
    else:
        return 0


def build_ret(ret, args, temp_result):
    result_section = []
    if not args["sid"]:
        ret["data"]["total_screens"] = _caculate_total_screens(result_section)
    args["sid"] = DefaultSidList
    for r in temp_result:
        if r["sid"] in args["sid"] and r['order'] >= args['index'] \
                and args['index'] + args['limit'] > r['order']:
            result_section.append(r)
    result_section = sorted(result_section, cmp=_dict_cmp)


@require_GET
def update_check(request):
    ret = {
        "result": 0,
        "msg": "OK",
        "data": {
            "total_screens": 0,
            "items": []
        },
    }
    args = get_common_params(request)
    # int(query.get('mt', 0))
    args['t'] = get_parameter_GET(request, 'mt', default=0, convert_func=int)
    # query.get('op', OTHER)
    args['operator'] = get_parameter_GET(request, 'op', default=OTHER)
    args['sid'] = get_parameter_GET(request, 'sid', convert_func=json.loads)
    args['index'] = get_parameter_GET(request, 'index', convert_func=int)
    args['limit'] = get_parameter_GET(request, 'limit', convert_func=int)
    args['cid'] = get_parameter_GET(request, 'cid', convert_func=int)
    if args['operator'] not in OPERATORS:
        args['operator'] = OTHER
    for q in (args['package_name'], args['source'], args['version'],
              args['t'], args['sid'], args['index'], args['limit']):
        if isinstance(q, HttpResponse):
            return q
    try:
        result_section = []
        section_infos = _get_rawdata(
            request, args, content, "get_content_data")
        if isinstance(section_infos, HttpResponse):
            return section_infos
        for r in section_infos:
            result_section.append(normalize_result(r, ["sid", "order", "fixed",
                                                       "title", "image", "size", "url", "description", "tags"]))
        ret = build_ret(ret, args, result_section)
    except Exception, e:
        logger.error(e)
        return internal_server_error(request, e, sys.exc_info())
    return response_json(ret)

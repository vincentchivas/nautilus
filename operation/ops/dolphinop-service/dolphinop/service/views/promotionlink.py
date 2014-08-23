#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On August 3, 2012
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import sys
import logging
import time
from django.views.decorators.http import require_GET
from dolphinop.service.views import response_json
from dolphinop.service.utils.content import RULE_ORIGINIZE, ALL_FLAG, OPERATORS, OTHER, now
from dolphinop.service.errors import parameter_error, resource_not_modified, internal_server_error
from dolphinop.service.models import plinkdb

logger = logging.getLogger('dolphinop.service')

DEFAULT_SOURCE = 'ofw'

SPECIAL_PID = '2'

STATUS_DELETED = -1
STATUS_DISABLED = 0
STATUS_PREVIEW = 1
STATUS_PUBLISHED = 2


def _filter_locale(items, locale):
    special = []
    common = []
    for item in items:
        try:
            in_locale = item['_rule']['locales']['include']
            ex_locale = item['_rule']['locales']['exclude']
            if locale not in ex_locale:
                del item['_rule']
                if locale in in_locale:
                    special.append(item)
                elif ALL_FLAG in in_locale:
                    common.append(item)
            else:
                continue
        except KeyError, e:
            continue
    return special if len(special) else common

def _filter_avn(items, avn):
    result = []
    if avn:
        avn = int(avn)
        result = [item for item in items if (item['_rule']['max_sdk'] >= avn and item['_rule']['min_sdk'] <= avn) or item['_rule']['max_sdk'] == 0]
    else:
        result = [item for item in items if item['_rule']['max_sdk'] == 0]
    return result

@require_GET
def show_promotionlinks(request):
    try:
        data = request.GET
        t = int(data.get('mt', 0))
        args = {
            'pn': data.get('pn', None),
            'src': data.get('src', None),
            'vn': data.get('ver') or data.get('vn', None),
            'lc': data.get('lc', None),
            'avn': data.get('avn', None),
            'op': data.get('op', OTHER),
            'time_valid': True,
        }
        if not args['vn']:
            return parameter_error(request, 'version')
        cond = {}
        cond_rule = RULE_ORIGINIZE
        for key, value in args.items():
            if key in cond_rule and value is not None:
                match = cond_rule[key]
                if not match[1]:
                    cond.update(eval(match[0]))
                else:
                    cond.update(eval(match[0] % (value, value))
                                if match[1] == 2 else eval(match[0] % value))
        logger.debug(cond)
    except KeyError, e:
        logger.debug("URL:%s Exception:%s" % (request.build_absolute_uri(), e))
        return parameter_error(request, e)
    except Exception, e:
        logger.exception(e)
        return internal_server_error(request, e, sys.exc_info())
    plinks = plinkdb.get_promotionlink(cond)
    result_plinks = filter(lambda pl: pl['last_modified'] > t, plinks)
    published_plinks = filter(
        lambda pl: pl['status'] == STATUS_PUBLISHED, result_plinks)
    logger.debug(published_plinks)
    valid_avn_plinks = _filter_avn(published_plinks, args['avn'])
    logger.debug(valid_avn_plinks)
    final_plinks = _filter_locale(valid_avn_plinks, args['lc'])
    logger.debug(final_plinks)
    if len(plinks) > 0 and len(result_plinks) == 0:
        return resource_not_modified(request, 'promotion link')
    return response_json(final_plinks)

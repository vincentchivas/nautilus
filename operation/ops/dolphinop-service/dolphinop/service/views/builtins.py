# Copyright (c) 2011 Baina Info Inc. All rights reserved.
# author:kunli
# date:2011-07-12
# email:kunli@bainainfo.com
import logging
import sys
import re
from datetime import datetime
from django.http import HttpResponse
from django.views.decorators.http import require_GET, last_modified
from dolphinop.service.models import builtindb
from dolphinop.decorator import auto_match_locale
from dolphinop.service.views import response_json, OTHER, OPERATORS
from dolphinop.service.errors import parameter_error, internal_server_error
from django.conf import settings

logger = logging.getLogger('dolphinop.service')


_FIELDS_FULL = {
    '_id': 0,
    'force': 1,
    'source': 1,
    'pname': 1,
    'timestamp': 1,
    'bookmarks': 1,
    'speedDials': 1,
    'webapps': 1,
    'webzineColumns': 1,
    'weibo': 1,
    'treasure_favs': 1,
    'preset_url': 1,
    'promotion': 1,
}


def get_query(request):
    query = request.GET
    source = query.get('src', 'ofw')
    pname = query.get('pname', None)
    pn = query.get('pn', None)
    pn = pname or pn
    if pn is None:
        return parameter_error(request, 'pn')
    operator = query.get('op', OTHER)
    if operator not in OPERATORS:
        operator = OTHER
    return source, pn, operator


def promotion_match(cond, file_name):
    try:
        if file_name:
            matchs = re.match(r'\D*_?(\d+)_(\d+)', file_name)
            if matchs and len(matchs.groups()) == 2:
                cond.update(
                    {'is_promotion': True, 'promotion_flag': '%s_%s' % matchs.groups()})
                builtins = builtindb.get_built_ins(cond, fields=_FIELDS_FULL)
                if builtins and len(builtins):
                    return builtins
                del cond['promotion_flag']
    except Exception, e:
        logger.info(e)
    cond.update({'is_promotion': {'$nin': [True]}})

    # retry if no found and query args do not use default value
    builtins = builtindb.get_built_ins(cond, fields=_FIELDS_FULL)
    if not builtins and cond['source'] != settings.DEFAULT_SOURCE:
        cond['source'] = settings.DEFAULT_SOURCE
        builtins = builtindb.get_built_ins(cond, fields=_FIELDS_FULL)

    return builtins


def build_condition(*args):
    cond = {}
    for name, value in zip(('source', 'pname', 'operators'), args):
        if name and value:
            cond[name] = value
    return cond


@auto_match_locale
@require_GET
@last_modified(lambda r: datetime.now())
def builtins(request):
    """
    Get builtin data.
    Client only requests once.
    """
    try:
        result = get_query(request)
        if isinstance(result, HttpResponse):
            return result
        cond = build_condition(*result)
        chn = request.GET.get('chn')
        builtins = promotion_match(cond, chn)
    except Exception, e:
        return internal_server_error(request, e, sys.exc_info())
    return response_json(builtins)

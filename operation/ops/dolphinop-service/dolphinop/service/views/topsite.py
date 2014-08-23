#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2013 Baina Info Inc. All rights reserved.
# Created On Apr 24, 2013
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import sys
import logging
from django.views.decorators.http import require_GET
from dolphinop.service.views import response_json
from dolphinop.service.errors import parameter_error, internal_server_error
from dolphinop.service.models import topsitedb

logger = logging.getLogger('dolphinop.service')


def _filter_items(items, t):
    results = []
    for item in items:
        if item['last_modified'] <= t:
            item = {'id': item['id']}
            results.append(item)
        else:
            del item['last_modified']
            results.append(item)
    return results


@require_GET
def show_topsites(request):
    try:
        query = request.GET
        package = query.get('pn')
        version = int(query.get('vn', '0'))
        mt = int(query.get('mt', '0'))
    except Exception, e:
        logger.info(e)
        return parameter_error(request, e)
    try:
        cond = {
            'package': package,
            'max_version': {'$gte': version},
            'min_version': {'$lte': version}
        }
        sites = topsitedb.get_sites(cond)
        if sites:
            last_modified = sites[0]['last_modified']
        else:
            return response_json({'sites': [], 'last_modified': 0})
        sites = _filter_items(sites, mt)
        return response_json({'sites': sites, 'last_modified': last_modified})
    except Exception, e:
        logger.error(e)
        return internal_server_error(request, e, sys.exc_info())

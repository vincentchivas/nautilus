#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2013 Baina Info Inc. All rights reserved.
# Created On May 17, 2013
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import sys
import logging
from django.views.decorators.http import require_GET
from dolphinop.service.views import response_json, ALL_FLAG
from dolphinop.service.errors import parameter_error, resource_not_modified, internal_server_error
from dolphinop.service.models import gamemodedb

logger = logging.getLogger('dolphinop.service')


@require_GET
def show_modes(request):
    try:
        query = request.GET
        package = query.get('pn')
        version = int(query.get('vn', '0'))
        source = query.get('src')
        mt = int(query.get('mt', '0'))
        mode = query.get('mode')
    except Exception, e:
        logger.info(e)
        return parameter_error(request, e)
    try:
        cond = {
            'package': package,
            'max_version': {'$gte': version},
            'min_version': {'$lte': version},
            'sources.include': {'$in': [source, ALL_FLAG]},
            'sources.exclude': {'$ne': source},
        }
        if mode:
            cond['mode'] = mode
        modes = gamemodedb.get_modes(cond)
        new_modes = filter(lambda x: x['last_modified'] > mt, modes)
        if len(new_modes) < len(modes):
            return resource_not_modified(request, 'modes')
        if modes:
            last_modified = modes[0]['last_modified']
            for mode in modes:
                del mode['last_modified']
            return response_json({'modes': modes, 'last_modified': last_modified})
        else:
            return response_json({'modes': modes, 'last_modified': 0})
    except Exception, e:
        logger.error(e)
        return internal_server_error(request, e, sys.exc_info())

#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On August 23, 2012
# @Author : Jun Wang
# Email: jwang@bainainfo.com

import logging
import sys
from django.views.decorators.http import require_GET
from dolphinop.service.views import response_json, ALL_FLAG
from dolphinop.service.errors import parameter_error, resource_not_modified, internal_server_error
from dolphinop.service.models import splashdb
from dolphinop.utils import perf_logging

logger = logging.getLogger('dolphinop.service')

DEFAULT_SOURCE = 'ofw'


@require_GET
@perf_logging
def show_splashscreens(request):
    data = request.GET
    try:
        package_name = data.get('pn')
        version = data.get('ver')
        vn = data.get('vn')
        version = version or vn
        version = int(version)
        source = data.get('src', DEFAULT_SOURCE)
        net = data.get('net')
        x = data.get('x')
        w = data.get('w')
        y = data.get('y')
        h = data.get('h')
        x = int(x or w)
        y = int(y or h)
        t = data.get('t', '0')
        mt = data.get('mt', '0')
        t = t or mt
        t = int(t)
    except Exception, e:
        logger.debug("URL:%s Exception:%s" % (request.build_absolute_uri(), e))
        return parameter_error(request, e)
    try:
        cond = {
            'package': package_name,
            'sources.include': {'$in': [source, ALL_FLAG]},
            'sources.exclude': {'$ne': source},
            'last_modified': {'$gt': t},
            '$or': [
                {'min_version': {'$lte': version},
                    'max_version': {'$gte': version}},
                {'min_version': 0, 'max_version': 0}
            ]
        }
        splashscreens = splashdb.get_splashscreens(cond)
        if splashscreens.count() == 0:
            return resource_not_modified(request, 'splashscreen')

        result_list = []
        for splashscreen in splashscreens:
            for screen in splashscreen['screens']:
                if (x >= screen['min_w'] and x <= screen['max_w']) and (y >= screen['min_h'] and y <= screen['max_h']):
                    result = {
                        'id': splashscreen['id'],
                        'title': splashscreen['title'],
                        'description': splashscreen['description'],
                        'initial_validity': splashscreen['initial_validity'],
                        'validity_by': splashscreen['validity_by'],
                        'color': splashscreen['color'],
                        'last_modified': splashscreen['last_modified'],
                    }
                    result['front_pic'] = '' if screen[
                        'front_wifi_only'] and net != 'wifi' else screen['front_pic']
                    result['background_pic'] = '' if screen[
                        'background_wifi_only'] and net != 'wifi' else screen['background_pic']
                    result_list.append(result)
    except Exception, e:
        logger.exception(e)
        return internal_server_error(request, e, sys.exc_info())
    return response_json(result_list)

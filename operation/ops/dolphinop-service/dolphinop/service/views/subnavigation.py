#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On August 25, 2012
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import logging
import sys
from django.views.decorators.http import require_GET
from dolphinop.service.views import response_json, DEFAULT_SOURCE
from dolphinop.service.errors import parameter_error, resource_not_modified, internal_server_error
from dolphinop.service.models import subnagdb, contentdb

logger = logging.getLogger('dolphinop.service')
NOVEL_SECTION = u'总排行'


@require_GET
def show_subnavigation(request):
    data = request.GET
    try:
        page = data.get('page')
        package_name = data.get('pname')
        last_modified = data.get('t', 0)
    except Exception, e:
        logger.debug("URL:%s Exception:%s" % (request.build_absolute_uri(), e))
        return parameter_error(request, e)
    try:
        cond = {
            'package': package_name,
            'page_name': page
        }
        logger.debug(cond)
        subnavigation = subnagdb.get_subnavigation(cond)
        if subnavigation:
            if page == 'novel':
                novel_list = contentdb.get_novels(
                    package_name, DEFAULT_SOURCE, NOVEL_SECTION)
                if novel_list:
                    novel_list = novel_list['items']
                for item in subnavigation['categories']:
                    if item['layout'] == 'feature':
                        item['items'] = novel_list
                return response_json(subnavigation)
            if subnavigation['last_modified'] <= last_modified:
                return resource_not_modified(request, 'subnavigation')
    except Exception, e:
        logger.exception(e)
        return internal_server_error(request, e, sys.exc_info())
    return response_json(subnavigation)

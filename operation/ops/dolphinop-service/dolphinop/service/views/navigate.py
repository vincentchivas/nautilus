#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On November 5, 2012
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import sys
import logging
from django.views.decorators.http import require_GET
from dolphinop.service.views import response_json
from dolphinop.service.errors import parameter_error, internal_server_error
from dolphinop.service.models import navigatedb, contentdb

logger = logging.getLogger('dolphinop.service')

DEFAULT_SOURCE = 'ofw'


STATUS_DELETED = -1
STATUS_DISABLED = 0
STATUS_PREVIEW = 1
STATUS_PUBLISHED = 2

HOT_WORDS_ID = 1


@require_GET
def show_navigate(request):
    try:
        data = request.GET
        section = int(data.get('section', 1))
        package = data.get('pname', None)
        pn = data.get('pn', None)
        package = package or pn
        t = int(data.get('t', 0))
        cond = {
            'last_modified': {'$gt': t}
        }
        if package:
            cond['package'] = package

    except KeyError, e:
        logger.debug("URL:%s Exception:%s" % (request.build_absolute_uri(), e))
        return parameter_error(request, e)
    except Exception, e:
        logger.exception(e)
        return internal_server_error(request, e, sys.exc_info())
    try:
        sections = navigatedb.get_navigates(cond)
        result_sections = []
        hotwords_section = contentdb.get_section(
            {'layout': HOT_WORDS_ID, 'platform': 'Android_CN'})
        hotwords = []
        if hotwords_section:
            hotwords = hotwords_section['groups'][0]['cats'][0]['items']
        for item in sections:
            if item['status'] == STATUS_PUBLISHED:
                result_sections.append(item)
            elif item['status'] == STATUS_DELETED:
                dic = {
                    'id': item['id'],
                    'status': item['status'],
                    'last_modified': item['last_modified'],
                }
                result_sections.append(dic)
        if section:
            result_dict = {
                'hotwords': hotwords,
                'sections': result_sections,
            }
        else:
            result_dict = {
                'hotwords': hotwords,
            }
    except Exception, e:
        logger.exception(e)
        return internal_server_error(request, e, sys.exc_info())
    return response_json(result_dict)

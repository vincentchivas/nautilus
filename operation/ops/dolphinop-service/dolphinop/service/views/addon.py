#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# @Author : Jun Wang
# @Date : 2012-2-25
# Email: jwang@bainainfo.com

import logging
from django.views.decorators.http import require_GET
from dolphinop.service.views import response_json
from dolphinop.service.errors import parameter_error, resource_not_modified
from dolphinop.service.models import addondb
from dolphinop.utils import perf_logging

logger = logging.getLogger('dolphinop.service')

DEFAULT_SOURCE = 'ofw'


@require_GET
@perf_logging
def show_addons(request):
    try:
        source = request.GET.get('src', DEFAULT_SOURCE)
        cond = {
            "packagename": request.GET.get('pn'),
            "source": {"$in": [source, DEFAULT_SOURCE]}
        }
        last_modified = int(request.GET.get('mt', '0'))
    except Exception, e:
        logger.info("URL:%s Exception:%s" % (request.build_absolute_uri(), e))
        return parameter_error(request, e)
    addon = addondb.get_addon(cond, source)
    if not addon:
        return response_json({'lastModified': 0, 'items': []})
    elif addon['last_modified'] <= last_modified:
        return resource_not_modified(request, 'addon')
    return response_json(addon)

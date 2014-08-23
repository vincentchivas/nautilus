#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2013 Baina Info Inc. All rights reserved.
# Created On May 10, 2013
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import sys
import logging
from django.views.decorators.http import require_GET
from dolphinop.service.views import response_json, ALL_FLAG
from dolphinop.service.errors import parameter_error, resource_not_modified, internal_server_error
from dolphinop.service.models import notificationdb

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
def show_notifications(request):
    try:
        query = request.GET
        package = query.get('pn')
        source = query.get('src', 'ofw')
        version = int(query.get('vn', '0'))
        locale = query.get('locale')
        mt = int(query.get('mt', '0'))
    except Exception, e:
        logger.info(e)
        return parameter_error(request, e)
    try:
        cond = {
            'package': package,
            'sources.include': {'$in': [source, ALL_FLAG]},
            'sources.exclude': {'$ne': source},
            'max_version': {'$gte': version},
            'min_version': {'$lte': version},
        }
        if locale:
            cond['locales.include'] = {'$in': [locale, ALL_FLAG]}
            cond['locales.exclude'] = {'$ne': source}
        logger.info(cond)
        notifications = notificationdb.get_notifications(cond)
        if notifications:
            new_notifications = filter(
                lambda x: x['last_modified'] > mt, notifications)
            if new_notifications:
                result_dict = {
                    'notifications': notifications,
                    'last_modified': notifications[0]['last_modified']
                }
                return response_json(result_dict)
            else:
                return resource_not_modified(request, 'notification')
        else:
            result_dict = {
                'notifications': [],
                'last_modified': 0
            }
            return response_json(result_dict)
    except Exception, e:
        logger.error(e)
        return internal_server_error(request, e, sys.exc_info())

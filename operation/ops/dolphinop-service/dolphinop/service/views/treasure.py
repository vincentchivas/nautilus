#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On Dec 9, 2012
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import sys
import logging
from django.views.decorators.http import require_GET
from dolphinop.service.views import response_json, ALL_FLAG, OTHER, OPERATORS
from dolphinop.service.errors import parameter_error, internal_server_error, resource_not_modified
from dolphinop.service.models import treasuredb
from pymongo import DESCENDING

logger = logging.getLogger('dolphinop.service')


def _filter_items(items, t):
    results = []
    for item in items:
        if item['last_modified'] <= t and item['icon']['last_modified'] <= t:
            item = {'id': item['id']}
        elif item['icon']['last_modified'] <= t:
            del item['icon']
        results.append(item)
    return results


@require_GET
def show_treasure(request):
    try:
        query = request.GET
        package_name = query.get('pn')
        source = query.get('src', 'ofw')
        t = int(query.get('mt', 0))
        favorite = query.get('fa', None)
        operator = query.get('op', OTHER)
        if operator not in OPERATORS:
            operator = OTHER
    except Exception, e:
        logger.info(e)
        return parameter_error(request, e)
    try:
        cond = {
            'package': package_name,
            'sources.include': source,
            'sources.exclude': {'$ne': source},
            'time': {'$gt': t},
            'operators': operator
        }
        section_infos = treasuredb.get_treasuers(cond)
        if not section_infos:
            cond['sources.include'] = ALL_FLAG
            section_infos = treasuredb.get_treasuers(cond)
            if not section_infos:
                return resource_not_modified(request, 'treasure')
        favorites = []
        if favorite:
            favorites = favorite.split(',')
            try:
                favorites = map(int, favorites)
            except Exception, e:
                logger.error(e)
                favorites = []

        for section in section_infos:
            if 'hot_icon' in section and 'last_modified' in section['hot_icon']:
                if section['hot_icon']['last_modified'] <= t:
                    del section['hot_icon']
            updates = []
            if favorites:
                for item in section['updates']:
                    if item['id'] in favorites:
                        updates.append(item)
            updates = _filter_items(updates, t)
            section['updates'] = updates
            for group in section['groups']:
                for cat in group['cats']:
                    cat['items'] = _filter_items(cat['items'], t)

    except Exception, e:
        logger.error(e)
        return internal_server_error(request, e, sys.exc_info())
    return response_json(section_infos)


@require_GET
def show_treasure2(request):
    try:
        query = request.GET
        package_name = query.get('pn')
        source = query.get('src', 'ofw')
        t = int(query.get('mt', 0))
        version = int(query.get('vn', 0))
        operator = query.get('op', OTHER)
        if operator not in OPERATORS:
            operator = OTHER
    except Exception, e:
        logger.info(e)
        return parameter_error(request, e)
    try:
        cond = {
            'package': package_name,
            'sources.include': source,
            'sources.exclude': {'$ne': source},
            'last_modified': {'$gt': t},
            'operators': operator,
            'max_version': {'$gte': version},
            'min_version': {'$lte': version}
        }
        section_info = treasuredb.get_treasuer(
            cond, sort=[('min_version', DESCENDING)])
        if not section_info:
            cond['sources.include'] = ALL_FLAG
            section_info = treasuredb.get_treasuer(
                cond, sort=[('min_version', DESCENDING)])
            if not section_info:
                return resource_not_modified(request, 'treasure')

    except Exception, e:
        logger.error(e)
        return internal_server_error(request, e, sys.exc_info())
    if len(section_info) < 1:
        return resource_not_modified(request, 'treasure')

    section_info = section_info[0]
    return response_json(section_info)

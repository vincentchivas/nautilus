#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On Dec 21, 2012
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import sys
import logging
import re
from operator import itemgetter
from django.views.decorators.http import require_GET
from dolphinop.service.views import response_json
from dolphinop.service.errors import parameter_error, internal_server_error
from dolphinop.service.models import skindb
from dolphinop.service.utils.content import ALL_FLAG

logger = logging.getLogger('dolphinop.service')

PAGE_SIZE = 30


def _build_common_cond(package_name, version, source):
    cond = {
        '_rule.packages': {'$in': [package_name]},
        '_rule.sources.include': {'$in': [source, ALL_FLAG]},
        '_rule.sources.exclude': {'$ne': source},
        '_rule.max_version': {'$gte': version},
        '_rule.min_version': {'$lte': version},
    }
    return cond

def _adapt_fields(item, fields):
    dic = {}
    logger.debug(fields)
    for key in fields:
        if key == 'font_size':
            sign = {
                'kb': 1000,
                'k': 1000,
                'm': 1,
                'mb': 1,
            }
            item['size'] = str(item['size'])
            unit = re.search(r'kb|mb|b|m|k', item['size'].lower())
            tmp_size = float(re.search(r'[\d\.]+', item['size']).group())
            dic['size'] = tmp_size / sign[unit.group()] if unit else tmp_size
            continue

        if key == 'client_icon':
            logger.debug(item)
            if key in item:
                logger.debug('match client_icon')
                dic['client_icon'] = item[key]
            else:
                dic['client_icon'] = item['icon']
            continue

        #logger.debug('normal %s' % key)
        dic[key] = item[key]
    return dic


def _filter_skins(items, fields):
    for item in items:
        for key in item.keys():
            if key in fields:
                del item[key]


def _filter_fields(item, exlcude_fields):
    if type(item) == dict:
        _filter_skins([item], exlcude_fields)
    elif type(item) in (list, tuple):
        _filter_skins(item, exlcude_fields)


def _generate_inc(item, key, mt, fields):
    if item['last_modified'] > mt:
        item = _adapt_fields(item, fields)
    else:
        item = {key: item[key]}
    return item


def _filter_locale(items, locale):
    result = []
    for item in items:
        tmp_locale = item.get('locales', None)
        if tmp_locale != None:
            del item['locales']
        if not tmp_locale:
            result.append(item)
            continue
        if locale in tmp_locale or ALL_FLAG in tmp_locale:
            result.append(item)
            continue

    return result


@require_GET
def show_skins(request):
    try:
        query = request.GET
        package_name = query.get('pn')
        version = int(query.get('v', 1))
        source = query.get('src', 'ofw')
        c_version = int(query.get('cv', 1))
        page = int(query.get('page', 1))
        size = int(query.get('size', PAGE_SIZE))
        ty = query.get('type', 'skin')

    except Exception, e:
        logger.warning(e)
        return parameter_error(request, e)
    try:
        cond = _build_common_cond(package_name, version, source)
        cond['theme_type'] = ty
        if ty == 'skin':
            cond['c_version'] = c_version
        logger.debug(cond)
        skins = skindb.get_skins(cond, page, size)

        filter_fields = ('client_icon', 'package', 'sources', 'promote') if ty == 'font' else (
            'client_icon', 'package', 'sources', 'promote', 'uploader')
        _filter_skins(skins, filter_fields)

    except Exception, e:
        logger.error(e)
        return internal_server_error(request, e, sys.exc_info())
    return response_json(skins)


@require_GET
def show_skin_detail(request):
    try:
        query = request.GET
        skin_id = int(query.get('id'))
    except Exception, e:
        logger.warning(e)
        return parameter_error(request, e)
    try:
        cond = {
            'id': skin_id
        }
        logger.debug(cond)
        skin = skindb.get_skin(cond)
        _filter_fields(skin, ['sources', 'locales', 'pakcage', 'order', '_rule'])
    except Exception, e:
        logger.error(e)
        return internal_server_error(request, e, sys.exc_info())
    return response_json(skin)


@require_GET
def show_promote_skins(request):

    try:
        query = request.GET
        package_name = query.get('pn')
        version = int(query.get('v', 1))
        source = query.get('src', 'ofw')
        c_version = int(query.get('cv', 1))
        lc = query.get('lc')
        mt = int(query.get('mt', '0'))
    except Exception, e:
        logger.warning(e)
        return parameter_error(request, e)
    try:
        cond = _build_common_cond(package_name, version, source)
        cond['$or'] = [{'c_version': c_version}, {'theme_type': {'$ne': 'skin'}}]
        cond['promote'] = True
        logger.debug(cond)
        skin_list = skindb.get_skins(cond)
        last_modified = 0
        fonts = []
        skins = []
        wallpapers = []
        skin_list = _filter_locale(skin_list, lc)
        for i in skin_list:
            if i['last_modified'] > last_modified:
                last_modified = i['last_modified']
            if i['theme_type'] == 'skin':
                fields = ('uid', 'version', 'c_version', 'name',
                          'icon', 'download_url', 'client_icon', 'id', 'tag')
                item = _generate_inc(i, 'uid', mt, fields)
                skins.append(item)
            elif i['theme_type'] == 'wallpaper':
                fields = ('uid', 'name', 'icon', 'download_url',
                          'client_icon', 'id', 'tag')
                item = _generate_inc(i, 'uid', mt, fields)
                wallpapers.append(item)
            elif i['theme_type'] == 'font':
                fields = ('uid', 'name', 'client_icon', 'icon',
                          'download_url', 'tag', 'font_size', 'id')
                item = _generate_inc(i, 'uid', mt, fields)
                logger.debug(item)
                fonts.append(item)
        result = {
            'last_modified': last_modified,
            'skins': skins,
            'wallpapers': wallpapers,
            'fonts': fonts,
        }
    except Exception, e:
        logger.error(e)
        return internal_server_error(request, e, sys.exc_info())
    return response_json(result)


def get_skin_update(pn, source, vn, uid, cv):
    cond = {
        'uid': uid,
        'version': {'$gt': vn},
        'c_version': cv,
        'package': pn,
        'sources.include': {'$in': [source, ALL_FLAG]},
        'sources.exclude': {'$ne': source}
    }
    skin_list = skindb.get_skin_list(cond)
    result = None
    if len(skin_list) > 1:
        skin_list.sort(key=itemgetter('version'), reverse=True)
        max_version = skin_list[0]['version']
        max_list = filter(lambda x: x['version'] == max_version, skin_list)
        for skin in max_list:
            result = skin
            if source in skin['sources']['include']:
                break
    elif skin_list:
        result = skin_list[0]
    if result is not None:
        result = {
            'download_url': result['download_url'],
            'version_code': result['version'],
            'title': result['name'],
            'update_time': result['update_time'],
            'package_name': result['package'],
            'apk_size': result['size'],
            'uid': result['uid'],
            'type': 'skin'
        }
    return result


@require_GET
def get_banner_list(request):
    try:
        query = request.GET
        # skin_id = int(query.get('id'))
        locale = query.get('lc', 'zh_CN')
        package_name = query.get('pn')
        version = int(query.get('v', 1))
        source = query.get('src', 'ofw')
        c_version = int(query.get('cv', 1))
    except Exception, e:
        logger.warning(e)
        return parameter_error(request, e)

    cond = _build_common_cond(package_name, version, source)
    cond['c_version'] = {'$in': [0, c_version]}
    data = skindb.get_banner_list(cond)
    data = _filter_locale(data, locale)
    _filter_fields(data, ['sources', 'locales', '_rule'])

    return response_json(data)


def _get_subjects(cond={}):
    data = skindb.get_subject_list(cond)
    _filter_fields(data, ['sources', 'locales', 'package', 'items', '_rule'])
    return data


@require_GET
def get_subjects(request):
    try:
        query = request.GET
        locale = query.get('lc', 'zh_CN')
        package_name = query.get('pn')
        version = int(query.get('v', 1))
        source = query.get('src', 'ofw')
        c_version = int(query.get('cv', 1))
    except Exception, e:
        logger.warning(e)
        return parameter_error(request, e)

    cond = _build_common_cond(package_name, version, source)
    cond['c_version'] = {'$in': [0, c_version]}
    data = _get_subjects(cond)
    data = _filter_locale(data, locale)
    result = {
        'items': data,
    }
    return response_json(result)


@require_GET
def get_subject(request):
    try:
        query = request.GET
        subject_id = int(query.get('id'))
    except Exception, e:
        logger.warning(e)
        return parameter_error(request, e)

    cond = {"id": subject_id}
    logger.info(cond)

    except_cond = {"id": {"$ne": subject_id}}
    logger.info(except_cond)

    data = skindb.get_subject(cond)
    _filter_fields(data, ['sources', 'locales', 'package', '_rule'])

    other_subjects = _get_subjects(except_cond)
    data.update({'other_subjects': other_subjects})

    return response_json(data)

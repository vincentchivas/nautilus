#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# @Author : Jun Wang
# @Date : 2012-5-25
# Email: jwang@bainainfo.com

import logging
import sys
import time
import urllib
from operator import itemgetter
from django.utils import simplejson
from django.views.decorators.http import require_GET, require_POST
from dolphinop.utils import filter_fields, get_bool
from dolphinop.service.views import response_json, ALL_FLAG, ALL_WEIGHT, MATCH_WEIGHT, skin
from dolphinop.service.errors import parameter_error, resource_not_modified, internal_server_error
from dolphinop.service.models import updatedb
from dolphinop.utils import perf_logging

logger = logging.getLogger('dolphinop.service')

DEFAULT_SOURCE = 'ofw'
UPDATE_FIELDS = {
    'title': 1,
    'download_url': 1,
    'version_name': 1,
    'version_code': 1,
    'content_title': 1,
    'update_time': 1,
    'change_log': 1,
    'button': 1,
    'is_auto': 1,
    'is_force': 1,
    'apk_size': 1,
    'package': 1,
    'package_name': 1,
    'sources': 1,
}


@require_GET
@perf_logging
def show_update(request):
    """
    Get one update info.
    """
    try:
        data = request.GET
        package_name = data.get('pn')
        source = data.get('src', 'ofw')
        version = int(data.get('vn', 0))
        auto = data.get('auto', None)
        auto = True if auto and auto.lower() == 'true' else False
        did = data.get('did', None)
        app = _get_update(package_name, source, version,
                          auto, did, locale='ignore')
    except Exception, e:
        logger.exception(e)
        return parameter_error(request, e)
    if not app:
        return resource_not_modified(request, 'updateservice')
    return response_json(app)


@require_POST
@perf_logging
def show_update2(request):
    """
    Get update info by post method.
    """
    try:
        data = request.POST
        raw_post_data = request.raw_post_data
        raw_data = urllib.unquote(raw_post_data)
        data = simplejson.loads(raw_data)

        app_info = data.get('app')
        auto = get_bool(data.get('auto', None))
        did = data.get('did', None)
        lc = data.get('lc', None)
        update_list = []
        for item in app_info:
            update = _get_update(
                item['pn'], item['src'], item['vn'], auto, did, locale=lc)
            if update:
                update_list.append(update)
    except Exception, e:
        logger.exception(e)
        return internal_server_error(request, e, sys.exc_info())
    return response_json(update_list)


@require_POST
@perf_logging
def show_update3(request):
    """
    Get update info by post method.
    """
    try:
        raw_post_data = request.raw_post_data
        raw_data = urllib.unquote(raw_post_data)
        data = simplejson.loads(raw_data)

        app_info = data.get('app')
        auto = get_bool(data.get('auto', None))
        os_vn = data.get('osvn', None)
        cpu = data.get('cpu', None)
        mobile = data.get('md', None)
        did = data.get('did', None)
        update_list = []
        for item in app_info:
            update = _get_update(
                item['pn'], item['src'], item['vn'], auto, os_vn, cpu, mobile, did, 'ignore')
            if update:
                update['increment'] = False
                update_list.append(update)
    except Exception, e:
        logger.exception(e)
        return internal_server_error(request, e, sys.exc_info())
    return response_json(update_list)


@require_POST
@perf_logging
def show_update4(request):
    """
    Get update info by post method.
    """
    try:
        raw_post_data = request.raw_post_data
        raw_data = urllib.unquote(raw_post_data)
        data = simplejson.loads(raw_data)
        logger.debug(data)

        app_info = data.get('app')
        logger.debug(app_info)
        auto = get_bool(data.get('auto', None))
        os_vn = data.get('osvn', None)
        cpu = data.get('cpu', None)
        mobile = data.get('md', None)
        did = data.get('did', None)
        update_list = []
        for item in app_info:
            logger.debug(item)
            if item['type'] == 'dolphin':
                update = _get_update(item['pn'], item['asrc'].strip(),
                                     item['vn'], auto, os_vn, cpu, mobile, did, 'ignore')
                logger.debug(update)
                if update:
                    increment_info = _get_incremnt(
                        item['hash'], update['version_code'])
                    if increment_info:
                        update['apk_url'] = update['download_url']
                        update['download_url'] = increment_info['url']
                        update['inc_size'] = increment_info['inc_size']
                        update['hashcode'] = increment_info['hashcode']
                        update['increment'] = True
                    else:
                        update['increment'] = False
                    logger.debug(update)
                    update_list.append(update)
            elif item['type'] == 'skin':
                update = skin.get_skin_update(
                    item['pn'], item['asrc'].strip(), int(item['vn']), item['uid'], int(item['cv']))
                if update:
                    update_list.append(update)
        logger.debug(update_list)
    except Exception, e:
        logger.exception(e)
        return internal_server_error(request, e, sys.exc_info())
    return response_json(update_list)


def _generate_filter(package_name, source, version, auto=None, os_vn=None, cpu=None, mobile=None):
    cond = {
        "package": package_name,
        "min_version": {"$lte": version},
        "max_version": {"$gte": version},
    }
    now = int(time.time())
    cond['valid_time'] = {'$lte': now}
    cond['invalid_time'] = {'$gte': now}
    if source:
        cond["sources.include"] = {'$in': [source, ALL_FLAG]}
        cond["sources.exclude"] = {'$ne': source}
    if auto:
        cond['is_auto'] = True
        if os_vn:
            cond['os_versions.include'] = {'$in': [os_vn, ALL_FLAG]}
            cond['os_versions.exclude'] = {'$ne': os_vn}
        if cpu:
            cond['cpus.include'] = {'$in': [cpu, ALL_FLAG]}
            cond['cpus.exclude'] = {'$ne': cpu}
        if mobile:
            cond['mobiles.include'] = {'$in': [mobile, ALL_FLAG]}
            cond['mobiles.exclude'] = {'$ne': mobile}
    else:
        if os_vn:
            cond['manual_os_versions.include'] = {'$in': [os_vn, ALL_FLAG]}
            cond['manual_os_versions.exclude'] = {'$ne': os_vn}
        if cpu:
            cond['manual_cpus.include'] = {'$in': [cpu, ALL_FLAG]}
            cond['manual_cpus.exclude'] = {'$ne': cpu}
        if mobile:
            cond['manual_mobiles.include'] = {'$in': [mobile, ALL_FLAG]}
            cond['manual_mobiles.exclude'] = {'$ne': mobile}
    return cond


def _get_incremnt(old_hash, version):
    cond = {
        'signs': old_hash,
        'new_version': version
    }
    patch = updatedb.get_update_patch(cond)
    if patch:
        return patch
    else:
        return None


def _calculate_rate(dict_data, key_values):
    rate = 0
    for key, value in key_values:
        condition = dict_data[key]['include']
        if isinstance(condition, (str, unicode)):
            if value == condition:
                rate += MATCH_WEIGHT
            else:
                rate += ALL_WEIGHT
        elif isinstance(condition, list):
            if value in condition:
                rate += MATCH_WEIGHT
            else:
                rate += ALL_WEIGHT
        else:
            raise TypeError('condition type should by str or list')
    return rate


def _rating_updates(data_list, key_values):
    for item in data_list:
        rate = _calculate_rate(item, key_values)
        item['rating'] = rate
    data_list.sort(key=itemgetter('rating', 'last_modified'), reverse=True)
    return data_list


def _check_sample(item, did):
    if did is None:
        return True
    sample = item['sample']
    if sample > 0:
        sample_count = updatedb.get_sample_count({'id': item['id']})
        if sample_count < sample:
            updatedb.update_sample_device({'id': item['id'], 'did': did})
            return True
        else:
            exist = updatedb.check_sample_device(
                {'id': item['id'], 'did': did})
            if exist:
                return True
            else:
                return False
    else:
        return True


def _filter_locale(items, locale):
    common = []
    special = []
    if locale == 'ignore':
        return items
    for item in items:
        tmp_locale = item.get('locales', None)
        if tmp_locale != None:
            del item['locales']
        if not tmp_locale:
            common.append(item)
            continue
        if locale in tmp_locale:
            special.append(item)
            continue

    return special if len(special) else common


def _get_update(pname, source, version, auto=None, os_vn=None, cpu=None, mobile=None, did=None, locale=None):
    cond = _generate_filter(pname, source, version, auto, os_vn, cpu, mobile)
    logger.debug(cond)
    updates = updatedb.get_updateservices(cond)
    logger.debug(updates)
    key_values = [
        ('sources', source),
        ('os_versions', os_vn),
        ('cpus', cpu),
        ('mobiles', mobile),
    ]
    updates = _filter_locale(updates, locale)
    _rating_updates(updates, key_values)
    for item in updates:
        check = _check_sample(item, did)
        if check:
            return filter_fields(item, UPDATE_FIELDS)
    return None

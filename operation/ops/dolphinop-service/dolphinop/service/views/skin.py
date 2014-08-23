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
from django.http import HttpResponse as http
from django.views.decorators.http import require_GET
from dolphinop.db.base import MongodbStorage
from dolphinop.service.views import response_json
from dolphinop.service.utils.content import ALL_FLAG, SKIN_ORIGINIZE, RULE_ORIGINIZE, SKIN_PARAS
from dolphinop.service.errors import parameter_error, internal_server_error
from dolphinop.service.utils.common_op import get_params, get_cond

SKIN_DB = MongodbStorage()
setattr(SKIN_DB, 'table', 'skin')
ORIGIN = SKIN_ORIGINIZE
ORIGIN.update(RULE_ORIGINIZE)
logger = logging.getLogger('dolphinop.service')

PAGE_SIZE = 30


def _adapt_fields(item, fields, types=None):
    dic = {}
    if types == 'font':
        sign = {'kb': 1000, 'k': 1000, 'm': 1, 'mb': 1}
        item['size'] = str(item['size'])
        unit = re.search(r'kb|mb|b|m|k', item['size'].lower())
        tmp_size = float(re.search(r'[\d\.]+', item['size']).group())
        dic['size'] = tmp_size / sign[unit.group()] if unit else tmp_size
        dic['icon'] = item['client_icon']
        for key in fields:
            if key not in ['icon', 'size', 'client_icon', 'font_size']:
                dic[key] = item[key]
    else:
        for key in fields:
            if types:
                dic[key] = item[key]
            else:
                for k in fields:
                    formats = k.split('.')
                    if len(formats) == 2 and formats[1] in item['_rule'].keys():
                            del item['_rule'][formats[1]]
                    elif k in item.keys():
                        del item[k]
    return dic


def _generate_inc(item, key, mt, fields, types=None):
    if item['last_modified'] > mt:
        item = _adapt_fields(item, fields, types)
    else:
        item = {key: item[key]}
    return item

@require_GET
def show_skins(request):
    try:
        args = get_params(request, 'get', SKIN_PARAS)
        if isinstance(args, http):
            return args
        fields = ('pn', 'cv', 'type', 'page', 'size', 'src')
        cond = get_cond(args, ORIGIN, fields)
        skins = SKIN_DB.get_paging_items(cond, {'_id': 0}, args['page'], args['size'])
        #parse_rule(skins, args, {'src': 'sources'}, {'especial': ['src']})
        filter_fields = ['client_icon', '_rule.packages',
                         '_rule.sources', 'promote', 'uploader']
        if args['type'] == 'font':
            del filter_fields[-1]
        for item in skins:
            _adapt_fields(item, filter_fields)
    except Exception, e:
        logger.error(e)
        return internal_server_error(request, e, sys.exc_info())
    return response_json(skins)

@require_GET
def show_skin_detail(request):
    try:
        skin_id = int(request.GET.get('id'))
    except Exception, e:
        logger.warning(e)
        return parameter_error(request, 'id')
    try:
        cond = {'id': skin_id}
        logger.debug(cond)
        skin = None
        if SKIN_DB.get_item(cond, {'id':0}):
            skin = SKIN_DB.get_item(cond, {'_id': 0})[0]
    except Exception, e:
        logger.error(e)
        return internal_server_error(request, e, sys.exc_info())
    return response_json(skin)

@require_GET
def show_promote_skins(request):
    try:
        local_paras = SKIN_PARAS + ['lc&BeNone','vn&option&0']
        args = get_params(request, 'get', local_paras)
        if isinstance(args, http):
            return args
        fields = ('pn', 'vn', 'lc', 'src')
        cond = get_cond(args, ORIGIN, fields)
        if(args['pn'] == 'com.dolphin.browser.xf'):
            cond.pop('_rule.min_version')
            cond.pop('_rule.max_version')
        elif args['vn'] == '0':
            cond.update({'_rule.min_version':0, '_rule.max_version':0})

        cond.update({'promote': True})
        logger.debug(cond)
        skin_list = SKIN_DB.get_item(cond, {'_id': 0})
        last_modified = 0
        if skin_list:
            skin_list.sort(key=itemgetter('last_modified'), reverse=True)
            last_modified = skin_list[0]['last_modified']
        skin_fields = {
            'skin': ['uid', 'name', 'icon', 'download_url', 'version', 'c_version'],
            'wallpaper': ['uid', 'name', 'icon', 'download_url'],
            'font': ['uid', 'name', 'client_icon', 'download_url', 'tag', 'font_size']
        }
        store = {}
        for key in skin_fields:
            store[key] = []
        for i in skin_list:
            if i['theme_type'] == 'skin' and i['c_version'] != args['cv']:
                continue
            if i['theme_type'] in skin_fields:
                item = _generate_inc(
                    i, 'uid', args['mt'], skin_fields[i['theme_type']], i['theme_type'])
                store[i['theme_type']].append(item)
        result = {
            'last_modified': last_modified,
            'skins': store['skin'],
            'wallpapers': store['wallpaper'],
            'fonts': store['font'],
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
    skin_list = SKIN_DB.get_item(cond, {'id':0})
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
                'package_name': pn,
                'apk_size': result['size'],
                'uid': result['uid'],
                'type': 'skin'
                }
    return result

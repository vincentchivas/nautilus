#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On September 12, 2012
# @Author : Jun Wang
# Email: jwang@bainainfo.com

import logging
import sys
import random
from django.views.decorators.http import require_GET
from dolphinop.service.views import response_json
from dolphinop.service.errors import parameter_error, internal_server_error, resource_not_modified
from dolphinop.service import models

logger = logging.getLogger('dolphinop.service')

DEFAULT_SOURCE = 'ofw'
DEFAULT_ACTION = 'false'
ALL_FLAG = 'all_condition'


@require_GET
def show_preset(request):
    data = request.GET
    try:
        os = data.get('os', '').lower()
        package = data.get('pname')
        source = data.get('src', DEFAULT_SOURCE)
        locale = data.get('l')
        version = int(data.get('v', 0))
        #os_version = data.get('sdk')
        #operator = data.get('no')
        #mobile = data.get('dt')
        #resolution = data.get('re')
        no_default_str = data.get('nd', DEFAULT_ACTION).lower()
        bool_map = {
            'true': True,
            'false': False
        }
        no_default = bool_map[no_default_str]
    except Exception, e:
        logger.debug("URL:%s Exception:%s" % (request.build_absolute_uri(), e))
        return parameter_error(request, e)
    try:
        cond = {
            'os': os,
            'package': package,
            'sources': {'$in': [source, ALL_FLAG]},
            #'os_versions': {'$in': [os_version, ALL_FLAG]},
            #'operators': {'$in': [operator, ALL_FLAG]},
            #'mobiles': {'$in': [mobile, ALL_FLAG]},
            #'resolutions': {'$in': [resolution, ALL_FLAG]},
            'locale': locale,
            '$or': [
                {'min_version': {'$lte': version},
                    'max_version': {'$gte': version}},
                {'min_version': 0, 'max_version': 0}
            ]
        }
        logger.debug(cond)
        presets = models.get_presets(cond)
        logger.debug(presets)
        preset_num = len(presets)
        if preset_num >= 2:
            if preset_num > 2:
                logger.warning('preset data error')
            rand = random.randint(0, 1)
            preset = presets[rand]
            preset['strategy'] = preset['strategies'][0]
        elif preset_num == 1:
            preset = presets[0]
            strategies = preset['strategies']
            strategies_num = len(strategies)
            if strategies_num >= 2:
                if strategies_num > 2:
                    logger.warning('preset strategy error')
                rand = random.randint(0, 1)
                preset['strategy'] = strategies[rand]
            elif len(strategies) == 1:
                preset['strategy'] = strategies[0]
            else:
                logger.error('Preset Strategy is none')
                preset['strategy'] = None
        elif preset_num == 0:
            preset = None
            if no_default:
                cond['sources'] = DEFAULT_SOURCE
                preset = models.get_preset(cond)
        logger.debug(preset)
        if isinstance(preset, dict) and 'strategies' in preset:
            del preset['strategies']
    except Exception, e:
        logger.exception(e)
        return internal_server_error(request, e, sys.exc_info())
    if not preset:
        return resource_not_modified(request, 'preset')

    return response_json(preset)

#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# @Author : Jun Wang
# @Date : 2012-2-25
# Email: jwang@bainainfo.com
import logging
from dolphinop.db import dbperf_logging
from pymongo import DESCENDING
logger = logging.getLogger('dolphinop.db')

_db = None

DEFAULT_SOURCE = 'ofw'

DISPLAY_FIELDS = {
    '_id': 0,
    'last_modified': 1,
    'items': 1,
    'source': 1,
}


@dbperf_logging
def get_addon(cond, source):
    sort = [('timestamp', DESCENDING)]
    addon_colls = _db.addon.find(cond, sort=sort, fields=DISPLAY_FIELDS)
    addon = None
    addon_default = None
    for item in addon_colls:
        if source == item['source']:
            addon = item
            break
        if DEFAULT_SOURCE == item['source']:
            addon_default = item
    if not addon:
        addon = addon_default
    if addon:
        del addon['source']
    return addon

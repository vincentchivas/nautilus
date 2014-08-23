#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On September 12, 2012
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import logging
from dolphinop.db import connect, cursor_to_array
logger = logging.getLogger('dolphinop.db')

_db = None
_preset = None


DISPLAY_FIELDS = {
    '_id': 0,
    'os': 0,
    'locale': 0,
    'platform': 0,
    'min_version': 0,
    'max_version': 0,
    'package': 0,
    'sources': 0,
    'os_versions': 0,
    'mobiles': 0,
    'operators': 0,
    'resolutions': 0,
}


def config(server, db, port=None):
    # check the server and db.
    assert server and db, 'Either "host" or "db" should not be None'
    global _db, _preset
    try:
        conn = connect(server, port)
    except Exception, e:
        logger.debug(e)
    _db = conn[db]
    _preset = _db['preset']


def get_preset(cond):
    preset = _preset.find_one(cond, fields=DISPLAY_FIELDS)
    return preset


def get_presets(cond):
    colls = _preset.find(cond, fields=DISPLAY_FIELDS)
    return cursor_to_array(colls)

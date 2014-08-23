#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On Dec 7, 2012
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import logging
from dolphinop.db import connect, cursor_to_array
logger = logging.getLogger('dolphinop.db')

_db = None


DISPLAY_FIELDS = {
    '_id': 0,
    'platform': 0,
    'packages': 0,
    'sources': 0,
}

TREASURE_FIELDS = {
    '_id': 0,
    'last_modified': 1,
    'items': 1,
}


def config(server, db, port=None):
    # check the server and db.
    assert server and db, 'Either "host" or "db" should not be None'
    global _db
    try:
        conn = connect(server, port)
    except Exception, e:
        logger.debug(e)
    _db = conn[db]


def get_treasuers(cond):
    colls = _db.treasure_section.find(cond, fields=DISPLAY_FIELDS)
    return cursor_to_array(colls)


def get_treasuer(cond, sort=None):
    return cursor_to_array(_db.treasure.find(cond, fields=TREASURE_FIELDS, sort=sort))

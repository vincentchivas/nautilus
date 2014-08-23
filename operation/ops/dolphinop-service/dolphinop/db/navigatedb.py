#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On November 5, 2012
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import logging
from dolphinop.db import connect, cursor_to_array
logger = logging.getLogger('dolphinop.db')

_db = None


DISPLAY_FIELDS = {
    '_id': 0,
    'packages': 0,
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


def get_navigate(cond):
    navigate = _db.navigate.find_one(cond, fields=DISPLAY_FIELDS)
    return navigate


def get_navigates(cond):
    colls = _db.navigate.find(cond, fields=DISPLAY_FIELDS)
    return cursor_to_array(colls)

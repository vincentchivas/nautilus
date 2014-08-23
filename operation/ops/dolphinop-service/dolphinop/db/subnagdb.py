#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On August 25, 2012
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import logging
from dolphinop.db import cursor_to_array

logger = logging.getLogger('dolphinop.db')

_db = None
_subnavigation = None


DISPLAY_FIELDS = {
    '_id': 0,
    'title': 1,
    'last_modified': 1,
    'categories': 1,
}
DETAIL_FIELDS = {
    '_id': 0,
}


def get_subnavigation(cond):
    subnavigation = _db.subnavigation.find_one(cond, fields=DISPLAY_FIELDS)
    return subnavigation


def get_subnavigations(cond):
    subnavigations = _db.subnavigation.find(cond, fields=DETAIL_FIELDS)
    return cursor_to_array(subnavigations)


def update_subnavigation(cond, data):
    _db.subnavigation.update(cond, data)

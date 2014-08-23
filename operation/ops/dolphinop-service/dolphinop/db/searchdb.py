#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On Jan 14, 2012
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import logging
from dolphinop.db import cursor_to_array
logger = logging.getLogger('dolphinop.db')

_db = None


DISPLAY_FIELDS = {
    '_id': 0,
    'packages': 0,
    'sources': 0,
}


def get_search_categories(cond, fields=DISPLAY_FIELDS):
    colls = _db.search_category.find(cond, fields=fields)
    return cursor_to_array(colls)


def update_search_category(cond, data):
    _db.search_category.update(cond, data, upsert=True)


def get_search_keywords(cond, fields=DISPLAY_FIELDS):
    colls = _db.search_keyword.find(cond, fields=fields)
    return cursor_to_array(colls)


def get_push_messages(cond, fields=DISPLAY_FIELDS):
    colls = _db.push_messages.find(cond, fields=fields)
    return cursor_to_array(colls)


def get_push_messages_new(cond, fields=DISPLAY_FIELDS):
    colls = _db.push_messages_new.find(cond, fields=fields)
    return cursor_to_array(colls)

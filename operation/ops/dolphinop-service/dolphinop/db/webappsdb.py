#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On Apr 18, 2013
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import logging
from dolphinop.db import cursor_to_array, dbperf_logging

logger = logging.getLogger('dolphinop.db')

_db = None

PAGE_SIZE = 20

DISPLAY_FIELDS = {
    '_id': 0,
}


@dbperf_logging
def get_list(coll, cond, sort=None, fields=DISPLAY_FIELDS, page=1, page_size=PAGE_SIZE):
    '''
    Get array data of specified collection.
    '''
    collection = _db[coll]
    result_cursor = collection.find(cond, fields=fields, sort=sort).skip(
        page * page_size).limit(page_size)
    return cursor_to_array(result_cursor)


@dbperf_logging
def get_obj(coll, cond, fields=DISPLAY_FIELDS):
    '''
    Get object data of specified collection.
    '''
    collection = _db[coll]
    return collection.find_one(cond, fields=fields)

#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On Dec 21, 2012
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import logging
from pymongo import ASCENDING
from dolphinop.db import cursor_to_array, dbperf_logging
logger = logging.getLogger('dolphinop.db')

_db = None


BRIEF_FIELDS = {
    '_id': 0,
    'id': 1,
    'icon': 1,
    'name': 1,
    'badge': 1,
}

DISPLAY_FIELDS = {
    '_id': 0,
}


@dbperf_logging
def get_skins(cond, page=1, page_size=30):
    colls = _db.skin.find(cond, fields=DISPLAY_FIELDS).sort(
        [('order', ASCENDING)]).skip((page - 1) * page_size).limit(page_size)
    return cursor_to_array(colls)


@dbperf_logging
def get_skin_list(cond):
    colls = _db.skin.find(cond, fields=DISPLAY_FIELDS)
    return cursor_to_array(colls)


@dbperf_logging
def get_skin(cond):
    colls = _db.skin.find_one(cond, fields=DISPLAY_FIELDS)
    return colls


@dbperf_logging
def get_banner_list(cond):
    colls = _db.skin_banner.find(
        cond, fields=DISPLAY_FIELDS).sort([('order', ASCENDING)])
    return cursor_to_array(colls)


@dbperf_logging
def get_subject_list(cond):
    colls = _db.skin_subject.find(
        cond, fields=DISPLAY_FIELDS).sort([('order', ASCENDING)])
    return cursor_to_array(colls)


@dbperf_logging
def get_subject(cond):
    colls = _db.skin_subject.find_one(cond, fields=DISPLAY_FIELDS)
    return colls

#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On Jan 6, 2012
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import logging
from dolphinop.db import cursor_to_array

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


def get_adverts(cond):
    colls = _db.advert.find(cond, fields=DISPLAY_FIELDS)
    return cursor_to_array(colls)


def get_advert(cond):
    coll = _db.advert.find_one(cond, fields=DISPLAY_FIELDS)
    return coll


def save_advert_track(data):
    _db.advert_track.save(data)

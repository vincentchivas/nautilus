#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On Apr 6, 2013
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import logging
from pymongo import DESCENDING
from dolphinop.db import cursor_to_array

logger = logging.getLogger('dolphinop.db')

_db = None


DISPLAY_FIELDS = {
    '_id': 0,
}


MODE_FIELDS = {
    '_id': 0,
    'title': 0,
    'icon': 0,
    'dolphin_download': 0,
    'package': 0,
    'sources': 0,
    'min_version': 0,
    'max_version': 0,
}


def get_game(cond):
    return _db.gamemode.find_one(cond, fields=DISPLAY_FIELDS)


def get_modes(cond):
    colls = _db.gamemode.find(cond, fields=MODE_FIELDS).sort(
        [('last_modified', DESCENDING)])
    return cursor_to_array(colls)

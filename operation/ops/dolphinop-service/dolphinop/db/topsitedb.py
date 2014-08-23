#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2013 Baina Info Inc. All rights reserved.
# Created On Apr 24, 2013
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import logging
from pymongo import DESCENDING
from dolphinop.db import cursor_to_array, dbperf_logging

logger = logging.getLogger('dolphinop.db')

_db = None


DISPLAY_FIELDS = {
    '_id': 0,
    'id': 1,
    'url': 1,
    'color': 1,
    'icon': 1,
    'last_modified': 1,
}


@dbperf_logging
def get_sites(cond):
    colls = _db.topsite.find(cond, fields=DISPLAY_FIELDS).sort(
        [('last_modified', DESCENDING)])
    return cursor_to_array(colls)

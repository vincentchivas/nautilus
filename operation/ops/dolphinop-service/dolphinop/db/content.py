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


def get_content_data(cond, fields=DISPLAY_FIELDS):
    colls = _db.content.find(cond, fields=fields)
    return cursor_to_array(colls)

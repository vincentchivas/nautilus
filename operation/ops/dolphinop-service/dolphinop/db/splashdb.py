#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On August 3, 2012
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import logging
logger = logging.getLogger('dolphinop.db')

_db = None
_splashscreen = None


DISPLAY_FIELDS = {
    '_id': 0,
}


def get_splashscreens(cond):
    splashscreens = _db.splashscreen.find(cond, fields=DISPLAY_FIELDS)
    return splashscreens

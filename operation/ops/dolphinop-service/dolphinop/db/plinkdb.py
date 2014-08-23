#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On August 3, 2012
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import logging

logger = logging.getLogger('dolphinop.db')

_db = None


DISPLAY_FIELDS = {
    '_id': 0,
    'id': 1,
    'Title': 1,
    'Url': 1,
    'Source': 1,
    'UrlImp': 1,
    'roms': 1,
    'rom_action': 1,
    'last_modified': 1,
    'status': 1,
    'images': 1,
    'weight': 1,
    'locales': 1,
    'pop': 1,
    'subtitle': 1,
    '_rule': 1
}


def get_promotionlink(cond):
    colls = _db.promotionlink.find(cond, fields=DISPLAY_FIELDS)
    plinks = [item for item in colls]
    return plinks

#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On Jan 25, 2013
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import logging
import time
from pymongo import DESCENDING, ASCENDING

logger = logging.getLogger('dolphinop.db')

_db = None

_INDEXES = {
    'iptable': [
        [('start_int', ASCENDING), ('end_int', ASCENDING),
         ('timestamp', DESCENDING)]
    ],
}


def get_info_by_ip(ip_int, valid_time):
    now = int(time.time())
    cond = {
        "start_int": {"$lte": ip_int},
        "end_int": {"$gte": ip_int},
        "timestamp": {"$gte": now - valid_time}
    }
    coll = _db.iptable.find_one(cond)
    return coll


def save_ip(dic):
    _db.iptable.save(dic)

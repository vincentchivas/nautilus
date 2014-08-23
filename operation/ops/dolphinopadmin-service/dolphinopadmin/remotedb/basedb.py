#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2013 Baina Info Inc. All rights reserved.
# Created On Apr 3, 2013
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import logging

_db = {}

logger = logging.getLogger('dolphinopadmin.remotedb')


def update_data(coll, cond, data, server, replace=True):
    assert coll  # coll can't be null.
    logger.info(data.keys())
    logger.info(cond)
    logger.info(replace)
    collection = _db[server][coll]
    if replace:
        status = collection.update(cond, data, upsert=True)
    else:
        status = collection.update(cond, {'$set': data}, upsert=True)
    return status


def delete_data(coll, cond, server):
    assert coll  # coll can't be null.
    collection = _db[server][coll]
    status = collection.remove(cond)
    return status

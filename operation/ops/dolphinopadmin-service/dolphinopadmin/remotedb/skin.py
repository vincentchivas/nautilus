#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On Dec 6, 2012
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import logging
from dolphinopadmin.remotedb import connect

_db = {}

logger = logging.getLogger('dolphinopadmin.remotedb')


def config(servers):
    global _db
    for key, value in servers.iteritems():
        try:
            conn = connect(value['host'], value['port'])
            _db[key] = conn[value['db']]
        except Exception, e:
            logger.error(e)


def update_skin(cond, data, server):
    skin = _db[server].skin.find_one({'id': cond['id']})
    if not skin and 'downloads' not in data:
        data['downloads'] = 0
    status = _db[server].skin.update(cond, {'$set': data}, upsert=True)
    return status


def delete_skin(cond, server):
    status = _db[server].skin.remove(cond)
    return status

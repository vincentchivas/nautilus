#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On November 5, 2012
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import time
import logging
from dolphinopadmin.remotedb import connect

STATUS_DELETED = -1
STATUS_DISABLED = 0
STATUS_PREVIEW = 1
STATUS_PUBLISHED = 2

_db = None
_section = {}

logger = logging.getLogger('dolphinopadmin.remotedb')


def config(servers):
    global _db, _section
    for key, value in servers.iteritems():
        try:
            conn = connect(value['host'], value['port'])
            _db = conn[value['db']]
            _section[key] = _db['navigate']
        except Exception, e:
            logger.error(e)


def update_section(cond, data, server):
    data['status'] = STATUS_PUBLISHED
    status = _section[server].update(cond, data, upsert=True)
    return status


def delete_section(cond, server):
    update = {'$set':
              {'status': STATUS_DISABLED, 'last_modified': int(time.time())}}
    status = _section[server].update(cond, update)
    return status

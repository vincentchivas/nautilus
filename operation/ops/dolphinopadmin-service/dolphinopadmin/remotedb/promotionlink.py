#!/usr/bin/env python
# coding: utf-8
'''
Copyright (c) 2012 Baina Info Inc. All rights reserved.
@Author : Jun Wang
@Date : 2012-2-24
'''

import logging
import time
from dolphinopadmin.remotedb import connect

STATUS_DELETED = -1
STATUS_DISABLED = 0
STATUS_PREVIEW = 1
STATUS_PUBLISHED = 2

_db = None
_plink = {}


logger = logging.getLogger('dolphinopadmin.remotedb')


def config(servers):
    global _db, _plink
    for key, value in servers.iteritems():
        try:
            conn = connect(value['host'], value['port'])
            _db = conn[value['db']]
            _plink[key] = _db['promotionlink']
        except Exception, e:
            logger.error(e)


def update_plink(cond, data, server):
    data['status'] = STATUS_PUBLISHED
    status = _plink[server].update(cond, data, True)
    return status


def delete_plink(cond, server):
    update = {'$set':
              {'status': STATUS_DISABLED, 'last_modified': int(time.time())}}
    status = _plink[server].update(cond, update)
    return status

#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On February 25, 2012
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import logging
from dolphinopadmin.remotedb import connect

_db = None
_category = {}
_subject = {}
_application = {}
_feature = {}
_hoting = {}

logger = logging.getLogger('dolphinopadmin.remotedb')


def config(servers):
    global _db, _category, _application, _feature, _hoting
    for key, value in servers.iteritems():
        try:
            conn = connect(value['host'], value['port'])
            _db = conn[value['db']]
            _category[key] = _db['addon_category']
            _application[key] = _db['addon_application']
            _feature[key] = _db['addon_feature']
            _hoting[key] = _db['addon_hoting']
            _subject[key] = _db['addon_subject']
        except Exception, e:
            logger.error(e)


def update_category(cond, data, server):
    status = _category[server].update(cond, data, True)
    return status


def update_subject(cond, data, server):
    status = _subject[server].update(cond, data, True)
    return status


def update_application(cond, data, server):
    status = _application[server].update(cond, data, True)
    return status


def update_feature(cond, data, server):
    status = _feature[server].update(cond, data, True)
    return status


def update_hoting(cond, data, server):
    status = _hoting[server].update(cond, data, True)
    return status


def delete_category(cond, server):
    status = _category[server].remove(cond)
    return status


def delete_subject(cond, server):
    status = _subject[server].remove(cond)
    return status


def delete_application(cond, server):
    status = _application[server].remove(cond)
    return status


def delete_feature(cond, server):
    status = _feature[server].remove(cond)
    return status


def delete_hoting(cond, server):
    status = _hoting[server].remove(cond)
    return status

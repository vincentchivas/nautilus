#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2013 Baina Info Inc. All rights reserved.
# Created On May 16, 2013
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import logging

_db = {}

logger = logging.getLogger('dolphinopadmin.remotedb')


def update_app(cond, data, server):
    collection = _db[server]['webapps_application']
    status = collection.update(cond, {'$set': data}, upsert=True)
    return status


def update_data(cond, data, server):
    collection = _db[server]['webapps_application']
    status = collection.update(
        cond, {'$addToSet': {'subjects': {'id': data['subject_id'], 'order': data['order']}}})
    return status


def delete_data(cond, data, server):
    collection = _db[server]['webapps_application']
    status = collection.update(
        cond, {'$pull': {'subjects': {'id': data['id'], 'order': data['order']}}})
    return status

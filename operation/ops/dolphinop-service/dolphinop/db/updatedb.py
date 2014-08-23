#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# @Author : Jun Wang
# @Date : 2012-5-25
# Email: jwang@bainainfo.com
import logging
from datetime import datetime
from dolphinop.db import cursor_to_array
logger = logging.getLogger('dolphinop.db')

_db = None

DISPLAY_FIELDS = {
    '_id': 0,
}

PATCH_FIELDS = {
    '_id': 0,
}


def get_updateservices(cond):
    """
    Get update info.
    """
    updateservices = _db.updateservice.find(cond, fields=DISPLAY_FIELDS)
    return cursor_to_array(updateservices)


def get_update_patch(cond):
    """
    Get update patch url.
    """
    patch = _db.update_patch.find_one(cond, fields=PATCH_FIELDS)
    return patch


def get_sample_count(cond):
    """
    Get sample count.
    """
    return _db.update_sample.find(cond).count()


def update_sample_device(cond):
    """
    Update sample device.
    """
    data = {
        'id': cond['id'],
        'did': cond['did'],
        'last_modified': datetime.now()
    }
    _db.update_sample.update(cond, data, upsert=True)


def check_sample_device(cond):
    """
    Check sample device existing
    """
    return _db.update_sample.find_one(cond)

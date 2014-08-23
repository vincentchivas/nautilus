#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2013 Baina Info Inc. All rights reserved.
# Created On May 23, 2013
# @Author : Jun Wang
# Email: jwang@bainainfo.com

import datetime


def now():
    return datetime.datetime.utcnow()


def forever():
    return datetime.datetime.strptime("2113-05-30", "%Y-%m-%d")


def set_order(obj, key='order', obj_list=None):
    if obj_list is None:
        obj_list = obj.__class__.objects.order_by(key)
    max_order = len(obj_list)
    new_order = getattr(obj, key)
    if new_order > max_order:
        new_order = max_order
    elif new_order < 1:
        new_order = 1
    sort_list = [i for i in obj_list if obj.id != i.id]
    sort_list.insert(new_order - 1, obj)
    order = 1
    for item in sort_list:
        setattr(item, key, order)
        order += 1
        item.save()

#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On September 26, 2012
# @Author : Jun Wang
# Email: jwang@bainainfo.com

from dolphinop.service.views import response_json


def show_recommends(request):
    """
    Get engine recommend strategy.
    """
    return response_json([])

#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On Jan 29, 2013
# @Author : Jun Wang
# Email: jwang@bainainfo.com
from django import forms


class ApkForm(forms.Form):
    product = forms.CharField(max_length=100)
    hash_code = forms.CharField(max_length=50)
    apk = forms.FileField()

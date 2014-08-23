#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2013 Baina Info Inc. All rights reserved.
# Created On Jan 25, 2013
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import logging
from django.db import models
from django.conf import settings
from dolphinopadmin.updateservice.models.update_base import Sign, Patch, File
from dolphinopadmin.configure.models import Package

logger = logging.getLogger('dolphinopadmin.admin')

XF_PACKAGE = 'com.dolphin.browser.xf'

MEDIA_ROOT = settings.MEDIA_ROOT


def get_xf_package():
    try:
        package_obj = Package.objects.get(uid=XF_PACKAGE)
        return package_obj
    except:
        package_obj = Package(name='海豚浏览器炫风版', uid=XF_PACKAGE)
        package_obj.save()
        return package_obj


class XFSign(Sign):
    package = models.ForeignKey(Package)

    class Meta:
        verbose_name = '中文海豚浏览器炫风版签名信息'
        verbose_name_plural = '中文海豚浏览器炫风版签名信息'
        app_label = 'updateservice'


class XFPatch(Patch):
    package = models.ForeignKey(Package, default=get_xf_package)
    signs = models.ManyToManyField(XFSign, blank=True)

    sign_class = XFSign

    def content_dict(self):
        result_dict = super(XFPatch, self).content_dict()
        result_dict['package'] = self.package.uid
        result_dict['signs'] = [i.hash_code for i in self.signs.all()]
        return result_dict

    class Meta:
        verbose_name = '中文海豚浏览器炫风版补丁'
        verbose_name_plural = '中文海豚浏览器炫风版补丁'
        app_label = 'updateservice'


class XFFile(File):
    package = models.ForeignKey(Package, default=get_xf_package)

    patch_class = XFPatch

    class Meta:
        verbose_name = '中文海豚浏览器炫风版完整升级包'
        verbose_name_plural = '中文海豚浏览器炫风版完整升级包'
        app_label = 'updateservice'

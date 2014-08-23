#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Author: qtgan
# Date: 2013/12/23
import logging
from django.contrib import messages
from dolphinopadmin.skin.models import \
    SkinCommon, Screenshot, \
    BannerSkin, SubjectSkin
from django.utils.translation import ugettext_lazy as _
from dolphinopadmin.base.base_admin import EntityModelAdmin, AllplatformsAdminT, \
    custom_register, query_platforms

logger = logging.getLogger('dolphinopadmin.admin')


class ScreenshotAdmin(AllplatformsAdminT):
    list_display = ('id', 'name', 'display_screenshot')
    list_display_links = ('id', 'name',)
    raw_id_fields = ['pic_file']
    ordering = ['id']


class SkinCommonAdmin(AllplatformsAdminT, EntityModelAdmin):
    collection = 'skin'
    keys = ['id']
    list_display = ('id', 'name', 'uid', 'version', 'compatible_version',
                    'download_url', 'update_file', 'order', 'is_upload_china', 'promote')
    list_display_links = ['uid', 'name']
    list_filter = ['rule', 'theme_type', 'compatible_version']
    list_editable = ['order']
    ordering = ['-id']
    search_fields = ['uid', 'name', 'id']
    raw_id_fields = ['icon', 'client_icon']
    save_as = False

    def save_model(self, request, obj, form, change):
        super(SkinCommonAdmin, self).save_model(request, obj, form, change)
        if not change:
            message = obj.save(self, request)
            if message is not None:
                messages.error(request, u'获取uid等信息失败！原因是%s' % message)
        else:
            obj.save()


class SubjectSkinAdmin(AllplatformsAdminT, EntityModelAdmin):
    collection = 'skin_subject'
    keys = ['id']
    list_display = ('id', 'order', 'desc', 'is_upload_china')
    list_editable = ['order']
    ordering = ['-id']
    search_fields = ['id']
    raw_id_fields = ['icon']


class BannerSkinAdmin(AllplatformsAdminT, EntityModelAdmin):
    collection = 'skin_banner'
    keys = ['id']
    list_display = ('id', 'order', 'action', 'value', 'is_upload_china')
    list_display_links = ['id', ]
    list_filter = ['rule', 'action']
    list_editable = ['order']
    ordering = ['-id']
    search_fields = ['id', 'value']
    raw_id_fields = ['icon']

label = ("skin", _("skin"))
inlines = (
    (SubjectSkin, SkinCommon, ("(self.%s.rule, self.%s.name)", '"desc": models.CharField(**{"max_length":200,"blank":True}),')),
    (SkinCommon, Screenshot, "(self.%s.name, self.%s.name)"),
)

base_model_admin = (
    (Screenshot, ScreenshotAdmin),
    (SkinCommon, SkinCommonAdmin),
    (BannerSkin, BannerSkinAdmin),
    (SubjectSkin, SubjectSkinAdmin),
)
for platform in query_platforms(['IosEN', 'IosCN']):
    filters = {"platform": "%s" % platform[0]}
    class_name = "%s" % platform[1]
    model_name = "%s" % platform[0]
    custom_register(base_model_admin, filters, class_name,
                    model_name, label, inlines)

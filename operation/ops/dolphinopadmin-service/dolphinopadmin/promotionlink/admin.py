#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On August 3, 2012
# @Author : Jun Wang
# Email: jwang@bainainfo.com

import logging
from django.utils.translation import ugettext_lazy as _
# from dolphinopadmin.base.admin import OnlineAdmin
from dolphinopadmin.base.base_admin import EntityModelAdmin, AllplatformsAdminT, \
    custom_register, query_platforms
from django.contrib import messages
#from dolphinopadmin.remotedb.promotionlink import update_plink, delete_plink
from dolphinopadmin.promotionlink.models import Plink

logger = logging.getLogger("dolphinopadmin.admin")


class PlinkAdmin(AllplatformsAdminT, EntityModelAdmin):

    collection = 'promotionlink'
    list_display = (
        'id', 'title', 'is_upload_local', 'is_upload_china', 'is_upload_ec2', 'url',
        'update_time')
    list_display_links = ['title']
    list_filter = ['rule']
    ordering = ['-id']
    search_fields = ['title']

    def save_model(self, request, obj, form, change):
        super(PlinkAdmin, self).save_model(request, obj, form, change)
        message = obj.save()
        if message is not None:
            setattr(self, "manual_error", True)
            messages.error(request, message)

base_model_admin = (
    (Plink, PlinkAdmin),
)
app_label = ("promotionlink", _("PromotionLink"))

for platform in query_platforms(['IosEN', ]):
    filters = {"platform": "%s" % platform[0]}
    class_name = "%s" % platform[1]
    model_name = "%s" % platform[0]
    custom_register(base_model_admin, filters,
                    class_name, model_name, app_label, {})

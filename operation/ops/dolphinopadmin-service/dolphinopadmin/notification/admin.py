#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2013 Baina Info Inc. All rights reserved.
# Created On May 10, 2013
# @Author : Jun Wang
# Email: jwang@bainainfo.com
from django.contrib import admin
from dolphinopadmin.base.admin import OnlineAdmin
from dolphinopadmin.notification.models import AndroidENNotification
from dolphinopadmin.utils.sites import custom_site


class NotificationAdmin(OnlineAdmin):

    collection = 'webapp_notification'

    list_display = ('id', 'package', 'name', 'url', 'update')
    list_filter = ('package', 'sourceset')
    ordering = ['-id']


custom_site.register(AndroidENNotification, NotificationAdmin)

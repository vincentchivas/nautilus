#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On Mar 7, 2013
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import logging
from django.contrib import admin
from django.conf import settings
from dolphinopadmin.base.admin import ToolAdmin, OnlineAdmin

from dolphinopadmin.weather.models import \
    Background, Display
from dolphinopadmin.utils.sites import custom_site
SERVERS = settings.ENV_CONFIGURATION
logger = logging.getLogger('dolphinopadmin.admin')


class BackgroundAdmin(ToolAdmin):

    list_display = ('id', 'title', 'background', 'url', 'last_modified')
    ordering = ['-id']
    readonly_fields = ('url', )


class DisplayAdmin(OnlineAdmin):

    collection = 'weather_display'

    def get_content(self, request, item, server):
        return item.content_dict(server)

    list_display = ('id', 'package', 'name', 'state', 'icon')
    list_filter = ('package', )
    ordering = ['-id']
    raw_id_fields = ['icon']
    search_fields = ['state', 'name']


custom_site.register(Background, BackgroundAdmin)
custom_site.register(Display, DisplayAdmin)

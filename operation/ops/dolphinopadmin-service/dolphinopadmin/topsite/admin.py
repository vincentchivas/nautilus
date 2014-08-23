#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On Apr 3, 2013
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import logging
from django.contrib import admin
from dolphinopadmin.base.admin import OnlineAdmin

from dolphinopadmin.topsite.models import Site
from dolphinopadmin.utils.sites import custom_site
logger = logging.getLogger('dolphinopadmin.admin')


class SiteAdmin(OnlineAdmin):

    collection = 'topsite'

    def get_content(self, request, item, server):
        return item.content_dict(server)

    list_display = ('id', 'title', 'url', 'icon',
                    'package', 'max_version', 'min_version')
    ordering = ['-id']
    search_fields = ('title', 'url')
    list_filter = ('package', 'max_version', 'min_version')
    raw_id_fields = ['icon']


custom_site.register(Site, SiteAdmin)

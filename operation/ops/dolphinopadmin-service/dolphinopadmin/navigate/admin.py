#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On November 5, 2012
# @Author : Jun Wang
# Email: jwang@bainainfo.com

import logging
from django.contrib import admin
from dolphinopadmin.base.admin import ToolAdmin, OnlineAdmin, BaseItemAdmin
from dolphinopadmin.remotedb.navigate import update_section, delete_section
from dolphinopadmin.navigate.models.android import *
from dolphinopadmin.utils.sites import custom_site

logger = logging.getLogger("dolphinopadmin.admin")


class CategoryAdmin(ToolAdmin):
    list_display = ('id', 'name', 'title', 'url', 'style')
    list_display_links = ('id',)
    ordering = ['id', ]
    search_fields = ['name', 'title', 'id', 'url']


class SectionAdmin(OnlineAdmin):

    keys = ['id', 'platform']

    """
    @staticmethod
    def update_method():
        return update_section

    @staticmethod
    def delete_method():
        return delete_section
    """
    collection = 'navigate'
    keys = ['id', 'platform']

    list_display = ('id', 'name', 'title', 'column')
    list_display_links = ('name',)
    ordering = ['id']
    search_fields = ['title']


class AndroidCNCategoryAdmin(CategoryAdmin):
    inlines = (AndroidCNCategoryItemShipnline,)


class AndroidCNSectionAdmin(SectionAdmin):
    inlines = (AndroidCNSectionCategoryShipInline, )


custom_site.register(AndroidCNItem, BaseItemAdmin)
custom_site.register(AndroidCNCategory, AndroidCNCategoryAdmin)
custom_site.register(AndroidCNSection, AndroidCNSectionAdmin)

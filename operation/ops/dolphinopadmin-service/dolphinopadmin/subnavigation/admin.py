#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On August 25, 2012
# @Author : Jun Wang
# Email: jwang@bainainfo.com

import logging
from django.contrib import admin
from dolphinopadmin.base.admin import ToolAdmin, OnlineAdmin, BaseItemAdmin
from dolphinopadmin.subnavigation.models import AndroidCNItem, AndroidCNCategory, AndroidCNPage, \
    AndroidCNCategoryItemShipnline, AndroidCNPageCategoryShipInline
from dolphinopadmin.utils.sites import custom_site

logger = logging.getLogger("dolphinopadmin.admin")


class CategoryAdmin(ToolAdmin):
    list_display = ('id', 'name', 'title', 'url', 'layout')
    list_editable = ('name', 'title', 'url')
    list_display_links = ('id',)
    ordering = ['id', ]
    search_fields = ['name', 'title', 'id', 'url']
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'title', 'url', 'layout', 'column')
        }),
    )


class PageAdmin(OnlineAdmin):
    collection = 'subnavigation'

    list_display = ('id', 'title')
    list_editable = ('title',)
    list_display_links = ('id',)
    ordering = ['id']
    search_fields = ['title', ]


class AndroidCNCategoryAdmin(CategoryAdmin):
    inlines = (AndroidCNCategoryItemShipnline,)


class AndroidCNPageAdmin(PageAdmin):
    inlines = (AndroidCNPageCategoryShipInline, )


custom_site.register(AndroidCNItem, BaseItemAdmin)
custom_site.register(AndroidCNCategory, AndroidCNCategoryAdmin)
custom_site.register(AndroidCNPage, AndroidCNPageAdmin)

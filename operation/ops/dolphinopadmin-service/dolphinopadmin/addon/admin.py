#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On February 25, 2012
# @Author : Jun Wang
# Email: jwang@bainainfo.com

import logging
from django.contrib import admin
from dolphinopadmin.base.admin import ToolAdmin, OnlineAdmin
from dolphinopadmin.addon.models.addon_base import Addon, Item, Addon_Item_Ship_Inline
from dolphinopadmin.utils.sites import custom_site

logger = logging.getLogger("dolphinopadmin.admin")


class ItemAdmin(ToolAdmin):

    list_display = ('id', 'name', 'download_url',
                    'description', 'show_in_addon_bar')
    list_display_links = ('name',)
    ordering = ['id']
    search_fields = ['name', 'download_url',
                     'application_name', 'icon_url', 'description']


class AddonAdmin(OnlineAdmin):

    collection = 'addon'

    inlines = (Addon_Item_Ship_Inline,)
    list_display = ('id', 'name', 'packagename', 'source')
    list_display_links = ('name',)
    list_filter = ['packagename', 'source']
    ordering = ['id']
    search_fields = ['name']


custom_site.register(Addon, AddonAdmin)
custom_site.register(Item, ItemAdmin)

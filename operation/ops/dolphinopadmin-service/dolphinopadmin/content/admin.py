#!/usr/bin/env python
# coding: utf-8
'''
Copyright (c) 2012 Baina Info Inc. All rights reserved.
@Author : Jun Wang
@Date : 2012-2-13
'''

import logging
from django.contrib import admin
from dolphinopadmin.base.admin import ToolAdmin, OnlineAdmin, BaseItemAdmin
from dolphinopadmin.content.models.android import *
from dolphinopadmin.content.models.iphone import *
from dolphinopadmin.utils.sites import custom_site

logger = logging.getLogger("dolphinopadmin.admin")


class PackageAdmin(ToolAdmin):
    list_display = ('id', 'title', 'os', 'device',
                    'locale', 'packagename', 'packageset')
    list_editable = ('title', 'os', 'device', 'locale',
                     'packagename', 'packageset')
    list_display_links = ('id',)
    list_filter = ['os', 'device', 'locale', 'packageset']
    ordering = ['id', ]
    search_fields = ['title', 'id']
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'os', 'device', 'locale', 'packagename', 'packageset')
        }),
    )


class PackageSetAdmin(ToolAdmin):
    list_display = ('id', 'name')
    list_editable = ['name']
    list_display_links = ('id',)
    list_filter = ['name']
    ordering = ['id', ]
    search_fields = ['name', 'id']
    fieldsets = (
        ('Basic Info', {
            'fields': ('name',)
        }),
    )


class SourceSetAdmin(ToolAdmin):

    list_display = ['id', 'name']
    list_display_links = ['name', ]
    ordering = ['id']
    search_fields = ['name']
    fieldsets = (
        ('Basic Info', {
            'fields': ('name',)
        }),
    )


class SourceAdmin(ToolAdmin):

    list_display = ['id', 'name', 'source', 'sourceset']
    list_display_links = ['name', ]
    ordering = ['id']
    search_fields = ['name', 'source']


class ItemAdmin(BaseItemAdmin):
    list_display = ('id', 'title', 'url', 'color')
    ordering = ['-id']
    search_fields = ['title', 'url']
    list_filter = ['color']


class CategoryAdmin(ToolAdmin):
    list_display = ('id', 'name', 'title', 'url')
    list_editable = ('name', 'title', 'url')
    list_display_links = ('id',)
    ordering = ['id', ]
    search_fields = ['name', 'title', 'id', 'url']


class NovelAdmin(OnlineAdmin):

    collection = 'contentNovel'
    keys = ['id', 'platform']

    list_display = ('id', 'name', 'title', 'url', 'packageset', 'sourceset')
    list_editable = ('name', 'title', 'url')
    list_display_links = ('id',)
    ordering = ['id', ]
    list_filter = ['packageset', 'sourceset']
    search_fields = ['name', 'title', 'id', 'url']


class GroupAdmin(ToolAdmin):

    list_display = ('id', 'name', 'title', 'api_version')
    list_editable = ('name', 'title')
    list_display_links = ('id',)
    ordering = ['id', 'name', 'title']
    search_fields = ['name', 'title', 'id']


class SectionAdmin(OnlineAdmin):

    collection = 'contentSections'
    keys = ['id', 'platform']

    list_display = ('id', 'name', 'title', 'layout', 'icon',
                    'order', 'packageset', 'sourceset')
    list_editable = ('title', 'layout', 'icon', 'order', 'packageset')
    list_display_links = ('id',)
    list_filter = ['packageset', 'api']
    ordering = ['order', 'id']
    search_fields = ['title', 'id', 'layout', 'icon', 'packageset', 'order']


class Android_NovelAdmin(NovelAdmin):
    inlines = (Android_novel_item_ship_inline,)


class Android_CategoryAdmin(CategoryAdmin):
    inlines = (Android_category_item_ship_inline,)


class Android_GroupAdmin(GroupAdmin):
    inlines = (Android_group_category_ship_inline,)


class Android_SectionAdmin(SectionAdmin):
    inlines = (Android_section_group_ship_inline,)


class iPhone_NovelAdmin(NovelAdmin):
    inlines = (iPhone_novel_item_ship_inline,)


class iPhone_CategoryAdmin(CategoryAdmin):
    inlines = (iPhone_category_item_ship_inline,)


class iPhone_GroupAdmin(GroupAdmin):
    inlines = (iPhone_group_category_ship_inline,)


class iPhone_SectionAdmin(SectionAdmin):
    inlines = (iPhone_section_group_ship_inline,)


custom_site.register(Android_Package, PackageAdmin)
custom_site.register(Android_PackageSet, PackageSetAdmin)
custom_site.register(Android_Source, SourceAdmin)
custom_site.register(Android_SourceSet, SourceSetAdmin)
custom_site.register(Android_Item, ItemAdmin)
custom_site.register(Android_Category, Android_CategoryAdmin)
custom_site.register(Android_Section, Android_SectionAdmin)
custom_site.register(Android_Group, Android_GroupAdmin)
custom_site.register(Android_Novel, Android_NovelAdmin)


custom_site.register(iPhone_Package, PackageAdmin)
custom_site.register(iPhone_PackageSet, PackageSetAdmin)
custom_site.register(iPhone_Source, SourceAdmin)
custom_site.register(iPhone_SourceSet, SourceSetAdmin)
custom_site.register(iPhone_Item, ItemAdmin)
custom_site.register(iPhone_Category, iPhone_CategoryAdmin)
custom_site.register(iPhone_Section, iPhone_SectionAdmin)
custom_site.register(iPhone_Group, iPhone_GroupAdmin)
custom_site.register(iPhone_Novel, iPhone_NovelAdmin)

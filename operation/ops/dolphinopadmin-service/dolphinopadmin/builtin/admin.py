#!/usr/bin/env python
# coding: utf-8
import logging
from django.contrib import admin
from dolphinopadmin.builtin.models import *
from dolphinopadmin.base.admin import ToolAdmin, OnlineAdmin
from dolphinopadmin.utils.sites import custom_site

logger = logging.getLogger('dolphinopadmin.admin')


class WebappAdmin(ToolAdmin):

    list_filter = ['category', 'os']
    ordering = ['order', 'title', ]
    search_fields = ['title', 'description', 'os']
    list_display = ('title', 'category', 'description', 'enabled',
                    'icon', 'local_id', 'locale', 'order', 'os', 'recommend', 'url')
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'category', 'description', 'enabled', 'icon', 'local_id', 'locale', 'order', 'recommend', 'url')
        }),
    )


class SpeedDialAdmin(ToolAdmin):

    list_display = ('title', 'url', 'favicon', 'order')
    list_filter = ['title', ]
    ordering = ['order', ]
    search_fields = ['title', 'order']


class WebzineAdmin(ToolAdmin):

    list_display = ('Name', 'Uri', 'Favicon', 'Category', 'uID')
    list_filter = ['Name', 'Category', ]
    ordering = ['uID', ]
    search_fields = ['Name', 'Description']


class BookmarkItemAdmin(ToolAdmin):

    list_display = ('title', 'url', 'order')
    list_filter = ['title', ]
    ordering = ['order', ]
    search_fields = ['title', 'order']


class PromotionAdmin(ToolAdmin):
    list_display = ('id', 'name', 'title', 'icon', 'action')
    list_filter = ['name', 'action']
    raw_id_fields = ['icon']


class BuiltinAdmin(OnlineAdmin):

    collection = 'builtins'
    keys = ['id', 'platform', 'fish']

    list_filter = ['os', 'pname', 'locale', 'source']
    ordering = ['id', 'os', ]
    search_fields = ['pname', 'name', 'source']
    list_display = ('id', 'name', 'locale', 'os', 'pname', 'source')
    list_display_links = ('name',)
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'os', 'pname', 'source', 'locale', 'force', 'weibo', 'treasure',
                       'cmcc', 'unicom', 'telecom', 'other_operator', 'is_upload_china', 'is_upload_ec2', 'is_upload_local')
        }),
    )


class Android_BuiltinAdmin(BuiltinAdmin):
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'is_promotion', 'promotion_flag', 'sub_flag', 'preset_url', 'os', 'pname', 'source', 'locale', 'force', 'weibo', 'treasure', 'promotion',
                       'cmcc', 'unicom', 'telecom', 'other_operator', 'is_upload_china', 'is_upload_ec2', 'is_upload_local')
        }),
    )

    def get_content(self, request, item, server):
        return item.content_dict(server)

    inlines = (Android_Bkm_built_shipInline, Android_Spd_built_shipInline,
               Android_Wbz_built_shipInline, Android_Wba_built_shipInline)


class iOS_BuiltinAdmin(BuiltinAdmin):
    inlines = (iOS_Bkm_built_shipInline, iOS_Spd_built_shipInline,
               iOS_Wbz_built_shipInline, iOS_Wba_built_shipInline)

custom_site.register(promotionAction, PromotionAdmin)

custom_site.register(Android_Builtin, Android_BuiltinAdmin)
custom_site.register(Android_Webapp, WebappAdmin)
custom_site.register(Android_Bookmark_item, BookmarkItemAdmin)
custom_site.register(Android_SpeedDial, SpeedDialAdmin)
custom_site.register(Android_WebzineColumn, WebzineAdmin)


custom_site.register(iOS_Builtin, iOS_BuiltinAdmin)
custom_site.register(iOS_Webapp, WebappAdmin)
custom_site.register(iOS_Bookmark_item, BookmarkItemAdmin)
custom_site.register(iOS_SpeedDial, SpeedDialAdmin)
custom_site.register(iOS_WebzineColumn, WebzineAdmin)

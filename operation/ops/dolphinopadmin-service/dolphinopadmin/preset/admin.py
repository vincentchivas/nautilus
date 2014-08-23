#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On August 23, 2012
# @Author : Jun Wang
# Email: jwang@bainainfo.com

import logging
from django.contrib import messages
from dolphinopadmin.preset.models import Adblock, Preset, BookmarkFolder, Bookmark, Speeddial, Gesture, Strategy
from dolphinopadmin.search.models import Category
from django.utils.translation import ugettext_lazy as _
from dolphinopadmin.base.base_admin import EntityModelAdmin, AllplatformsAdminT, \
    custom_register, query_platforms
from dolphinopadmin.utils.sites import custom_site

logger = logging.getLogger("dolphinopadmin.admin")


class BookmarkAdmin(AllplatformsAdminT):

    list_display = ['id', 'name', 'url']
    list_display_links = ['name']
    search_fields = ['name', 'url']

class BookmarkFolderAdmin(AllplatformsAdminT):

    list_display = ['id', 'name']
    list_display_links = ['name']
    search_fields = ['name']


class SpeeddialAdmin(AllplatformsAdminT):

    list_display = ['id', 'title', 'url']
    list_display_links = ['title']
    raw_id_fields = ['icon']
    ordering = ['id']
    search_fields = ['title']



class SearchEngineAdmin(AllplatformsAdminT):

    list_display = ['name', 'title', 'order',
                    'rule', 'is_upload_china', 'is_upload_ec2']
    list_display_links = ['title']
    list_filter = ['rule']
    ordering = ['id']
    search_fields = ['title', 'id', 'order']
    ordering = ['-id']


class StrategyAdmin(AllplatformsAdminT):

    list_display = ['id', 'name', 'duration', 'tutorials']
    list_display_links = ['name']
    search_fields = ['tutorials']


class GestureAdmin(AllplatformsAdminT, EntityModelAdmin):

    list_display = ['id', 'title', 'user_gesture_file', 'marked_file']
    list_display_links = ['title']
    ordering = ['id']
    search_fields = ['title']


class PresetAdmin(AllplatformsAdminT, EntityModelAdmin):
    collection = 'preset'

    keys = ['id']
    list_display = ('id', 'title')
    list_display_links = ('title',)
    list_filter = ['rule']
    ordering = ['id']
    search_fields = ['title']


class AdblockAdmin(AllplatformsAdminT, EntityModelAdmin):
    collection = 'adblock'
    keys = ['id']
    list_display = ['id', 'adp_file', 'china_url', 'ec2_url', 'local_url']

    def get_content(self, request, item, server):
        return item.content_dict(server)

inlines = (
    (Preset, Category, '(self.%s.name, self.%s.name)'),
    (Preset, BookmarkFolder, '(self.%s.name, self.%s.name)'),
    (Preset, Bookmark, '(self.%s.name, self.%s.name)'),
    (Preset, Speeddial, '(self.%s.name, self.%s.name)'),
    (Preset, Strategy, '(self.%s.name, self.%s.name)'),
    (BookmarkFolder, Bookmark, '(self.%s.name, self.%s.name)'),
)

foreign_filter = (
    (
        'Preset',
        ('gesture',)
    ),
)

label = ('preset', _('preset'))

for platform in query_platforms(['IosEN', 'IosCN', 'AndroidCN']):
    filters = {'platform': platform[0]}
    class_name = platform[1]
    model_name = platform[0]
    base_model_admin = (
        (Bookmark, BookmarkAdmin),
        (BookmarkFolder, BookmarkFolderAdmin),
        (Speeddial, SpeeddialAdmin),
        (Gesture, GestureAdmin),
        (Strategy, StrategyAdmin),
        #(Category, SearchEngineAdmin),
        (Preset, PresetAdmin)
    )
    custom_register(
        base_model_admin, filters, class_name, model_name, label, inlines,
        foreign_filter)

custom_site.register(Adblock, AdblockAdmin)

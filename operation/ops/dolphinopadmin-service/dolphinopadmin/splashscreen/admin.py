#!/usr/bin/env python
# -*- coding:utf-8 -*-
# coder yfhe

import logging
from dolphinopadmin.splashscreen.models import Screen, Splash
from django.utils.translation import ugettext_lazy as _
from dolphinopadmin.base.base_admin import EntityModelAdmin, AllplatformsAdminT, \
    custom_register, query_platforms

logger = logging.getLogger("dolphinopadmin.admin")


class ScreenAdmin(AllplatformsAdminT):

    list_display = (
        'id', 'title', 'min_w', 'max_w', 'min_h', 'max_h', 'front_picture',
        'front_wifi_only', 'background_picture', 'background_wifi_only')
    ordering = ['id']
    raw_id_fields = ['front_icon', 'background_icon']
    search_fields = ['title']


class SplashAdmin(AllplatformsAdminT, EntityModelAdmin):

    collection = 'splashscreen'

    list_display = ('id', 'title', 'version')
    list_display_links = ('title',)
    ordering = ['id']
    search_fields = ['title']

inlines = (
    (Splash, Screen, '(self.%s.title, self.%s.title)'),
)

label = ('splashscreen', _('splash screen'))

for platform in query_platforms(['IosEN', 'IosCN', 'AndroidEN']):
    filters = {'platform': platform[0]}
    class_name = platform[1]
    model_name = platform[0]
    base_model_admin = (
        (Splash, SplashAdmin),
        (Screen, ScreenAdmin),
    )
    custom_register(base_model_admin, filters, class_name,
                    model_name, label, inlines)

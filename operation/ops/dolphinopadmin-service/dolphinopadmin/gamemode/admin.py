#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On Apr 3, 2013
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import logging
from django.contrib import admin
from django.conf import settings
from dolphinopadmin.base.admin import OnlineAdmin

from dolphinopadmin.gamemode.models import Game
from dolphinopadmin.utils.sites import custom_site
SERVERS = settings.ENV_CONFIGURATION
logger = logging.getLogger('dolphinopadmin.admin')


class GameAdmin(OnlineAdmin):

    collection = 'gamemode'

    def get_content(self, request, item, server):
        return item.content_dict(server)

    list_display = ('id', 'title', 'url', 'icon', 'dolphin',
                    'mode', 'package', 'sourceset')
    list_filter = ('package', 'sourceset')
    ordering = ['-id']
    search_fields = ('title', 'url')
    raw_id_fields = ['icon']


custom_site.register(Game, GameAdmin)

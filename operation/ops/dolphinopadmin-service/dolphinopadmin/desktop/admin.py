#!/usr/bin/env python
# -*- coding:utf-8 -*-
# coder yfhe
import logging
from dolphinopadmin.desktop.models import Item, Folder, Screen, Desktop

from django.utils.translation import ugettext_lazy as _
from dolphinopadmin.base.base_admin import EntityModelAdmin, AllplatformsAdminT, \
    custom_register, query_platforms
logger = logging.getLogger('dolphinopadmin.admin')


class ItemAdmin(AllplatformsAdminT):
    list_display = ('id', 'name', 'title', 'url', 'delete')
    search_fields = ('title', 'url')
    list_filter = ('delete',)
    raw_id_fields = ['icon']

class FolderAdmin(AllplatformsAdminT):
    list_display = ('id', 'title')
    raw_id_fields = ['icon']

class ScreenAdmin(AllplatformsAdminT):
    list_display = ('id', 'name', 'sid', 'last_modified')
    search_fields = ('name', 'sid')


class DesktopAdmin(AllplatformsAdminT, EntityModelAdmin):

    #keys = ['id', 'platform']
    collection = 'desktops'

    list_display = ('id', 'name', 'is_upload_china')
    search_fields = ('name',)

inlines = (
    (Folder, Item, '(self.%s.title, self.%s.title)'),
    (Screen, Folder, '(self.%s.name, self.%s.title)'),
    (Screen, Item, '(self.%s.name, self.%s.title)'),
    (Desktop, Screen, '(self.%s.title, self.%s.title)'),
)

foreign_filter = ()

label = ('desktop', _('desktop'))

for platform in query_platforms(['IosEN', 'IosCN'], [('IOS', unicode(_('ios')))]):
    filters = {'platform': platform[0]}
    class_name = platform[1]
    model_name = platform[0]
    base_model_admin = (
        (Item, ItemAdmin),
        (Folder, FolderAdmin),
        (Screen, ScreenAdmin),
        (Desktop, DesktopAdmin)
    )
    custom_register(
        base_model_admin, filters, class_name, model_name, label, inlines,
        foreign_filter)

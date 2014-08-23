#!/usr/bin/env python
# -*- coding:utf-8 -*-
# coder yfhe

import logging
from dolphinopadmin.treasure.models import Item, Category, Group, Section, Treasure
from dolphinopadmin.base.base_admin import AllplatformsAdminT, EntityModelAdmin, \
    custom_register, query_platforms
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger('dolphinopadmin.admin')


class ItemAdmin(AllplatformsAdminT):

    list_display = ['id', 'title', 'url', 'promotion', 'last_modified']
    list_display_links = ('id', 'title')
    search_fields = ('title', 'url')
    raw_id_fields = ['icon']


class CategoryAdmin(AllplatformsAdminT):

    list_display = ('id', 'name', 'title', 'url')
    list_display_links = ('id', 'name')
    search_fields = ['name', 'title', 'id', 'url']


class GroupAdmin(AllplatformsAdminT):

    list_display = ('id', 'name', 'title')
    list_display_links = ('id',)
    search_fields = ['name', 'title', 'id']


class SectionAdmin(AllplatformsAdminT, EntityModelAdmin):

    collection = 'treasure_section'

    list_display = ('id', 'name', 'is_upload_china')
    list_display_links = ('id', 'name',)
    #list_filter = ['rule']
    search_fields = ('name', 'id')


class TreasureAdmin(AllplatformsAdminT, EntityModelAdmin):

    collection = 'treasure'

    list_display = ('id', 'name', 'is_upload_china')
    list_display_links = ('id', 'name',)
    #list_filter = ['rule']
    search_fields = ('name', 'id')

inlines = ((Treasure, Item, '(self.%s.name,self.%s.title)'),
           (Section, Group, '(self.%s.name,self.%s.name)'),
           (Group, Category, '(self.%s.name,self.%s.name)'),
           (Category, Item, ('(self.%s.name,self.%s.title)',
            '"online_time": models.DateTimeField(**{"default":datetime.datetime.now}),')),
           (Section, Item, '(self.%s.name,self.%s.title)'))

base_model_admin = ((Item, ItemAdmin), (Category, CategoryAdmin),
                    (Group, GroupAdmin), (Section, SectionAdmin), (Treasure, TreasureAdmin))
foreign_filter = ()
for platform in query_platforms(['IosEN', 'IosCN', 'AndroidEN']):
    filters = {'platform': platform[0]}
    class_name = platform[1]
    model_name = platform[0]
    label = ("treasure", _("treasures"))
    custom_register(
        base_model_admin, filters, class_name, model_name, label, inlines,
        foreign_filter)

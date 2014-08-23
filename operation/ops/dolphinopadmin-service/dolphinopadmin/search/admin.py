#!/usr/bin/env python
# -*- coding:utf-8 -*-
# coder yfhe

import logging
#from dolphinopadmin.base.utils import set_order

from django.utils.translation import ugettext_lazy as _
from dolphinopadmin.search.models import Hotword, Category, Search, Keyword
from dolphinopadmin.base.base_admin import EntityModelAdmin, AllplatformsAdminT, \
    custom_register, query_platforms

logger = logging.getLogger('dolphinopadmin.admin')


class HotwordAdmin(AllplatformsAdminT):

    list_display = ['id', 'title', 'url']
    search_fields = ['title', 'url']
    ordering = ['-id']


class SearchAdmin(AllplatformsAdminT):

    list_display = ['id', 'name', 'title', 'url']
    search_fields = ['title', 'url']
    ordering = ['-id']
    raw_id_fields = ['icon']


class CategoryAdmin(AllplatformsAdminT, EntityModelAdmin):

    collection = 'search_category'
    replace = False
    auto_sort = True

    list_display = ['name', 'title', 'order',
                    'rule', 'is_upload_china', 'is_upload_ec2']
    list_display_links = ['title']
    list_filter = ['rule']
    ordering = ['id']
    search_fields = ['title', 'id', 'order']
    ordering = ['-id']


class KeywordAdmin(AllplatformsAdminT, EntityModelAdmin):

    collection = 'search_keyword'
    auto_sort = True

    list_display = ['keyword', 'order', 'track',
                    'is_upload_china', 'is_upload_ec2', 'rule']
    list_display_links = ['keyword']
    list_filter = ['rule']
    ordering = ['-id']

inlines = (
    (Category, Search, ('(self.%s.title,self.%s.title)',
     '"default":models.BooleanField(**{"default":False}),')),
    (Category, Hotword, '(self.%s.title,self.%s.title)'),
)

foreign_filter = (
    (
        'Category',
        ('search', 'hotword')
    ),
)
label = ("search", _("search engine"))

for platform in query_platforms([]):
    filters = {'platform': platform[0]}
    class_name = platform[1]
    model_name = platform[0]
    base_model_admin = (
        (Category, CategoryAdmin),
        (Hotword, HotwordAdmin),
        (Search, SearchAdmin),
        (Keyword, KeywordAdmin),
    )
    custom_register(
        base_model_admin, filters, class_name, model_name, label, inlines,
        foreign_filter)

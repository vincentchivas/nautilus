#!/usr/bin/env python
# -*-coding:utf-8 -*-
# Author: qtgan
# Date: 2013/12/12
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from dolphinopadmin.websitesnav.models import SiteCategory, Website, \
    Strategy
from dolphinopadmin.utils.sites import custom_site
from dolphinopadmin.base.base_admin import EntityModelAdmin, AllplatformsAdminT, \
    custom_register
from dolphinopadmin.base.content import NAV_FUNCTION as functions


class WebsiteAdmin(AllplatformsAdminT):
    list_display = ('id', 'site_title', 'url')
    list_display_links = ('id', 'site_title',)


class SiteCategoryAdmin(AllplatformsAdminT):
    list_display = ('category_name', 'sites_count')
    list_display_links = ('category_name', )


class StrategyAdmin(AllplatformsAdminT, EntityModelAdmin):
    list_display = ('title', 'rule', 'sites_count')
    list_display_links = ('title',)
    collection = 'websitesnav'      # collection(table) name in mongodb

    def get_list_display(self, request):
        if self.model.filters['function'] is "navigation":
            return ('title', 'rule', 'sites_count', "categories_count")
        else:
            return ('title', 'rule', 'sites_count')

label = ("websitesnav", _("navigation"))
# for navigation
base_model_admin_1 = (
    (Website, WebsiteAdmin),
    (SiteCategory, SiteCategoryAdmin),
    (Strategy, StrategyAdmin),
)

# for shortcut and hotsearch
base_model_admin_2 = (
    (Website, WebsiteAdmin),
    (Strategy, StrategyAdmin),
)

inlines_1 = (
    (SiteCategory, Website,
     '(self.%s.category_name, self.%s.category_belong)'),
    (Strategy, Website, '(self.%s.rule, self.%s.site_title)'),
    (Strategy, SiteCategory, '(self.%s.rule, self.%s.category_name)'),
)

inlines_2 = (
    (SiteCategory, Website,
     '(self.%s.category_name, self.%s.category_belong)'),
    (Strategy, Website, '(self.%s.rule, self.%s.site_title)'),
)
for func in functions:
    filters = {"function": func[0]}
    class_name = "%s" % func[1]
    model_name = "%s" % func[0]
    if func[0] is 'navigation':
        base_model_admin = base_model_admin_1
        inlines = inlines_1
    else:
        base_model_admin = base_model_admin_2
        inlines = inlines_2
    custom_register(base_model_admin, filters, class_name,
                    model_name, label, inlines)

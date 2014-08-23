# -*- coding:utf-8 -*-
#/usr/bin/env python
# coding: utf-8
import logging
from django.contrib import admin
from dolphinopadmin.base.utils import set_order
from django.utils.translation import ugettext_lazy as _
from dolphinopadmin.webapps.models import Application, Category, \
    Subject
from dolphinopadmin.base.base_admin import EntityModelAdmin, AllplatformsAdminT, \
    custom_register, query_platforms

logger = logging.getLogger('dolphinopadmin.admin')


class WebappsAdmin(AllplatformsAdminT, EntityModelAdmin):
    keys = ['id', 'platform']
    search_fields = ['name', 'description']
    raw_id_fields = ['icon']
    ordering = ['order']
    auto_sort = True


class CategoryAdmin(WebappsAdmin):

    collection = 'webapps_category'
    list_display = ('id', 'name', 'order', 'icon', 'description')


class SubjectAdmin(WebappsAdmin):

    collection = 'webapps_subject'
    list_display = ('id', 'name', 'order', 'icon', 'description')
    search_fields = ['name', 'description']
    radio_fields = {'tag': admin.HORIZONTAL}


class ApplicationAdmin(WebappsAdmin):

    collection = 'webapps_application'
    list_display = ('id', 'name', 'order', 'category', 'category_order',
                    'icon', 'description', 'promote', 'is_upload_china', 'is_upload_ec2')
    list_display_links = ('name',)
    list_filter = ['promote', 'category']
    ordering = ['category_order']
    search_fields = ['name', 'description']
    radio_fields = {'tag': admin.HORIZONTAL}

    def save_model(self, request, obj, form, change):
        super(ApplicationAdmin, self).save_model(request, obj, form, change)
        if change:
            obj_list = obj.__class__.objects.filter(
                category=obj.category).order_by('category_order')
            set_order(obj, 'category_order', obj_list)
        else:
            obj.save()

inlines = (
    (Subject, Application, '(self.%s.name, self.%s.name)'),
)

foreign_filter = (
    (
        'Application',
        ('category',)
    ),
)
label = ("webapps", _("web application"))

base_model_admin = (
    (Category, CategoryAdmin),
    (Subject, SubjectAdmin),
    (Application, ApplicationAdmin),
)
for platform in query_platforms(['IosEN', 'AndroidCN']):
    filters = {'platform': platform[0]}
    class_name = platform[1]
    model_name = platform[0]
    custom_register(
        base_model_admin, filters, class_name, model_name, label, inlines,
        foreign_filter)

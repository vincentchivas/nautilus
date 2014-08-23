#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On Apr 3, 2013
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import logging
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from dolphinopadmin.utils.sites import custom_site
from dolphinopadmin.base.base_admin import EntityModelAdmin, AllplatformsAdminT, \
    custom_register
#from django import forms
from dolphinopadmin.resource.models import Icon, ResourceBase

logger = logging.getLogger('dolphinopadmin.admin')

RESOURCE_TYPE = (
    ('icon', _('icon')),
    ('screenshot', _('screenshot')),
    ('package', _('package')),
)


class IconAdmin(AllplatformsAdminT, EntityModelAdmin):

    list_display = ('id', 'title', 'icon_file', 'width', 'height',
                    'china_url', 'ec2_url', 'is_upload_china', 'is_upload_ec2')
    list_filter = ('width', 'height', 'is_upload_china', 'is_upload_ec2')
    list_per_page = 50
    ordering = ['-id']
    readonly_fields = ('china_url', 'ec2_url', 'local_url', 'last_modified',
                       'upload_china', 'upload_ec2', 'upload_local',
                       'is_upload_china', 'is_upload_ec2', 'is_upload_local')
    search_fields = ('icon', 'title', 'id')

    # def pre_upload(self, request, queryset, server):
    #    for obj in queryset:
    #        obj.upload_file(server)

    def save_model(self, request, obj, form, change):
        super(IconAdmin, self).save_model(request, obj, form, change)
        message = obj.save()
        if message is not None:
            setattr(self, "manual_error", True)
            messages.error(request, message)


class ResourceBaseAdmin(EntityModelAdmin, AllplatformsAdminT):
    list_filter = ('width', 'height', 'is_upload_china', 'is_upload_ec2')
    readonly_fields = (
        'width', 'height', 'china_url', 'ec2_url', 'local_url', 'is_upload_china',
        'is_upload_ec2', 'is_upload_local')
    search_fields = ('file_obj', 'title', 'id')
    upload_file = True

    def get_list_display(self, request):
        if self.model.filters['types'] in ['icon', 'screenshot']:
            list_display = ('title', 'width', 'height',
                            'is_upload_china', 'is_upload_ec2')
        else:
            list_display = ('title', 'is_upload_china', 'is_upload_ec2')

        return list_display

    def get_fieldsets(self, request, obj=None):

        if self.model.filters['types'] in ['icon', 'screenshot']:
            fieldsets = (('Basic Info', {
                'fields': ('file_obj', 'title', 'width', 'height',
                           'china_url', 'ec2_url', 'local_url', 'is_upload_china',
                           'is_upload_ec2', 'is_upload_local')
            }),
            )
        else:
            fieldsets = (('Basic Info', {
                'fields': ('file_obj', 'title', 'china_url', 'ec2_url', 'local_url',
                           'is_upload_china', 'is_upload_ec2', 'is_upload_local')
            }),
            )

        return fieldsets

    def save_model(self, request, obj, form, change):
        super(ResourceBaseAdmin, self).save_model(request, obj, form, change)
        obj.types = self.model.filters['types']
        message = obj.save()
        if message is not None:
            setattr(self, 'manual_error', True)
            messages.error(request, message)
            return None
        #super(ResourceBaseAdmin, self).save_model(request, obj, form, change)


def query_types():
    return RESOURCE_TYPE

inlines = ()
foreign_filter = ()
label = ("resource", _("file resource"))

for tmp_type in query_types():
    filters = {'types': tmp_type[0]}
    class_name = unicode(tmp_type[1])
    model_name = tmp_type[0]
    base_model_admin = (
        (ResourceBase, ResourceBaseAdmin),
    )
    custom_register(
        base_model_admin, filters, class_name, model_name, label, inlines,
        foreign_filter)

custom_site.register(Icon, IconAdmin)

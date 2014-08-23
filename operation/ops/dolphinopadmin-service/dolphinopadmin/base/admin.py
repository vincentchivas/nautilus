#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# @Author : Jun Wang
# @Date : 2012-7-10
# Email: jwang@bainainfo.com

import logging
from django.contrib import admin
from django.contrib import messages
from django.conf import settings
from django.contrib.admin.actions import delete_selected

from admin_enhancer import admin as enhanced_admin
from dolphinopadmin.remotedb import basedb


LOCAL = 'local'
CHINA = 'china'
EC2 = 'ec2'

_ONLINE = ['local', 'china', 'ec2']

DB_SERVERS = settings.ENV_CONFIGURATION


logger = logging.getLogger("dolphinopadmin.admin")


def _update_selected(env, queryset, value):
    if env == 'local':
        queryset.update(is_upload_local=value)
    elif env == 'china':
        queryset.update(is_upload_china=value)
    elif env == 'ec2':
        queryset.update(is_upload_ec2=value)


def _get_actions(envs, actions=[]):
    for env in envs:
        actions.append('upload_to_%s' % env)
        actions.append('delete_from_%s' % env)
    return actions


class ToolAdmin(enhanced_admin.EnhancedModelAdminMixin, admin.ModelAdmin):

#    delete_selected_confirmation_template = 'admin/base/delete_selected_confirmation.html'
    save_as = True
    save_on_top = True
    keys = ['id']
    replace = True

    def _upload_to_mongodb(self, request, queryset, server, func_name=None):
        message = ''
        mongo_pk = {}
        try:
            for item in queryset:
                if hasattr(self, 'get_content'):
                    mongo_data = self.get_content(request, item, server)
                elif hasattr(item, 'content_dict'):
                    mongo_data = item.content_dict()
                else:
                    break
                if '_sync_key' in mongo_data and isinstance(mongo_data['_sync_key'], dict):
                    mongo_pk = {'_sync_key': mongo_data['_sync_key']}
                else:
                    for key in self.keys:
                        mongo_pk[key] = mongo_data[key]
                if hasattr(self, 'update_method'):
                    self.update_method()(mongo_pk, mongo_data, server)
                elif hasattr(self, 'collection'):
                    basedb.update_data(
                        self.collection, mongo_pk, mongo_data, server, self.replace)
                else:
                    func_name(mongo_pk, mongo_data, server)
                if server in _ONLINE:
                    logger.info('User: %s upload data to %s' %
                                (request.user.username, server))
                    logger.info(mongo_data)
            _update_selected(server, queryset, True)
            message += 'Upload %d %s to %s successfully!\n' % (queryset.count(),
                                                               queryset[0].__class__.__name__, server)
            messages.success(request, message)
        except Exception, e:
            message += 'Error:Upload failed, %s!' % e
            messages.error(request, message)
            logger.exception(e)

    def _delete_selected_from_online(self, request, queryset, server, func_name=None):
        message = ''
        try:
            for item in queryset:
                mongo_pk = {}
                if hasattr(self, 'get_content'):
                    mongo_data = self.get_content(request, item, server)
                elif hasattr(item, 'content_dict'):
                    try:
                        mongo_data = item.content_dict()
                    except Exception, e:
                        mongo_data = {}
                        for key in self.keys:
                            mongo_data[key] = item.__dict__[key]
                else:
                    break
                if '_sync_key' in mongo_data and isinstance(mongo_data['_sync_key'], dict):
                    mongo_pk = {'_sync_key': mongo_data['_sync_key']}
                else:
                    for key in self.keys:
                        mongo_pk[key] = mongo_data[key]
                if hasattr(self, 'special_delete'):
                    self.special_delete(item, server)
                elif hasattr(self, 'delete_method'):
                    self.delete_method()(mongo_pk, server)
                elif hasattr(self, 'collection'):
                    basedb.delete_data(self.collection, mongo_pk, server)
                else:
                    func_name(mongo_pk, server)
                if server in _ONLINE:
                    logger.info('User: %s delete data from %s' %
                                (request.user.username, server))
                    logger.info(mongo_data)
            _update_selected(server, queryset, False)
            message += 'Delete %d %s from %s successfully!\n' % (queryset.count(),
                                                                 queryset[0].__class__.__name__, server)
            messages.success(request, message)
        except Exception, e:
            message += 'Error:Delete failed, %s!' % e
            messages.error(request, message)
            logger.exception(e)

    def delete_selected_from_admin(self, request, queryset):
        message = ''
        for item in queryset:
            if not hasattr(item, 'is_upload_local'):
                break
            if item.is_upload_local:
                message += 'Warning: %s has been upload to local, please delete it from local first!' % item
                break
            elif item.is_upload_china:
                message += 'Warning: %s has been upload to china, please delete it from china first!' % item
                break
            elif item.is_upload_ec2:
                message += 'Warning: %s has been upload to ec2, please delete it from ec2 first!' % item
                break
        if message == '':
            message += 'Delete selected data from admin successfully!'
            return delete_selected(self, request, queryset)
        else:
            messages.warning(request, message)
            logger.debug(message)
    delete_selected_from_admin.short_description = u'delete selected from admin'

    actions = _get_actions(
        DB_SERVERS.keys(), actions=['delete_selected_from_admin'])

    def get_actions(self, request):
        actions = super(ToolAdmin, self).get_actions(request)
        if not request.POST.get('post'):
            if 'delete_selected' in actions:
                del actions['delete_selected']
        if hasattr(self, 'online') and not getattr(self, 'online'):
            del_actions = _get_actions(DB_SERVERS.keys())
            for action in del_actions:
                if action in actions:
                    del actions[action]
        return actions

    def save_model(self, request, obj, form, change):
        obj.save()

    def has_delete_permission(self, request, obj=None):
        if 'action' in request.POST:
            return True
        else:
            return False


class OnlineAdmin(ToolAdmin):

    keys = ['id']
    readonly_fields = ['is_upload_local', 'is_upload_china', 'is_upload_ec2']

    def upload_to_local(self, request, queryset):
        if hasattr(self, 'pre_upload'):
            self.pre_upload(request, queryset, LOCAL)
        self._upload_to_mongodb(request, queryset, LOCAL)
    upload_to_local.short_description = u"publish to local"

    def upload_to_china(self, request, queryset):
        if hasattr(self, 'pre_upload'):
            self.pre_upload(request, queryset, CHINA)
        self._upload_to_mongodb(request, queryset, CHINA)
    #upload_to_china.short_description = u"上传到中国服务器"
    upload_to_china.short_description = u"publish to china"

    def upload_to_ec2(self, request, queryset):
        if hasattr(self, 'pre_upload'):
            self.pre_upload(request, queryset, EC2)
        self._upload_to_mongodb(request, queryset, EC2)
    #upload_to_ec2.short_description = u"上传到国外服务器"
    upload_to_ec2.short_description = u"publish to ec2"

    def delete_from_local(self, request, queryset):
        if hasattr(self, 'pre_delete'):
            self.pre_delete(request, queryset, LOCAL)
        self._delete_selected_from_online(request, queryset, LOCAL)
    #delete_from_local.short_description = u"从本地服务器删除"
    delete_from_local.short_description = u"delete from local"

    def delete_from_china(self, request, queryset):
        if hasattr(self, 'pre_delete'):
            self.pre_delete(request, queryset, CHINA)
        self._delete_selected_from_online(request, queryset, CHINA)
    #delete_from_china.short_description = u"从中国服务器删除"
    delete_from_china.short_description = u"delete from china"

    def delete_from_ec2(self, request, queryset):
        if hasattr(self, 'pre_delete'):
            self.pre_delete(request, queryset, EC2)
        self._delete_selected_from_online(request, queryset, EC2)
    #delete_from_ec2.short_description = u"从国外服务器删除"
    delete_from_ec2.short_description = u"delete from ec2"


class EnhancedAdminInline(enhanced_admin.EnhancedModelAdminMixin, admin.TabularInline):
    pass


class BasePackageAdmin(ToolAdmin):
    list_display = ['id', 'package']
    list_display_links = ['package']
    ordering = ['id']
    search_fields = ['package']
    fieldsets = (
        ('Basic Info', {
            'fields': ('package',)
        }),
    )


class BaseSourceAdmin(ToolAdmin):

    list_display = ['id', 'source']
    list_display_links = ['source']
    ordering = ['id']
    search_fields = ['source']


class BaseSourceSetAdmin(ToolAdmin):

    list_display = ['id', 'name']
    list_display_links = ['name']
    ordering = ['id']
    search_fields = ['name']


class BaseItemAdmin(ToolAdmin):
    list_display = ['id', 'title', 'url']
    list_editable = ['title', 'url']
    list_display_links = ['id']
    ordering = ['id']
    search_fields = ['title', 'id', 'url']


class BaseOsVersionAdmin(ToolAdmin):

    list_display = ('id', 'os_version')
    list_display_links = ['os_version']
    ordering = ['-id']
    search_fields = ['os_version']


class BaseResolutionAdmin(ToolAdmin):

    list_display = ('id', 'resolution')
    list_display_links = ['resolution']
    ordering = ['-id']
    search_fields = ['resolution']


class BaseMobileAdmin(ToolAdmin):

    list_display = ('id', 'mobile')
    list_display_links = ['mobile']
    ordering = ['-id']
    search_fields = ['mobile']


class BaseRomAdmin(ToolAdmin):

    list_display = ('id', 'rom')
    list_display_links = ['rom']
    ordering = ['-id']
    search_fields = ['rom']


class BaseMobileOperatorAdmin(ToolAdmin):

    list_display = ['id', 'operator']
    list_display_links = ['operator']
    ordering = ['id']
    search_fields = ['operator']


class BaseCPUAdmin(ToolAdmin):

    list_display = ('id', 'cpu')
    list_display_links = ['cpu']
    ordering = ['-id']
    search_fields = ['cpu']


class BaseProductAdmin(ToolAdmin):

    list_display = ('id', 'name', 'uid')
    ordering = ['-id']


class BaseIconAdmin(ToolAdmin):

    list_display = ('id', 'title', 'icon', 'url', 'last_modified')
    ordering = ['-id']
    readonly_fields = ('url', 'last_modified', 'upload_china',
                       'upload_ec2', 'upload_local')

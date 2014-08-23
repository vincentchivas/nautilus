#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On February 25, 2012
# @Author : Jun Wang
# Email: jwang@bainainfo.com
#import sys
#from threading import Thread
#from django.contrib import admin

import logging
import re
import os
from ftplib import FTP
from django.contrib import messages
from dolphinopadmin.base.admin import ToolAdmin, OnlineAdmin
from dolphinopadmin.updateservice.models import Button, \
    Update, XFSign, XFPatch, XFFile, \
    UpdateButtonShipInline
from dolphinopadmin.updateservice.forms import ButtonAdminForm
from dolphinopadmin.utils.sites import custom_site

logger = logging.getLogger("dolphinopadmin.admin")

PATCH_NAME = re.compile(
    r'.+_(?P<source>[a-z]+)_(?P<old_vname>(\d+\.)+(\d))_(?P<new_vname>(\d+\.)+(\d))_\d+.patch')
CN_PACKAGE = 'com.dolphin.browser.cn'
FTP_SERVER = '42.121.117.185'
FTP_PATH = '/cdn_online/patch'
FTP_USER = 'cdn_online'
FTP_PASSWORD = 'ysdss@cdn_o'


def upload_file(request, queryset, server, path):
    try:
        ftp = FTP(FTP_SERVER)
        ftp.login(FTP_USER, FTP_PASSWORD)
        logger.info(path)
        logger.info(server)
        ftp.cwd('%s/%s' % (path, server))
        for obj in queryset:
            file_name = os.path.basename(obj.update_file.name)
            try:
                logger.info(file_name)
                ftp.storbinary('STOR %s' % file_name, obj.update_file)
                url = 'http://download.dolphin-browser.cn/downloads/%s/%s/%s' % ('patch',
                                                                                 server, file_name)
                obj.url = url
                logger.debug(url)
                obj.save()
            except Exception, e:
                logger.exception(e)
                messages.error(request, u'上传文件%s到%s失败,Error:%s' %
                               (file_name, server, e))
        ftp.quit()
    except Exception, e:
        logger.exception(e)
        messages.error(request, u'上传文件到%s失败,Error:%s' % (server, e))


def delete_file(request, queryset, server, path):
    try:
        ftp = FTP(FTP_SERVER)
        ftp.login(FTP_USER, FTP_PASSWORD)
        ftp.cwd('%s/%s' % (path, server))
        for obj in queryset:
            file_name = os.path.basename(obj.update_file.name)
            try:
                ftp.delete(file_name)
                obj.url = ''
                obj.save()
            except Exception, e:
                logger.exception(e)
                messages.error(request, u'从%s删除文件%s失败,Error:%s' %
                               (server, file_name, e))
        ftp.quit()
    except Exception, e:
        logger.exception(e)
        messages.error(request, u'从%s删除文件%s失败,Error:%s' %
                       (server, file_name, e))


def upload_patches(request, patch_model, patch_queryset):
    patch_admin = PatchAdmin(patch_model, custom_site)
    patch_admin.upload_to_local(request, patch_queryset)


class ButtonAdmin(ToolAdmin):

    form = ButtonAdminForm

    list_display = ('id', 'name', 'action')
    list_display_links = ('name', )
    ordering = ['-id']
    search_fields = ['name', 'action']


class UpdateAdmin(OnlineAdmin):

    collection = 'updateservice'

    inlines = (UpdateButtonShipInline, )
    list_display = ('id', 'title', 'version_name',
                    'version_code', 'package', 'sourceset')
    list_display_links = ('title',)
    list_filter = ['package', 'version_name', 'sourceset']
    ordering = ['-id']
    search_fields = ['title']


class packageAdmin(ToolAdmin):

    list_display = ('id', 'name', 'uid')
    ordering = ['-id']


class SignAdmin(ToolAdmin):

    list_display = ('id', 'hash_code', 'package', 'source', 'version', 'vname')
    list_filter = ['package', 'source', 'version', 'vname']
    ordering = ['-id']


class PatchAdmin(OnlineAdmin):

    collection = 'update_patch'

    def pre_upload(self, request, queryset, server):
        upload_file(request, queryset, server, FTP_PATH)

    def pre_delete(self, request, queryset, server):
        delete_file(request, queryset, server, FTP_PATH)

    list_display = ('id', 'update_file', 'is_upload_local', 'is_upload_china',
                    'is_upload_ec2', 'package', 'old_version', 'new_version')
    list_display_links = ('update_file', )
    list_filter = ['package', 'new_version', 'old_version']
    ordering = ['-id']
    search_fields = ['update_file']
    filter_horizontal = ['signs']


class FileAdmin(ToolAdmin):

    def save_model(self, request, obj, form, change):
        obj.save(request)

    list_display = ('id', 'update_file', 'package', 'version', 'vname')
    list_display_links = ('update_file', )
    list_filter = ['package', 'vname']
    ordering = ['-id']
    search_fields = ['update_file']


custom_site.register(Update, UpdateAdmin)
custom_site.register(Button, ButtonAdmin)
custom_site.register(XFSign, SignAdmin)
custom_site.register(XFPatch, PatchAdmin)
custom_site.register(XFFile, FileAdmin)

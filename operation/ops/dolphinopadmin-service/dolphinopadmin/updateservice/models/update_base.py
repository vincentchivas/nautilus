#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# @Author : Jun Wang
# @Date : 2012-5-3
# Email: jwang@bainainfo.com
import time
import logging
import os
import subprocess
from datetime import datetime
from django.db import models
from django.contrib import messages
from django.conf import settings
from dolphinopadmin.utils import md5
from dolphinopadmin.base.models import BaseOnline
from dolphinopadmin.configure.models import Package, SourceSet, OSVersionSet, MobileSet, CPUSet, Locale
from dolphinopadmin.base.admin import EnhancedAdminInline


logger = logging.getLogger('dolphinopadmin.admin')

DEFAULT_SOURCE = 'ofw'
MEDIA_ROOT = settings.MEDIA_ROOT
PATCH_PATH = 'updateservice/patch'
FILE_PATH = 'updateservice/file'
KB = 1024
MB = 1024 * 1024


class Button(models.Model):

    name = models.CharField(max_length=200)
    action = models.CharField(max_length=200, blank=True)
    url = models.CharField(max_length=2000, blank=True)
    icon_url = models.CharField(max_length=2000, blank=True)
    package = models.CharField(max_length=100, blank=True)

    def content_dict(self):
        result_dict = {
            "btn": self.name,
            "action": self.action,
        }
        if self.url:
            result_dict['url'] = self.url
        if self.icon_url:
            result_dict['icon_url'] = self.icon_url
        if self.package:
            result_dict['package'] = self.package
        return result_dict

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'updateservice'


class Update(BaseOnline):

    title = models.CharField(max_length=200)
    package = models.ForeignKey(Package)
    download_url = models.CharField(max_length=1000)
    version_name = models.CharField(max_length=200)
    version_code = models.IntegerField()
    min_version = models.IntegerField()
    max_version = models.IntegerField()
    content_title = models.CharField(max_length=100)
    update_time = models.CharField(max_length=200)
    change_log = models.TextField(max_length=10000)
    auto = models.BooleanField(default=True)
    is_force = models.BooleanField(default=False)
    os = models.CharField(max_length=200)
    sample = models.IntegerField(
        verbose_name='抽样数量', default=-1, help_text='大于0为抽样,否则为全量')
    valid_time = models.DateTimeField(
        default=datetime.now, help_text="Beijing Time")
    invalid_time = models.DateTimeField(help_text="Beijing Time")
    apk_size = models.CharField(max_length=200)
    locales = models.ManyToManyField(Locale, blank=True)
    button = models.ManyToManyField(Button, through='UpdateButtonShip')

    sourceset = models.ForeignKey(SourceSet)
    os_versions = models.ForeignKey(
        OSVersionSet, verbose_name='自动更新系统版本集合', related_name='auto_os_versions')
    mobiles = models.ForeignKey(
        MobileSet, verbose_name='自动更新机型集合', related_name='auto_mobiles')
    cpus = models.ForeignKey(
        CPUSet, verbose_name='自动更新CPU集合', related_name='auto_cpus')
    manual_os_versions = models.ForeignKey(
        OSVersionSet, verbose_name='手动更新系统版本集合', related_name='manual_os_versions')
    manual_mobiles = models.ForeignKey(
        MobileSet, verbose_name='手动更新机型集合', related_name='manual_mobiles')
    manual_cpus = models.ForeignKey(
        CPUSet, verbose_name='手动更新CPU集合', related_name='manual_cpus')

    def get_buttons(self):
        buttons = UpdateButtonShip.objects.filter(
            update__id=self.id).order_by('order')
        button_list = []
        for item in buttons:
            dic = item.button.content_dict()
            dic['order'] = item.order
            button_list.append(dic)
        return button_list

    def get_locales(self):
        locales = self.locales.all()
        locale_list = [item.locale for item in locales]
        return locale_list if len(locales) else None

    def content_dict(self):
        result_dict = {
            "id": self.id,
            "title": self.title,
            "download_url": self.download_url,
            "version_name": self.version_name,
            "version_code": self.version_code,
            "min_version": self.min_version,
            "max_version": self.max_version,
            "content_title": self.content_title,
            "update_time": self.update_time,
            "package": self.package.uid,
            "locales": self.get_locales(),
            "package_name": self.package.uid,
            "change_log": self.change_log,
            "is_auto": self.auto,
            "is_force": self.is_force,
            "os": self.os.lower(),
            "sample": self.sample,
            "valid_time": int(time.mktime(self.valid_time.timetuple())),
            "invalid_time": int(time.mktime(self.invalid_time.timetuple())),
            "apk_size": self.apk_size,
            "sources": self.sourceset.content_dict(),
            "button": self.get_buttons(),
            "os_versions": self.os_versions.content_dict(),
            "mobiles": self.mobiles.content_dict(),
            "cpus": self.cpus.content_dict(),
            "manual_os_versions": self.manual_os_versions.content_dict(),
            "manual_mobiles": self.manual_mobiles.content_dict(),
            "manual_cpus": self.manual_cpus.content_dict(),
            "last_modified": int(time.time())
        }
        return result_dict

    def __unicode__(self):
        return self.title

    class Meta:
        app_label = 'updateservice'


class Sign(models.Model):
    hash_code = models.CharField('Hash', max_length=100, blank=True)
    source = models.CharField('渠道', max_length=200, blank=True)
    version = models.IntegerField('版本号', default=0, blank=True)
    vname = models.CharField('版本名', max_length=200, blank=True)

    class Meta:
        abstract = True


class Patch(BaseOnline):
    update_file = models.FileField(upload_to=PATCH_PATH, verbose_name='补丁文件')
    inc_size = models.CharField(max_length=50, blank=True)
    old_version = models.IntegerField('旧版版本号', default=0, blank=True)
    old_vname = models.CharField('旧版版本名', max_length=200, blank=True)
    new_version = models.IntegerField('新版版本号', default=0, blank=True)
    new_vname = models.CharField('新版版本名', max_length=200, blank=True)
    url = models.CharField(max_length=2000, blank=True)
    hashcode = models.CharField(max_length=50)
    last_modified = models.DateTimeField(auto_now=True)

    def content_dict(self):
        result_dict = {
            'id': self.id,
            'old_version': self.old_version,
            'new_version': self.new_version,
            'url': self.url,
            'inc_size': self.inc_size,
            'hashcode': self.hashcode
        }
        return result_dict

    def save(self, *args, **kwargs):
        super(Patch, self).save(*args, **kwargs)
        inc_size = self.update_file.size
        if inc_size >= MB:
            self.inc_size = '%.1fMB' % (inc_size * 1.0 / MB)
        elif inc_size >= KB:
            self.inc_size = '%sKB' % (inc_size / KB)
        else:
            self.inc_size = '%sB' % inc_size
        patch_content = self.update_file.read()
        if patch_content:
            self.hashcode = md5(patch_content)
        super(Patch, self).save()

    def __unicode__(self):
        return os.path.basename(self.update_file.name)

    class Meta:
        abstract = True


class File(models.Model):
    update_file = models.FileField(upload_to=FILE_PATH, verbose_name='完整APK文件',
                                   help_text='保存时生产Patch文件')
    version = models.IntegerField('版本号', default=0, blank=True)
    vname = models.CharField('版本名', max_length=200, blank=True)

    def save(self, request=None, *args, **kwargs):
        if request:
            try:
                super(File, self).save(*args, **kwargs)
                current_file = os.path.join(MEDIA_ROOT, self.update_file.name)
                patch_path = os.path.join(MEDIA_ROOT, PATCH_PATH)
                logger.info(current_file)
                command = "unzip -o %s -d %s" % (current_file, patch_path)
                logger.info(command)
                result = subprocess.call(command, shell=True)
                logger.info(result)
                info_file = os.path.join(patch_path, 'info.txt')
                with open(info_file, 'r') as f:
                    for line in f:
                        patch_name, patch_info = line.split(':')
                        source_info, package_name, old_version, old_vname, new_version, new_vname = patch_info.split(
                            ';')
                        self.version = new_version
                        self.vname = new_vname
                        old_version = int(old_version)
                        new_version = int(new_version)
                        patch_name = os.path.join(PATCH_PATH, patch_name)
                        patch_file = os.path.join(MEDIA_ROOT, patch_name)
                        with open(patch_file, 'r') as patch:
                            patch_hash = md5(patch.read())
                            package = Package.objects.get(uid=package_name)
                            patch_obj, created = self.patch_class.objects.get_or_create(
                                hashcode=patch_hash, update_file=patch_name, package=package,
                                old_version=old_version, old_vname=old_vname, new_version=new_version, new_vname=new_vname)
                            for source_pair in source_info.split(','):
                                hash_code, source = source_pair.split('-')
                                obj, created = self.patch_class.sign_class.objects.get_or_create(
                                    hash_code=hash_code,
                                    package=package, source=source, version=old_version, vname=old_vname)
                                patch_obj.signs.add(obj)
                super(File, self).save(*args, **kwargs)
                os.remove(info_file)
            except Exception, e:
                logger.exception(e)
                messages.error(request, e)
        else:
            super(File, self).save(*args, **kwargs)

    def __unicode__(self):
        return os.path.basename(self.update_file.name)

    class Meta:
        abstract = True


class UpdateButtonShip(models.Model):
    update = models.ForeignKey(Update)
    button = models.ForeignKey(Button)
    order = models.IntegerField()

    class Meta:
        app_label = 'updateservice'


class UpdateButtonShipInline(EnhancedAdminInline):
    model = UpdateButtonShip
    extra = 1

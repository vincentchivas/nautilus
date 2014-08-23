#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# @Author : Jun Wang
# @Date : 2012-7-10
# Email: jwang@bainainfo.com
import os
import logging
from datetime import datetime
from django.db import models
from django.conf import settings
from dolphinopadmin.utils import scp
from dolphinopadmin.remotedb import config, basedb


config(basedb, settings.ENV_CONFIGURATION)

logger = logging.getLogger('dolphinopadmin.admin')

ALL_FLAG = 'all_condition'
OTHER = 'other_condition'
SERVERS = settings.ENV_CONFIGURATION


class BaseOnline(models.Model):

    is_upload_local = models.BooleanField(
        default=False, verbose_name="上传到本地服务器")
    is_upload_china = models.BooleanField(
        default=False, verbose_name="上传到中国服务器")
    is_upload_ec2 = models.BooleanField(default=False, verbose_name="上传到国外服务器")

    class Meta:
        abstract = True


class BaseFile(models.Model):

    last_modified = models.DateTimeField(auto_now_add=True)

    upload_local = models.DateTimeField(
        auto_now_add=True, verbose_name="上传到本地服务器时间")
    upload_china = models.DateTimeField(
        auto_now_add=True, verbose_name="上传到中国服务器时间")
    upload_ec2 = models.DateTimeField(
        auto_now_add=True, verbose_name="上传到国外服务器时间")

    def upload_file(self, field, server, force=False):
        if hasattr(self, field):
            time_field = 'upload_%s' % server
            upload_time = getattr(self, time_field)
            file_obj = getattr(self, field)
            if force or upload_time <= self.last_modified:
                local_base = settings.MEDIA_ROOT
                local = os.path.join(local_base, file_obj.name)
                remote_base = '/home/static/resources'
                remote = os.path.join(remote_base, file_obj.name)
                result = scp.scp(SERVERS[server]['statics'], 'static',
                                 '/var/app/data/dolphinopadmin-service/static.pem', local, remote)
                if not result:
                    raise ValueError('上传文件%s失败' % file_obj)
                setattr(self, time_field, datetime.now())
            self.url = 'http://' + \
                SERVERS[server]['domain'] + '/resources/' + file_obj.name
            self.save(False)
        else:
            raise KeyError('字段%s不存在' % field)

    def save(self, modified=True):
        if modified:
            self.last_modified = datetime.now()
        super(BaseFile, self).save()

    class Meta:
        abstract = True


class BaseItem(models.Model):

    title = models.CharField(max_length=200)
    url = models.CharField(max_length=2000)

    def content_dict(self):
        result_dict = {
            "title": self.title,
            "url": self.url,
        }
        return result_dict

    def __unicode__(self):
        return "%s(%.80s)" % (self.title, self.url)

    class Meta:
        abstract = True


class BasePackage(models.Model):

    package = models.CharField(max_length=200)

    def content_dict(self):
        result_dict = {
            "package": self.package,
        }
        return result_dict

    def __unicode__(self):
        return self.package

    class Meta:
        abstract = True


class BaseSource(models.Model):

    source = models.CharField(max_length=100)

    def content_dict(self):
        result_dict = {
            "source": self.source,
        }
        return result_dict

    def __unicode__(self):
        return self.source

    class Meta:
        abstract = True


class BaseSourceSet(models.Model):

    name = models.CharField(max_length=100)
    exclude = models.BooleanField('排除所选渠道', default=False)

    def get_m2m_dict(self, field, key, exclude_field=None):
        obj_list = getattr(self, field).all()
        field_dict = {'include': [], 'exclude': []}
        item_list = []
        for obj in obj_list:
            item_list.append(obj.content_dict()[key])
        if exclude_field and getattr(self, exclude_field):
            field_dict = {'include': [ALL_FLAG], 'exclude': item_list}
        else:
            if not item_list:
                item_list = [ALL_FLAG]
            field_dict = {'include': item_list, 'exclude': []}
        return field_dict

    def content_dict(self):
        return self.get_m2m_dict('sources', 'source', 'exclude')

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True


class BaseProduct(models.Model):
    name = models.CharField('产品名称', max_length=200)
    uid = models.CharField('唯一标识', max_length=200,
                           unique=True, help_text='客户端一般用包名，其它单独确定')

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True


class BaseOsVersion(models.Model):

    os_version = models.CharField(max_length=200)

    def content_dict(self):
        result_dict = {
            "os_version": self.os_version,
        }
        return result_dict

    def __unicode__(self):
        return self.os_version

    class Meta:
        abstract = True


class BaseResolution(models.Model):

    resolution = models.CharField(max_length=100)

    def content_dict(self):
        result_dict = {
            "resolution": self.resolution,
        }
        return result_dict

    def __unicode__(self):
        return self.resolution

    class Meta:
        abstract = True


class BaseMobile(models.Model):

    mobile = models.CharField(max_length=100)

    def content_dict(self):
        result_dict = {
            "mobile": self.mobile,
        }
        return result_dict

    def __unicode__(self):
        return self.mobile

    class Meta:
        verbose_name = '机型'
        verbose_name_plural = '机型'
        abstract = True


class BaseRom(models.Model):

    rom = models.CharField(max_length=200)

    def content_dict(self):
        result_dict = {
            "rom": self.rom,
        }
        return result_dict

    def __unicode__(self):
        return self.rom

    class Meta:
        abstract = True


class BaseCPU(models.Model):

    cpu = models.CharField(max_length=100)

    def content_dict(self):
        result_dict = {
            "cpu": self.cpu,
        }
        return result_dict

    def __unicode__(self):
        return self.cpu

    class Meta:
        abstract = True


class BaseMobileOperator(models.Model):

    operator = models.CharField(max_length=100, verbose_name="Mobile Operator")

    def content_dict(self):
        result_dict = {
            "operator": self.operator,
        }
        return result_dict

    def __unicode__(self):
        return self.operator

    class Meta:
        abstract = True

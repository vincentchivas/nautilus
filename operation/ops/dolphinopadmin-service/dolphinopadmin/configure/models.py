#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2013 Baina Info Inc. All rights reserved.
# coder yfhe
import logging
#import time
from django.utils.translation import ugettext_lazy as _
from datetime import datetime
from django.db import models
from dolphinopadmin.base.content import ALL_FLAG
#from dolphinopadmin.base.utils import now, forever

logger = logging.getLogger('dolphinopadmin.admin')

ITEM_HELP_TEXT = '一般只添加新的渠道,不要修改已有的渠道,避免影响其它产品'


def get_m2m_dict(self, field, key, exclude_field=None):
    obj_list = getattr(self, field).all()
    field_dict = {'include': [], 'exclude': []}
    item_list = []
    for obj in obj_list:
        item_list.append(getattr(obj, key))
    if exclude_field and getattr(self, exclude_field):
        field_dict = {'include': [ALL_FLAG], 'exclude': item_list}
    else:
        if not item_list:
            item_list = [ALL_FLAG]
        field_dict = {'include': item_list, 'exclude': []}
    return field_dict


def get_m2m_rule(self, field, key, exclude_field=None):
    obj_list = getattr(self, field).all()
    field_dict = {'include': [], 'exclude': []}
    item_list = []
    for obj in obj_list:
        item_list.append(getattr(obj, key))
    if not item_list:
        item_list = None
    if exclude_field is None:
        return item_list
    elif exclude_field and getattr(self, exclude_field):
        #field_dict = {'include': None, 'exclude': item_list}
        field_dict = {'include': None, 'exclude': item_list}
    else:
        field_dict = {'include': item_list, 'exclude': []}
    return field_dict


class Package(models.Model):
    name = models.CharField('产品名称', max_length=200)
    uid = models.CharField('包名', max_length=200,
                           unique=True, help_text='客户端一般用包名，其它单独确定')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = '产品'
        verbose_name_plural = '产品'
        app_label = 'configure'


class Source(models.Model):

    source = models.CharField(max_length=100, help_text=ITEM_HELP_TEXT)

    def __unicode__(self):
        return self.source

    class Meta:
        verbose_name = '渠道'
        verbose_name_plural = '渠道'
        app_label = 'configure'


class SourceSet(models.Model):

    name = models.CharField(max_length=100)
    exclude = models.BooleanField('排除所选渠道', default=False)
    sources = models.ManyToManyField(
        Source, blank=True, help_text=ITEM_HELP_TEXT)

    def content_dict(self):
        return get_m2m_dict(self, 'sources', 'source', 'exclude')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = '渠道集合'
        verbose_name_plural = '渠道集合'
        app_label = 'configure'


class Locale(models.Model):

    locale = models.CharField(max_length=100, help_text=ITEM_HELP_TEXT)

    def __unicode__(self):
        return self.locale

    class Meta:
        verbose_name = '语言'
        verbose_name_plural = '语言'
        app_label = 'configure'


class LocaleSet(models.Model):

    name = models.CharField(max_length=100)
    exclude = models.BooleanField('排除所选语言', default=False)
    locales = models.ManyToManyField(
        Locale, blank=True, help_text=ITEM_HELP_TEXT)

    def content_dict(self):
        return get_m2m_dict(self, 'locales', 'locale', 'exclude')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = '语言集合'
        verbose_name_plural = '语言集合'
        app_label = 'configure'


class VersionCode(models.Model):
    package = models.ForeignKey(Package, verbose_name='产品')
    vname = models.CharField('版本名称', max_length=200)
    version = models.IntegerField('版本号')

    def __unicode__(self):
        return '%s-%d' % (self.vname, self.version)

    class Meta:
        verbose_name = '版本名称和版本号映射'
        verbose_name_plural = '版本名称和版本号映射'
        app_label = 'configure'


class OSVersion(models.Model):

    os_version = models.CharField(
        max_length=200, verbose_name='系统版本', help_text=ITEM_HELP_TEXT)

    def content_dict(self):
        result_dict = {
            "os_version": self.os_version,
        }
        return result_dict

    def __unicode__(self):
        return self.os_version

    class Meta:
        verbose_name = '系统版本'
        verbose_name_plural = '系统版本'
        app_label = 'configure'


class OSVersionSet(models.Model):

    name = models.CharField(max_length=100)
    exclude = models.BooleanField('排除所选渠道', default=False)
    os_versions = models.ManyToManyField(
        OSVersion, blank=True, help_text=ITEM_HELP_TEXT)

    def content_dict(self):
        return get_m2m_dict(self, 'os_versions', 'os_version', 'exclude')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = '系统版本集合'
        verbose_name_plural = '系统版本集合'
        app_label = 'configure'


class Mobile(models.Model):

    mobile = models.CharField(
        max_length=100, verbose_name='机型', help_text=ITEM_HELP_TEXT)

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
        app_label = 'configure'


class MobileSet(models.Model):

    name = models.CharField(max_length=100)
    exclude = models.BooleanField('排除所选渠道', default=False)
    mobiles = models.ManyToManyField(
        Mobile, blank=True, help_text=ITEM_HELP_TEXT)

    def content_dict(self):
        return get_m2m_dict(self, 'mobiles', 'mobile', 'exclude')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = '机型集合'
        verbose_name_plural = '机型集合'
        app_label = 'configure'


class CPU(models.Model):

    cpu = models.CharField(max_length=100, help_text=ITEM_HELP_TEXT)

    def __unicode__(self):
        return self.cpu

    class Meta:
        app_label = 'configure'


class CPUSet(models.Model):

    name = models.CharField(max_length=100)
    exclude = models.BooleanField('排除所选渠道', default=False)
    cpus = models.ManyToManyField(CPU, blank=True, help_text=ITEM_HELP_TEXT)

    def content_dict(self):
        return get_m2m_dict(self, 'cpus', 'cpu', 'exclude')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'CPU集合'
        verbose_name_plural = 'CPU集合'
        app_label = 'configure'


class Operator(models.Model):

    operator = models.CharField(max_length=100, help_text=ITEM_HELP_TEXT)
    code = models.CharField(
        max_length=100, help_text='运营商代码，用逗号分隔，移动为00,02,联通为01,电信为03，其它情况为other_condition')

    def __unicode__(self):
        return '%s(%s)' % (self.operator, self.code)

    class Meta:
        app_label = 'configure'


class Location(models.Model):

    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200, help_text=ITEM_HELP_TEXT)

    def __unicode__(self):
        return self.location

    class Meta:
        app_label = 'configure'


class Rule(models.Model):

    name = models.CharField(max_length=100, help_text=ITEM_HELP_TEXT)
    min_version = models.IntegerField()
    max_version = models.IntegerField()
    packages = models.ManyToManyField(Package)
    operators = models.ManyToManyField(Operator, blank=True)
    exclude_source = models.BooleanField('排除所选渠道', default=False)
    sources = models.ManyToManyField(Source, blank=True)
    exclude_locale = models.BooleanField('排除所选语言', default=False)
    locales = models.ManyToManyField(Locale, blank=True)
    exclude_location = models.BooleanField('排除所选位置', default=False)
    locations = models.ManyToManyField(Location, blank=True)
    min_sdk = models.IntegerField(verbose_name=_('min os version'), default=0)
    max_sdk = models.IntegerField(verbose_name=_('max os version'), default=0)
    gray_level = models.IntegerField(verbose_name=_('gray level'), default=100, help_text=_('number limit 0 to 100'))
    gray_level_start = models.IntegerField(verbose_name=_('gray level start'), default=1, help_text=_('it must lower than 100 - gray level '))
    #start_time = models.DateTimeField(default=datetime.now)
    #end_time = models.DateTimeField(default=datetime.now)

    def get_operators(self):
        operator_list = self.operators.all()
        operators = []
        for obj in operator_list:
            operators.extend(obj.code.split(','))
        if not len(operators):
            operators.append(ALL_FLAG)
        return operators

    def content_dict(self):
        min_mark = self.gray_level_start
        min_mark = 1 if min_mark < 1 else min_mark
        max_mark = self.gray_level + min_mark
        max_mark = 101 if max_mark > 101 else max_mark
        result_dict = {
            'min_version': self.min_version,
            'max_version': self.max_version,
            'max_sdk': self.max_sdk,
            'min_sdk': self.min_sdk,
            'packages': get_m2m_rule(self, 'packages', 'uid'),
            'operators': self.get_operators(),
            'sources': get_m2m_dict(self, 'sources', 'source', 'exclude_source'),
            'locales': get_m2m_dict(self, 'locales', 'locale', 'exclude_locale'),
            'locations': get_m2m_dict(self, 'locations', 'location', 'exclude_location'),
            'min_mark': min_mark,
            'max_mark': max_mark
            #'start_time': int(time.mktime(self.start_time.timetuple())),
            #'end_time': int(time.mktime(self.end_time.timetuple()))
        }
        return result_dict

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = '配置条件'
        verbose_name_plural = '配置条件'
        app_label = 'configure'

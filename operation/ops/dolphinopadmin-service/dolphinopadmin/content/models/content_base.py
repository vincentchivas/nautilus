# -*- coding:utf-8 -*-
'''
Copyright (c) 2012 Baina Info Inc. All rights reserved.
@Author : Jun Wang
@Date : 2012-2-13
'''
import time
from django.db import models
from dolphinopadmin.base.models import BaseOnline

TIME_DELTA = 8

COLOR_CHOICES = (
    (u'none', u'none'),
    (u'#FF0000', u'red'),
)


class Package(models.Model):

    Local_CHOICES = (
        (u'zh_CN', u'zh_CN'),
        (u'en_US', u'en_US'),
        (u'0', u'N/A'),
    )
    OS_CHOICES = (
        (u'all', u'all'),
        (u'android', u'android'),
        (u'androidpad', u'androidpad'),
        (u'iphone', u'iphone'),
        (u'ipad', u'ipad'),
        (u'wphone', u'wphone'),
        (u'wslate', u'wslate'),
    )

    title = models.CharField(max_length=100)
    os = models.CharField(max_length=100, choices=OS_CHOICES, default='all')
    device = models.CharField(max_length=100)
    locale = models.CharField(max_length=100, choices=Local_CHOICES)
    packagename = models.CharField(max_length=100)

    def content_dict(self):
        result_dict = {
            "packagename": self.packagename,
        }
        return result_dict

    def __unicode__(self):
        return self.title

    class Meta:
        app_label = 'content'
        abstract = True


class PackageSet(models.Model):
    name = models.CharField(max_length=100)

    def content_dict(self):
        result_dict = {
            "name": self.name,
        }
        return result_dict

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'content'
        abstract = True


class SourceSet(models.Model):
    name = models.CharField(max_length=100)

    def get_source(self, class_name):
        item_list = []
        items = class_name.objects.filter(sourceset__id=self.id)
        for item in items:
            item_dict = item.content_dict()
            item_list.append(item_dict['source'])
        return item_list

    def content_dict(self):
        result_dict = {
        }
        return result_dict

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'content'
        abstract = True


class Source(models.Model):

    name = models.CharField(max_length=100)
    source = models.CharField(max_length=100)

    def content_dict(self):
        result_dict = {
            "source": self.source,
        }
        return result_dict

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'content'
        abstract = True


class Section(BaseOnline):

    TEST_CHOICES = (
        (u'test', u'test'),
        (u'official', u'official'),
    )
    name = models.CharField(max_length=100)
    title = models.CharField(blank=True, max_length=100)
    icon = models.URLField(max_length=1000)
    order = models.IntegerField()
    api = models.CharField(
        max_length=100, default='official', choices=TEST_CHOICES)
    lastmodified = models.DateTimeField(
        auto_now=True, verbose_name='lastModified')

    def content_dict(self):
        result_dict = {
            "id": self.id,
            "title": self.title,
            "api": self.api,
            "ico": self.icon,
            "layout": int(self.layout),
            "order": self.order,
            "time": int(time.time()),
        }
        return result_dict

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'content'
        abstract = True


class Group(models.Model):

    API_CHOICES = (
        (1, '1'),
        (2, '2'),
    )
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100, blank=True)
    api_version = models.IntegerField(default=1, choices=API_CHOICES)

    def content_dict(self):
        result_dict = {
            "group": self.title,
            "api_version": self.api_version,
        }
        return result_dict

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'content'
        abstract = True


class Category(models.Model):

    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100, blank=True)
    url = models.CharField(max_length=1000, blank=True)

    def content_dict(self):
        result_dict = {
            "title": self.title,
            "url": self.url,
        }
        return result_dict

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'content'
        abstract = True


class Novel(BaseOnline):

    name = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    url = models.CharField(max_length=1000, blank=True)

    def content_dict(self):
        result_dict = {
            "id": self.id,
            "title": self.title,
            "url": self.url,
        }
        return result_dict

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'content'
        abstract = True


class Item(models.Model):

    title = models.CharField(max_length=100)
    url = models.CharField(max_length=1000)
    color = models.CharField(
        default='none', max_length=100, choices=COLOR_CHOICES)

    def content_dict(self):
        result_dict = {
            "title": self.title,
            "url": self.url,
        }
        if self.color and self.color != 'none':
            result_dict['color'] = self.color
        return result_dict

    def __unicode__(self):
        return "%s(%.50s)" % (self.title, self.url)

    class Meta:
        app_label = 'content'
        abstract = True

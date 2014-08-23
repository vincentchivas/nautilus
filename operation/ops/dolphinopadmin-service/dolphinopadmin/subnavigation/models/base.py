#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On August 25, 2012
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import time
from django.db import models

TIME_DELTA = 8


class Page(models.Model):

    PAGE_TYPE_CHOICES = (
        (u'normal', u'normal'),
        (u'news', u'news'),
        (u'novel', u'novel'),
    )

    page_name = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    page_type = models.CharField(
        max_length=100, default='normal', choices=PAGE_TYPE_CHOICES)
    is_upload_dev = models.BooleanField(default=False)
    is_upload_local = models.BooleanField(default=False)
    is_upload_china = models.BooleanField(default=False)
    is_upload_ec2 = models.BooleanField(default=False)

    def content_dict(self):
        result_dict = {
            "id": self.id,
            "title": self.title,
            "page_name": self.page_name,
            "page_type": self.page_type,
            "last_modified": int(time.time()),
        }
        return result_dict

    def __unicode__(self):
        return self.title

    class Meta:
        abstract = True


class Category(models.Model):

    LAYOUT_CHOICES = (
        (u'normal', u'normal'),
        (u'news', u'news'),
        (u'feature', u'feature'),
    )
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100, blank=True)
    url = models.CharField(max_length=1000, blank=True)
    layout = models.CharField(
        max_length=100, default='normal', choices=LAYOUT_CHOICES)
    column = models.IntegerField()

    def content_dict(self):
        result_dict = {
            "title": self.title,
            "url": self.url,
            "layout": self.layout,
            "column": self.column
        }
        return result_dict

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True

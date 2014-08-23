#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On November 5, 2012
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import time
from django.db import models
from django.conf import settings
from dolphinopadmin.base.models import BaseOnline
from dolphinopadmin.remotedb.navigate import config

config(servers=settings.ENV_CONFIGURATION)

TIME_DELTA = 8


class Section(BaseOnline):

    LAYOUT_CHOICES = (
        (u'00-', u'1'),
        (u'10-', u'2'),
        (u'2-0', u'3'),
        (u'111', u'4'),
        (u'13-', u'5'),
    )
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200, blank=True)
    more = models.CharField(max_length=200, blank=True)
    more_url = models.CharField(max_length=2000, blank=True)
    column = models.IntegerField()
    order = models.IntegerField()
    style = models.CharField(
        max_length=100, default='1', choices=LAYOUT_CHOICES)

    def content_dict(self):
        result_dict = {
            "id": self.id,
            "title": self.title,
            "more": self.more,
            "more_url": self.more_url,
            "column": self.column,
            "order": self.order,
            "style": self.style,
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
    )
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100, blank=True)
    url = models.CharField(max_length=2000, blank=True)
    style = models.CharField(
        max_length=100, default='normal', choices=LAYOUT_CHOICES)

    def content_dict(self):
        result_dict = {
            "title": self.title,
            "url": self.url,
            "style": self.style,
        }
        return result_dict

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True

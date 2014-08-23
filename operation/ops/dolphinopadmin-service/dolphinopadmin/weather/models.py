#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On Mar 7, 2013
# @Author : Jun Wang
# Email: jwang@bainainfo.com
from django.db import models
from dolphinopadmin.base.models import BaseOnline, BaseFile
from dolphinopadmin.configure.models import Package
from dolphinopadmin.resource.models import Icon


class Background(BaseFile):
    background = models.FileField(upload_to=u'weather/bg/')
    title = models.CharField(max_length=100, blank=True)
    url = models.CharField(max_length=2000, blank=True)

    def content_dict(self, pic=True):
        result_dict = {
            "id": self.id,
        }
        return result_dict

    def __unicode__(self):
        return "%s" % (self.title or self.background)

    class Meta:
        app_label = 'weather'


class Display(BaseOnline):

    name = models.CharField(max_length=100, blank=True)
    state = models.CharField('天气', max_length=100)
    description = models.CharField('提示', max_length=200, blank=True)
    city = models.CharField('城市', max_length=100, default='default')
    icon = models.ForeignKey(Icon)
    background = models.ForeignKey(Background)
    package = models.ForeignKey(Package)
    begin = models.IntegerField(default=0)
    end = models.IntegerField(default=24)

    def content_dict(self, server):
        self.check()
        self.icon.upload_file(server)
        self.background.upload_file('background', server)
        result_dict = {
            "id": self.id,
            "state": self.state,
            "des": self.description,
            "cityName": self.city,
            "icon": self.icon.get_url(server),
            "bg": self.background.url,
            "begin": self.begin,
            "end": self.end,
            "package": self.package.uid
        }
        return result_dict

    def check(self):
        pass

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'weather'

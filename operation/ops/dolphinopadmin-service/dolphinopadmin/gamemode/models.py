#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On Apr 3, 2013
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import time
from django.db import models
from dolphinopadmin.base.models import BaseOnline
from dolphinopadmin.configure.models import Package, SourceSet
from dolphinopadmin.resource.models import Icon

MODE_CHOICES = (
    ('game', 'game'),
    ('webapp', 'webapp')
)


class Game(BaseOnline):

    title = models.CharField(max_length=200)
    url = models.CharField(max_length=2000)
    icon = models.ForeignKey(Icon)
    mode = models.CharField(max_length=100, choices=MODE_CHOICES)
    dolphin = models.CharField('海豚浏览器下载链接', max_length=2000, blank=True)
    package = models.ForeignKey(Package)
    sourceset = models.ForeignKey(SourceSet)
    min_version = models.IntegerField()
    max_version = models.IntegerField()
    last_modified = models.DateTimeField(auto_now=True)

    def content_dict(self, server):
        self.icon.upload_file(server)
        result_dict = {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "icon": self.icon.get_url(server),
            "dolphin_download": self.dolphin,
            "mode": self.mode,
            "package": self.package.uid,
            "sources": self.sourceset.content_dict(),
            "min_version": self.min_version,
            "max_version": self.max_version,
            "last_modified": int(time.time())
        }
        return result_dict

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = '模式配置'
        verbose_name_plural = '模式配置'
        app_label = 'gamemode'

#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2013 Baina Info Inc. All rights reserved.
# Created On Apr 24, 2013
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import time
from django.db import models
from dolphinopadmin.base.models import BaseOnline
from dolphinopadmin.configure.models import Package
from dolphinopadmin.resource.models import Icon


class Site(BaseOnline):
    title = models.CharField(max_length=200)
    url = models.CharField(
        max_length=2000, help_text='可以使用通配符*,比如*.baidu.com匹配二级域名')
    color = models.CharField(max_length=200, blank=True)
    icon = models.ForeignKey(Icon)
    package = models.ForeignKey(Package)
    min_version = models.IntegerField()
    max_version = models.IntegerField()

    def content_dict(self, server):
        self.icon.upload_file(server)
        result_dict = {
            "id": self.id,
            "url": self.url,
            "color": self.color,
            "icon": self.icon.get_url(server),
            "package": self.package.uid,
            "max_version": self.max_version,
            "min_version": self.min_version,
            "last_modified": int(time.time())
        }
        return result_dict

    def __unicode__(self):
        return self.title

    class Meta:
        app_label = 'topsite'

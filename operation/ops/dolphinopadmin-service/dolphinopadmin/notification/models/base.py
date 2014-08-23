#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On May 10, 2013
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import time
from django.db import models
from datetime import datetime
from dolphinopadmin.base.models import BaseOnline


class Notification(BaseOnline):

    name = models.CharField(max_length=100)
    url = models.CharField(max_length=2000)
    update = models.BooleanField(default=True)
    update_time = models.DateTimeField(default=datetime.now)
    min_version = models.IntegerField()
    max_version = models.IntegerField()

    def content_dict(self):
        result_dict = {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "update": self.update,
            "update_time": time.mktime(self.update_time.timetuple()),
            "min_version": self.min_version,
            "max_version": self.max_version,
            "locales": self.localeset.content_dict(),
            "package": self.package.uid,
            "sources": self.sourceset.content_dict(),
            "last_modified": int(time.time())
        }
        return result_dict

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True

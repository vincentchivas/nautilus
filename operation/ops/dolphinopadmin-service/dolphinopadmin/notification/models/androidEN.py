#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On May 10, 2013
# @Author : Jun Wang
# Email: jwang@bainainfo.com
from django.db import models
from dolphinopadmin.configure.models import Package, SourceSet, LocaleSet
from base import Notification


class AndroidENNotification(Notification):

    package = models.ForeignKey(Package)
    sourceset = models.ForeignKey(SourceSet)
    localeset = models.ForeignKey(LocaleSet)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'notification'

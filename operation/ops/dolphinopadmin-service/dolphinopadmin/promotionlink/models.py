#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On August 3, 2012
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import time
import re
import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
# from dolphinopadmin.base.models import BaseOnline
from dolphinopadmin.base.base_model import BaseStatus
from dolphinopadmin.configure.models import Rule
from dolphinopadmin.remotedb.promotionlink import config
from dolphinopadmin.base.utils import now, forever

config(servers=settings.ENV_CONFIGURATION)

# class Plink(BaseOnline):


class Plink(BaseStatus):
    title = models.CharField(max_length=200, verbose_name=_("Title"))
    url = models.CharField(max_length=5000, blank=True,
                           null=True, verbose_name=_("URL"))
    update_time = models.DateTimeField(
        auto_now=True, verbose_name=_("Update Time"))
    weight = models.IntegerField(default=1, verbose_name=_("Weight"))
    images = models.TextField(
        max_length=2000, blank=True, verbose_name=_("Images"))
    pop = models.BooleanField(default=False, blank=True, verbose_name=_("Pop"))
    rule = models.ForeignKey(Rule, related_name='+', verbose_name=_("Rule"))
    subtitle = models.CharField(
        max_length=200, blank=True, verbose_name=_("Subtitle"))
    valid_time = models.DateTimeField(
        default=datetime.datetime.now, verbose_name=_("Valid Time"))
    invalid_time = models.DateTimeField(
        default=datetime.datetime.now, verbose_name=_("Invalid Time"))

    # add for refactoring
    platform = models.CharField(max_length=100, editable=False)

    """
    def get_operators(self):
        operators = []
        if self.cmcc:
            operators.extend(['00', '02'])
        if self.unicom:
            operators.append('01')
        if self.telecom:
            operators.append('03')
        if self.other_operator:
            operators.append(OTHER)
        return operators

    def get_locales(self):
        locales = self.locales.all()
        locale_list = [item.locale for item in locales]
        return locale_list if len(locales) else None
    """

    def content_dict(self, server, is_del=False):
        if is_del:
            return {
                'id': self.id
            }

        rules = self.rule.content_dict()
        rules.update({
            "start_time": self.valid_time + datetime.timedelta(hours=-8) if self.valid_time else now(),
            "end_time": self.invalid_time + datetime.timedelta(hours=-8) if self.invalid_time else forever(),
        })
        result_dict = {
            "id": self.id,
            "Title": self.title,
            "Url": self.url,
            "pop": int(self.pop),
            "_rule": rules,
            "last_modified": int(time.time()),
            "weight": self.weight,
            "images": self.images.split(',') if self.images else [],
            "status": 2
        }
        if self.pop:
            result_dict['subtitle'] = self.subtitle
        return result_dict

    def __unicode__(self):
        return self.title

    def save(self, modified=True):
        self.platform = self.__class__.filters["platform"]
        try:
            if self.pop:
                if not self.images:
                    raise ValueError("image can't be blank")
                patt = re.compile(
                    r'http://[a-zA-Z\d\-\.]+[a-zA-Z#%=&\?\d\-\_\/\.]+[a-zA-Z]')
                self.images = patt.findall(self.images)
                tmp_images = ''
                if len(self.images) == 1:
                    tmp_images = ''.join(self.images)
                else:
                    for index in xrange(len(self.images) - 1):
                        tmp_images += self.images[index] + ','
                    tmp_images += self.images[-1]
                self.images = tmp_images
        except Exception, e:
            return e
        super(Plink, self).save()

    class Meta:
        app_label = 'promotionlink'
        verbose_name = _("PromotionLink")
        verbose_name_plural = _("PromotionLink")

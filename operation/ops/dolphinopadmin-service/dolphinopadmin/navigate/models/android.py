#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On November 5, 2012
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import logging
from django.db import models
from dolphinopadmin.base.models import BaseItem
from dolphinopadmin.configure.models import Package
from dolphinopadmin.base.admin import EnhancedAdminInline
from base import Section, Category


DEFAULT_PALTFORM = 'AndroidCN'

logger = logging.getLogger("dolphinopadmin.admin")


class AndroidCNItem(BaseItem):

    def content_dict(self):
        result_dict = super(AndroidCNItem, self).content_dict()
        return result_dict

    class Meta:
        verbose_name = u'Android Item'
        verbose_name_plural = u'Android Item'
        app_label = 'navigate'


class AndroidCNCategory(Category):

    items = models.ManyToManyField(
        AndroidCNItem, through='AndroidCNCategoryItemShip')

    def get_items(self):
        obj_list = []
        items = AndroidCNCategoryItemShip.objects.filter(
            category__id=self.id).order_by('order')
        for item in items:
            item_dict = item.item.content_dict()
            obj_list.append(item_dict)
        return obj_list

    def content_dict(self):
        result_dict = super(AndroidCNCategory, self).content_dict()
        result_dict['items'] = self.get_items()
        return result_dict

    class Meta:
        verbose_name = u'Android Category'
        verbose_name_plural = u'Android Category'
        app_label = 'navigate'


class AndroidCNSection(Section):

    categories = models.ManyToManyField(
        AndroidCNCategory, through='AndroidCNSectionCategoryShip')
    package = models.ForeignKey(Package)
    platform = models.CharField(max_length=100, default=DEFAULT_PALTFORM)

    def get_categorys(self):
        obj_list = []
        items = AndroidCNSectionCategoryShip.objects.filter(
            page__id=self.id).order_by('order')
        for item in items:
            dic = item.category.content_dict()
            obj_list.append(dic)
        return obj_list

    def content_dict(self):
        result_dict = super(AndroidCNSection, self).content_dict()
        result_dict.update({
            'categories': self.get_categorys(),
            'package': self.package.uid,
            'platform': self.platform,
            'status': 2
        })
        return result_dict

    class Meta:
        verbose_name = u'Android Section'
        verbose_name_plural = u'Android Section'
        app_label = 'navigate'


class AndroidCNSectionCategoryShip(models.Model):

    page = models.ForeignKey(AndroidCNSection)
    category = models.ForeignKey(AndroidCNCategory)
    order = models.IntegerField()

    def __unicode__(self):
        return "%s(%s)" % (self.page, self.category)

    class Meta:
        verbose_name = u"Android Section所关联的Category"
        verbose_name_plural = u"Android Section所关联的Category"
        app_label = 'navigate'


class AndroidCNCategoryItemShip(models.Model):

    category = models.ForeignKey(AndroidCNCategory)
    item = models.ForeignKey(AndroidCNItem)
    order = models.IntegerField()

    def __unicode__(self):
        return "%s(%s)" % (self.category, self.item)

    class Meta:
        verbose_name = u"Android Category所关联的Item"
        verbose_name_plural = u"Android Category所关联的Item"
        app_label = 'navigate'


class AndroidCNSectionCategoryShipInline(EnhancedAdminInline):
    model = AndroidCNSectionCategoryShip
    extra = 1


class AndroidCNCategoryItemShipnline(EnhancedAdminInline):
    model = AndroidCNCategoryItemShip
    extra = 1

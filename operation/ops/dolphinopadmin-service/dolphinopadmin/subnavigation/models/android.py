#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On August 25, 2012
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import logging
from django.db import models
from dolphinopadmin.base.models import BaseItem
from dolphinopadmin.configure.models import Package
from dolphinopadmin.base.admin import EnhancedAdminInline
from base import Page, Category


DEFAULT_PALTFORM = 'AndroidCN'
ALL_SOURCE = 'all_source_flag'

logger = logging.getLogger("dolphinopadmin.admin")


class AndroidCNItem(BaseItem):

    def content_dict(self):
        result_dict = super(AndroidCNItem, self).content_dict()
        return result_dict

    class Meta:
        verbose_name = u'Android Item'
        verbose_name_plural = u'Android Item'
        app_label = 'subnavigation'


class AndroidCNCategory(Category):

    items = models.ManyToManyField(
        AndroidCNItem, through='AndroidCNCategoryItemShip')

    def get_items(self):
        obj_list = []
        items = AndroidCNCategoryItemShip.objects.filter(
            category__id=self.id).order_by('order')
        for item in items:
            item_dict = item.item.content_dict()
            item_dict['order'] = item.order
            obj_list.append(item_dict)
        return obj_list

    def content_dict(self):
        result_dict = super(AndroidCNCategory, self).content_dict()
        result_dict['items'] = self.get_items()
        return result_dict

    class Meta:
        verbose_name = u'Android Category'
        verbose_name_plural = u'Android Category'
        app_label = 'subnavigation'


class AndroidCNPage(Page):

    categories = models.ManyToManyField(
        AndroidCNCategory, through='AndroidCNPageCategoryShip')
    package = models.ForeignKey(Package)
    platform = models.CharField(max_length=100, default=DEFAULT_PALTFORM)

    def get_categorys(self):
        obj_list = []
        items = AndroidCNPageCategoryShip.objects.filter(
            page__id=self.id).order_by('order')
        for item in items:
            dic = item.category.content_dict()
            dic['order'] = item.order
            obj_list.append(dic)
        return obj_list

    def content_dict(self):
        result_dict = super(AndroidCNPage, self).content_dict()
        result_dict['categories'] = self.get_categorys()
        result_dict['package'] = self.package.uid
        result_dict['platform'] = self.platform
        return result_dict

    class Meta:
        verbose_name = u'Android Page'
        verbose_name_plural = u'Android Page'
        app_label = 'subnavigation'


class AndroidCNPageCategoryShip(models.Model):

    page = models.ForeignKey(AndroidCNPage)
    category = models.ForeignKey(AndroidCNCategory)
    order = models.IntegerField()

    def __unicode__(self):
        return u"%s(%s)" % (self.page, self.category)

    class Meta:
        verbose_name = u"Android Page所关联的Category"
        verbose_name_plural = u"Android Page所关联的Category"
        app_label = 'subnavigation'


class AndroidCNCategoryItemShip(models.Model):

    category = models.ForeignKey(AndroidCNCategory)
    item = models.ForeignKey(AndroidCNItem)
    order = models.IntegerField()

    def __unicode__(self):
        return u"%s(%s)" % (self.category, self.item)

    class Meta:
        verbose_name = u"Android Category所关联的Item"
        verbose_name_plural = u"Android Category所关联的Item"
        app_label = 'subnavigation'


class AndroidCNPageCategoryShipInline(EnhancedAdminInline):
    model = AndroidCNPageCategoryShip
    extra = 1


class AndroidCNCategoryItemShipnline(EnhancedAdminInline):
    model = AndroidCNCategoryItemShip
    extra = 1

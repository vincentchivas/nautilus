#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# @Author : Jun Wang
# @Date : 2012-2-25
# Email: jwang@bainainfo.com
import time
from django.db import models
from dolphinopadmin.base.models import BaseOnline
from dolphinopadmin.base.admin import EnhancedAdminInline


class Item(models.Model):

    CATEGORY_CHOICES = (
        (1, u'Add-on'),
        (2, u'Theme'),
    )

    name = models.CharField(max_length=100)
    download_url = models.CharField(max_length=1000)
    application_name = models.CharField(max_length=200)
    icon_url = models.CharField(max_length=1000)
    description = models.CharField(max_length=500)
    long_description = models.TextField(max_length=2000)
    addon_bar_icon_url = models.CharField(max_length=1000)
    packagename = models.CharField(max_length=200, verbose_name='package name')
    show_in_addon_bar = models.BooleanField(default=True)
    is_text_selection_addon = models.BooleanField()

    def content_dict(self):
        result_dict = {
            "id": self.id,
            "name": self.name,
            "download_url": self.download_url,
            "application_name": self.application_name,
            "icon_url": self.icon_url,
            "description": self.description,
            "long_description": self.long_description,
            "addon_bar_icon_url": self.addon_bar_icon_url,
            "package_name": self.packagename,
            "show_in_addon_bar": self.show_in_addon_bar,
            "is_text_selection_addon": self.is_text_selection_addon,
        }
        return result_dict

    def __unicode__(self):
        return "ID:%d name:%s" % (self.id, self.name)

    class Meta:
        app_label = 'addon'


class Addon(BaseOnline):

    name = models.CharField(max_length=200)
    packagename = models.CharField(max_length=500)
    source = models.CharField(max_length=200)
    item = models.ManyToManyField(Item, through='Addon_Item_Ship')

    def get_item(self):
        items = Addon_Item_Ship.objects.filter(addon__id=self.id)
        dict_list = []
        for it in items:
            item_dict = it.item.content_dict()
            item_dict["order"] = it.order
            dict_list.append(item_dict)
        return dict_list

    def content_dict(self):
        result_dict = {
            "id": self.id,
            "items": self.get_item(),
            "packagename": self.packagename,
            "source": self.source,
            "last_modified": int(time.time())
        }
        return result_dict

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'addon'


class Addon_Item_Ship(models.Model):
    addon = models.ForeignKey(Addon)
    item = models.ForeignKey(Item)
    order = models.IntegerField()

    class Meta:
        app_label = 'addon'


class Addon_Item_Ship_Inline(EnhancedAdminInline):
    model = Addon_Item_Ship
    raw_id_fields = ['item']
    extra = 1

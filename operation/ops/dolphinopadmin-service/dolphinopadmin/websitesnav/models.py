#/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: qtgan
# Date: 2013/12/12

import json
import time
from django.db import models
from django.utils.translation import ugettext_lazy as _
from dolphinopadmin.base.base_model import BaseStatus
from dolphinopadmin.base.content import NAV_FUNCTION as functions
from dolphinopadmin.configure.models import Rule
from dolphinopadmin.resource.models import Icon


class Website(models.Model):
    # The title of the website
    site_title = models.CharField(max_length=30, verbose_name=_("site title"))
    url = models.URLField(max_length=300)  # The url of the website
    icon = models.ForeignKey(
        Icon, verbose_name=_("icon"), null=True, blank=True)
    function = models.CharField(max_length=100, editable=False)
    # is_upload_local = False

    def __unicode__(self):
        # return u"%s %s" % (self.category_belong, self.site_title)
        return self.site_title

    def save(self, *args, **kwargs):
        self.function = self.__class__.filters['function']
        super(Website, self).save(*args, **kwargs)

    def content_dict(self, server, icon=True):
        result_dict = {
            "title": self.site_title,
            "url": self.url,
        }
        if not icon:
            return result_dict
        else:
            if self.icon is None:
                raise ValueError(
                    _(" site %s's icon field is null" % self.site_title))
            self.icon.upload_file(server)
            result_dict.update({"icon_url": self.icon.get_url(server)})
            return result_dict

    class Meta:
        app_label = 'websitesnav'
        verbose_name = _("Item")
        verbose_name_plural = _("Item")
        ordering = ['-id']


class SiteCategory(models.Model):
    category_name = models.CharField(
        max_length=20, verbose_name=_("category name"))
    function = models.CharField(max_length=100, editable=False)

    def __unicode__(self):
        return self.category_name

    def sites_count(self):
        return self.websitesnav_sitecategorywebsiteship_set.count()

    def save(self, *args, **kwargs):
        try:
            self.function = self.__class__.filters['function']
        except Exception, e:
            print "SiteCategory.function is: ", self.function
        super(SiteCategory, self).save(*args, **kwargs)

    def content_dict(self, server):
        result_dict = {
            "category": self.category_name,
            "sites": []
        }
        ships_with_sites = self.websitesnav_sitecategorywebsiteship_set.all().order_by(
            "order")[:4]
        if len(ships_with_sites) < 4:
            # there should be 4 sites in each category
            raise ValueError(
                _("there should be 4 sites in %sth category" % self.category_name))
        for ship in ships_with_sites:
            site_dict = ship.website.content_dict(server, icon=False)
            result_dict["sites"].append(site_dict)
        return result_dict

    class Meta:
        app_label = 'websitesnav'
        verbose_name = _("Category")
        verbose_name_plural = _("Category")  # name shown in the admin console


class Strategy(BaseStatus):
    title = models.CharField(max_length=100, verbose_name=_("Title"))
    rule = models.ForeignKey(Rule, verbose_name=_('rule'))
    function = models.CharField(max_length=100, editable=False)

    def sites_count(self):
        return self.websitesnav_strategywebsiteship_set.count()

    def categories_count(self):
        return self.websitesnav_strategysitecategoryship_set.count()

    def content_dict(self, server, is_del=False):
        if is_del:
            return {
                "_sync_key": {
                    "id": self.id,
                },
            }
        result_dict = {
            "_sync_key": {
                "id": self.id,
            },
            "mt": time.mktime(self.modified_time.timetuple()),
            "function": self.function,
            "_data": {},
            "_rule": self.rule.content_dict()
        }

        shipswithwebsite = self.websitesnav_strategywebsiteship_set.all().order_by(
            "order")[:9]
        if len(shipswithwebsite) < 9 and self.function == functions[0][0]:
            # there should be 9 website in the strategy
            raise ValueError(
                _("the number of the recommendsites in %sth strategy is less than 9" % self.id))
        elif len(shipswithwebsite) < 4:
            raise ValueError(
                _("the number of sites in %sth strategy is less than 4" % self.id))
        website_list = []
        for ship in shipswithwebsite:
            # site = Website.objects.get(id = ship.website_id)
            if self.function == functions[2][0]:
                # 对于搜索热词，不需要icon_url键值对
                site_dict = ship.website.content_dict(server, icon=False)
            else:
                site_dict = ship.website.content_dict(server)
            website_list.append(site_dict)
        if self.function == functions[0][0]:
            # 如果是navigate功能，则.......
            result_dict["_data"].update({"recommend": website_list})
        else:
            # result_dict["_data"].update({self.function: website_list})
            result_dict["_data"] = website_list
            return result_dict

        # 如果是Navigate功能，则还需要添加进Category数据
        shipswithcategory = self.websitesnav_strategysitecategoryship_set.all().order_by(
            "order")[:4]
        # 只在Recommend功能中检查Category满足4个的条件
        if len(shipswithcategory) < 4:
            # there should be 4 sitecategory in the strategy
            raise ValueError(
                _("the number of sitecategory in %dth strategy is less than 4" % self.id))
        website_list = []  # 清空
        for ship in shipswithcategory:
            # category = SiteCategory.objects.get(id = ship.sitecategory_id)
            category_dict = ship.sitecategory.content_dict(server)
            website_list.append(category_dict)
        result_dict["_data"].update({"category": website_list})
        return result_dict

    def save(self, *args, **kwargs):
        self.function = self.__class__.filters['function']
        super(BaseStatus, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"%s" % self.rule

    class Meta:
        verbose_name = _("Strategy")
        verbose_name_plural = _("Strategy")
        app_label = 'websitesnav'

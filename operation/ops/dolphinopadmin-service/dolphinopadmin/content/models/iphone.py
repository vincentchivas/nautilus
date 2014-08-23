# -*- coding:utf-8 -*-
'''
Copyright (c) 2012 Baina Info Inc. All rights reserved.
@Author : Jun Wang
@Date : 2012-2-13
'''
import logging
from django.db import models
from datetime import datetime
from operator import attrgetter
from dolphinopadmin.base.admin import EnhancedAdminInline
from content_base import *


DEFAULT_PALTFORM = 'iPhone_CN'
logger = logging.getLogger("dolphinopadmin.admin")


class iPhone_PackageSet(PackageSet):
#    package = models.ManyToManyField(iPhone_Package,through='iPhone_set_package_ship')

    def get_packages(self):
        obj_list = []
        packages = iPhone_Package.objects.filter(packageset__id=self.id)
        for item in packages:
            temp = item.content_dict()['packagename']
            obj_list.append(temp)
        return obj_list

    def content_dict(self):
        result_dict = super(iPhone_PackageSet, self).content_dict()
        result_dict['packages'] = self.get_packages()
        return result_dict

    class Meta:
        verbose_name = u'iPhone Package Set'
        verbose_name_plural = u'iPhone Package Set'
        app_label = 'content'

    def save(self, *args, **kwargs):
        super(iPhone_PackageSet, self).save(*args, **kwargs)


class iPhone_Package(Package):
    packageset = models.ForeignKey(iPhone_PackageSet)

    def content_dict(self):
        result_dict = super(iPhone_Package, self).content_dict()
        return result_dict

    class Meta:
        verbose_name = u'iPhone Package'
        verbose_name_plural = u'iPhone Package'
        app_label = 'content'

    def save(self, *args, **kwargs):
        super(iPhone_Package, self).save(*args, **kwargs)


class iPhone_SourceSet(SourceSet):

    def content_dict(self):
        result_dict = super(iPhone_SourceSet, self).content_dict()
        result_dict['sources'] = self.get_source(iPhone_Source)
        return result_dict

    class Meta:
        verbose_name = u'iPhone Source Set'
        verbose_name_plural = u'iPhone Source Set'
        app_label = 'content'

    def save(self, *args, **kwargs):
        super(iPhone_SourceSet, self).save(*args, **kwargs)


class iPhone_Source(Source):
    sourceset = models.ForeignKey(iPhone_SourceSet)

    def content_dict(self):
        result_dict = super(iPhone_Source, self).content_dict()
        return result_dict

    class Meta:
        verbose_name = u'iPhone Source'
        verbose_name_plural = u'iPhone Source'
        app_label = 'content'

    def save(self, *args, **kwargs):
        super(iPhone_Source, self).save(*args, **kwargs)


class iPhone_Item(Item):

    def content_dict(self):
        result_dict = super(iPhone_Item, self).content_dict()
        return result_dict

    class Meta:
        verbose_name = u'iPhone Item'
        verbose_name_plural = u'iPhone Item'
        app_label = 'content'

    def save(self, *args, **kwargs):
        super(iPhone_Item, self).save(*args, **kwargs)


class iPhone_Category(Category):

    item = models.ManyToManyField(
        iPhone_Item, through='iPhone_category_item_ship')

    def get_items(self):
        obj_list = []
        items = iPhone_category_item_ship.objects.filter(
            category__id=self.id).order_by('order')
        order_list = []
        for item in items:
            if item.order not in order_list:
                order_list.append(item.order)
        for position in order_list:
            filter_list = []
            filter_list = [item for item in items if item.order == position]
            filter_list.sort(key=attrgetter('online_time'), reverse=True)
            item = None
            now = datetime.now()
            for obj in filter_list:
                if now > obj.online_time:
                    item = obj
                    break
            if not item:
                item = filter_list[0]
            dic = item.item.content_dict()
            dic['order'] = item.order
            obj_list.append(dic)
        return obj_list

    def content_dict(self):
        result_dict = super(iPhone_Category, self).content_dict()
        result_dict['items'] = self.get_items()
        return result_dict

    class Meta:
        verbose_name = u'iPhone Category'
        verbose_name_plural = u'iPhone Category'
        app_label = 'content'

    def save(self, *args, **kwargs):
        super(iPhone_Category, self).save(*args, **kwargs)


class iPhone_Novel(Novel):

    item = models.ManyToManyField(
        iPhone_Item, through='iPhone_novel_item_ship')
    packageset = models.ForeignKey(iPhone_PackageSet)
    sourceset = models.ForeignKey(iPhone_SourceSet)
    platform = models.CharField(max_length=100, default=DEFAULT_PALTFORM)

    def get_items(self):
        obj_list = []
        items = iPhone_novel_item_ship.objects.filter(
            novel__id=self.id).order_by('order')
        order_list = []
        for item in items:
            if item.order not in order_list:
                order_list.append(item.order)
        for position in order_list:
            filter_list = []
            filter_list = [item for item in items if item.order == position]
            filter_list.sort(key=attrgetter('online_time'), reverse=True)
            item = None
            now = datetime.now()
            for obj in filter_list:
                if now > obj.online_time:
                    item = obj
                    break
            if not item:
                item = filter_list[0]
            dic = item.item.content_dict()
            dic['order'] = item.order
            obj_list.append(dic)
        return obj_list

    def content_dict(self):
        result_dict = super(iPhone_Novel, self).content_dict()
        result_dict['items'] = self.get_items()
        result_dict['packages'] = self.packageset.content_dict()['packages']
        result_dict['sources'] = self.sourceset.content_dict()['sources']
        result_dict['platform'] = self.platform
        return result_dict

    class Meta:
        verbose_name = u'iPhone Novel'
        verbose_name_plural = u'iPhone Novel'
        app_label = 'content'

    def save(self, *args, **kwargs):
        super(iPhone_Novel, self).save(*args, **kwargs)


class iPhone_Group(Group):

    category = models.ManyToManyField(
        iPhone_Category, through='iPhone_group_category_ship')

    def get_categorys(self):
        obj_list = []
        items = iPhone_group_category_ship.objects.filter(
            group__id=self.id).order_by('order')
        for item in items:
            dic = item.category.content_dict()
            dic['order'] = item.order
            obj_list.append(dic)
        return obj_list

    def content_dict(self):
        result_dict = super(iPhone_Group, self).content_dict()
        result_dict['cats'] = self.get_categorys()
        return result_dict

    class Meta:
        verbose_name = u'iPhone Group'
        verbose_name_plural = u'iPhone Group'
        app_label = 'content'

    def save(self, *args, **kwargs):
        super(iPhone_Group, self).save(*args, **kwargs)


class iPhone_Section(Section):
    LAYOUT_CHOICES = (
        (u'1', u'搜索'),
        (u'2', u'新闻资讯'),
        (u'3', u'手机酷站'),
        (u'4', u'热门应用'),
        (u'5', u'热门游戏'),
        (u'6', u'特价购物'),
        (u'7', u'免费小说'),
    )
    layout = models.CharField(
        max_length=100, choices=LAYOUT_CHOICES, default='搜索')
    platform = models.CharField(max_length=100, default=DEFAULT_PALTFORM)
    packageset = models.ForeignKey(iPhone_PackageSet)
    sourceset = models.ForeignKey(iPhone_SourceSet)
    group = models.ManyToManyField(
        iPhone_Group, through='iPhone_section_group_ship')

    def get_groups(self):
        obj_list = []
        items = iPhone_section_group_ship.objects.filter(
            section__id=self.id).order_by('order')
        for item in items:
            dic = item.group.content_dict()
            dic['order'] = item.order
            obj_list.append(dic)
        return obj_list

    def content_dict(self):
        result_dict = super(iPhone_Section, self).content_dict()
        result_dict['platform'] = self.platform
        result_dict['packages'] = self.packageset.content_dict()['packages']
        result_dict['sources'] = self.sourceset.content_dict()['sources']
        result_dict['groups'] = self.get_groups()
        return result_dict

    class Meta:
        verbose_name = u'iPhone Section'
        verbose_name_plural = u'iPhone Section'
        app_label = 'content'

    def save(self, *args, **kwargs):
        super(iPhone_Section, self).save(*args, **kwargs)


class iPhone_section_group_ship(models.Model):
    section = models.ForeignKey(iPhone_Section)
    group = models.ForeignKey(iPhone_Group)
    order = models.IntegerField()

    def __unicode__(self):
        return u"%s(%s)" % (self.section.title, self.group.name)

    class Meta:
        verbose_name = u"iPhone Section所关联的Group"
        verbose_name_plural = u"iPhone Section所关联的Group"
        app_label = 'content'


class iPhone_group_category_ship(models.Model):
    group = models.ForeignKey(iPhone_Group)
    category = models.ForeignKey(iPhone_Category)
    order = models.IntegerField()

    def __unicode__(self):
        return u"%s(%s)" % (self.group.name, self.category.name)

    class Meta:
        verbose_name = u"iPhone Group所关联的Category"
        verbose_name_plural = u"iPhone Group所关联的Category"
        app_label = 'content'


class iPhone_category_item_ship(models.Model):
    category = models.ForeignKey(iPhone_Category)
    item = models.ForeignKey(iPhone_Item)
    order = models.IntegerField()
    online_time = models.DateTimeField(default=datetime.now)

    def __unicode__(self):
        return u"%s(%s)" % (self.category.name, self.item.title)

    class Meta:
        verbose_name = u"iPhone Category所关联的Item"
        verbose_name_plural = u"iPhone Category所关联的Item"
        app_label = 'content'


class iPhone_novel_item_ship(models.Model):
    novel = models.ForeignKey(iPhone_Novel)
    item = models.ForeignKey(iPhone_Item)
    order = models.IntegerField()
    online_time = models.DateTimeField(default=datetime.now)

    def __unicode__(self):
        return u"%s(%s)" % (self.category.name, self.item.title)

    class Meta:
        verbose_name = u"iPhone Novel所关联的Item"
        verbose_name_plural = u"iPhone Novel所关联的Item"
        app_label = 'content'


class iPhone_section_group_ship_inline(EnhancedAdminInline):
    model = iPhone_section_group_ship
    extra = 1


class iPhone_group_category_ship_inline(EnhancedAdminInline):
    model = iPhone_group_category_ship
    extra = 1


class iPhone_category_item_ship_inline(EnhancedAdminInline):
    model = iPhone_category_item_ship
    extra = 1


class iPhone_novel_item_ship_inline(EnhancedAdminInline):
    model = iPhone_novel_item_ship
    extra = 1

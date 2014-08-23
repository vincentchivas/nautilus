# -*- coding:utf-8 -*-
'''
Copyright (c) 2012 Baina Info Inc. All rights reserved.
@Author : Jun Wang
@Date : 2012-2-13
'''
import logging
from django.db import models
from operator import attrgetter
from dolphinopadmin.base.admin import EnhancedAdminInline
from datetime import datetime
from content_base import *


DEFAULT_PALTFORM = 'Android_CN'

logger = logging.getLogger("dolphinopadmin.admin")


class Android_PackageSet(PackageSet):
#    package = models.ManyToManyField(Android_Package,through='Android_set_package_ship')

    def get_packages(self):
        obj_list = []
        packages = Android_Package.objects.filter(packageset__id=self.id)
        for item in packages:
            temp = item.content_dict()['packagename']
            obj_list.append(temp)
        return obj_list

    def content_dict(self):
        result_dict = super(Android_PackageSet, self).content_dict()
        result_dict['packages'] = self.get_packages()
        return result_dict

    class Meta:
        verbose_name = u'Android Package Set'
        verbose_name_plural = u'Android Package Set'
        app_label = 'content'

    def save(self, *args, **kwargs):
        super(Android_PackageSet, self).save(*args, **kwargs)


class Android_Package(Package):
    packageset = models.ForeignKey(Android_PackageSet)

    def content_dict(self):
        result_dict = super(Android_Package, self).content_dict()
        return result_dict

    class Meta:
        verbose_name = u'Android Package'
        verbose_name_plural = u'Android Package'
        app_label = 'content'

    def save(self, *args, **kwargs):
        super(Android_Package, self).save(*args, **kwargs)


class Android_SourceSet(SourceSet):

    def content_dict(self):
        result_dict = super(Android_SourceSet, self).content_dict()
        result_dict['sources'] = self.get_source(Android_Source)
        return result_dict

    class Meta:
        verbose_name = u'Android Source Set'
        verbose_name_plural = u'Android Source Set'
        app_label = 'content'

    def save(self, *args, **kwargs):
        super(Android_SourceSet, self).save(*args, **kwargs)


class Android_Source(Source):
    sourceset = models.ForeignKey(Android_SourceSet)

    def content_dict(self):
        result_dict = super(Android_Source, self).content_dict()
        return result_dict

    class Meta:
        verbose_name = u'Android Source'
        verbose_name_plural = u'Android Source'
        app_label = 'content'

    def save(self, *args, **kwargs):
        super(Android_Source, self).save(*args, **kwargs)


class Android_Item(Item):

    def content_dict(self):
        result_dict = super(Android_Item, self).content_dict()
        return result_dict

    class Meta:
        verbose_name = u'Android Item'
        verbose_name_plural = u'Android Item'
        app_label = 'content'

    def save(self, *args, **kwargs):
        super(Android_Item, self).save(*args, **kwargs)


class Android_Category(Category):

    item = models.ManyToManyField(
        Android_Item, through='Android_category_item_ship')

    def get_items(self):
        obj_list = []
        items = Android_category_item_ship.objects.filter(
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
        result_dict = super(Android_Category, self).content_dict()
        result_dict['items'] = self.get_items()
        return result_dict

    class Meta:
        verbose_name = u'Android Category'
        verbose_name_plural = u'Android Category'
        app_label = 'content'

    def save(self, *args, **kwargs):
        super(Android_Category, self).save(*args, **kwargs)


class Android_Novel(Novel):

    item = models.ManyToManyField(
        Android_Item, through='Android_novel_item_ship')
    packageset = models.ForeignKey(Android_PackageSet)
    sourceset = models.ForeignKey(Android_SourceSet)
    platform = models.CharField(max_length=100, default=DEFAULT_PALTFORM)

    def get_items(self):
        obj_list = []
        items = Android_novel_item_ship.objects.filter(
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
        result_dict = super(Android_Novel, self).content_dict()
        result_dict['items'] = self.get_items()
        result_dict['packages'] = self.packageset.content_dict()['packages']
        result_dict['sources'] = self.sourceset.content_dict()['sources']
        result_dict['platform'] = self.platform
        return result_dict

    class Meta:
        verbose_name = u'Android Novel'
        verbose_name_plural = u'Android Novel'
        app_label = 'content'

    def save(self, *args, **kwargs):
        super(Android_Novel, self).save(*args, **kwargs)


class Android_Group(Group):

    category = models.ManyToManyField(
        Android_Category, through='Android_group_category_ship')
    items = models.ManyToManyField(
        Android_Item, through='Android_group_item_ship')

    def get_categorys(self):
        obj_list = []
        items = Android_group_category_ship.objects.filter(
            group__id=self.id).order_by('order')
        for item in items:
            dic = item.category.content_dict()
            dic['order'] = item.order
            obj_list.append(dic)
        return obj_list

    def get_items(self):
        obj_list = []
        items = Android_group_item_ship.objects.filter(
            group__id=self.id).order_by('order')
        for item in items:
            dic = item.item.content_dict()
            dic['order'] = item.order
            obj_list.append(dic)
        return obj_list

    def content_dict(self):
        result_dict = super(Android_Group, self).content_dict()
        result_dict['cats'] = self.get_categorys()
        items = self.get_items()
        if items:
            result_dict['items'] = items
        return result_dict

    class Meta:
        verbose_name = u'Android Group'
        verbose_name_plural = u'Android Group'
        app_label = 'content'

    def save(self, *args, **kwargs):
        super(Android_Group, self).save(*args, **kwargs)


class Android_Section(Section):
    LAYOUT_CHOICES = (
        (u'1', u'搜索'),
        (u'2', u'新闻资讯'),
        (u'3', u'手机酷站'),
        (u'4', u'安卓应用'),
        (u'5', u'安卓游戏'),
        (u'6', u'特价购物'),
        (u'7', u'免费小说'),
        (u'8', u'手机酷站(低配版)'),
        (u'9', u'应用游戏(低配版)'),
        (u'10', u'小说影音(低配版)'),
        (u'11', u'生活购物(低配版)'),
        (u'12', u'娱乐搞笑(低配版)'),
    )
    layout = models.CharField(
        max_length=100, choices=LAYOUT_CHOICES, default='搜索')
    platform = models.CharField(max_length=100, default=DEFAULT_PALTFORM)
    packageset = models.ForeignKey(Android_PackageSet)
    sourceset = models.ForeignKey(Android_SourceSet)
    group = models.ManyToManyField(
        Android_Group, through='Android_section_group_ship')

    def get_groups(self):
        obj_list = []
        items = Android_section_group_ship.objects.filter(
            section__id=self.id).order_by('order')
        for item in items:
            dic = item.group.content_dict()
            dic['order'] = item.order
            obj_list.append(dic)
        return obj_list

    def content_dict(self):
        result_dict = super(Android_Section, self).content_dict()
        result_dict['platform'] = self.platform
        result_dict['packages'] = self.packageset.content_dict()['packages']
        result_dict['sources'] = self.sourceset.content_dict()['sources']
        result_dict['groups'] = self.get_groups()
        return result_dict

    class Meta:
        verbose_name = u'Android Section'
        verbose_name_plural = u'Android Section'
        app_label = 'content'

    def save(self, *args, **kwargs):
        super(Android_Section, self).save(*args, **kwargs)


class Android_section_group_ship(models.Model):
    section = models.ForeignKey(Android_Section)
    group = models.ForeignKey(Android_Group)
    order = models.IntegerField()

    def __unicode__(self):
        return u"%s(%s)" % (self.section.title, self.group.name)

    class Meta:
        verbose_name = u"Android Section所关联的Group"
        verbose_name_plural = u"Android Section所关联的Group"
        app_label = 'content'


class Android_group_category_ship(models.Model):
    group = models.ForeignKey(Android_Group)
    category = models.ForeignKey(Android_Category)
    order = models.IntegerField()

    def __unicode__(self):
        return u"%s(%s)" % (self.group.name, self.category.name)

    class Meta:
        verbose_name = u"Android Group所关联的Category"
        verbose_name_plural = u"Android Group所关联的Category"
        app_label = 'content'


class Android_group_item_ship(models.Model):
    group = models.ForeignKey(Android_Group)
    item = models.ForeignKey(Android_Item)
    order = models.IntegerField()

    def __unicode__(self):
        return u"%s(%s)" % (self.group.name, self.item.title)

    class Meta:
        verbose_name = u"Android Group所关联的Item"
        verbose_name_plural = u"Android Group所关联的Item"
        app_label = 'content'


class Android_category_item_ship(models.Model):
    category = models.ForeignKey(Android_Category)
    item = models.ForeignKey(Android_Item)
    order = models.IntegerField()
    online_time = models.DateTimeField(default=datetime.now)

    def __unicode__(self):
        return u"%s(%s)" % (self.category.name, self.item.title)

    class Meta:
        verbose_name = u"Android Category所关联的Item"
        verbose_name_plural = u"Android Category所关联的Item"
        app_label = 'content'


class Android_novel_item_ship(models.Model):
    novel = models.ForeignKey(Android_Novel)
    item = models.ForeignKey(Android_Item)
    order = models.IntegerField()
    online_time = models.DateTimeField(default=datetime.now)

    def __unicode__(self):
        return u"%s(%s)" % (self.novel.name, self.item.title)

    class Meta:
        verbose_name = u"Android Novel所关联的Item"
        verbose_name_plural = u"Android Novel所关联的Item"
        app_label = 'content'


class Android_section_group_ship_inline(EnhancedAdminInline):
    model = Android_section_group_ship
    extra = 1


class Android_group_category_ship_inline(EnhancedAdminInline):
    model = Android_group_category_ship
    extra = 1


class Android_group_item_ship_inline(EnhancedAdminInline):
    model = Android_group_item_ship
    extra = 1


class Android_category_item_ship_inline(EnhancedAdminInline):
    model = Android_category_item_ship
    extra = 1


class Android_novel_item_ship_inline(EnhancedAdminInline):
    model = Android_novel_item_ship
    extra = 1

# -*- coding:utf-8 -*-
'''
Copyright (c) 2011 Baina Info Inc. All rights reserved.
@Author : Wenyuan Wu
@Date : 2011-11-28
'''
import datetime
import time
from django.contrib import admin
from django.db import models


class Ad(models.Model):

    sponsor = models.CharField(max_length=50, verbose_name=u'广告商')
    image_url = models.CharField(max_length=200, verbose_name=u'图片地址')
    click_url = models.URLField(verify_exists=False, verbose_name=u'目标地址')

    def __unicode__(self):
        return self.sponsor

    def content_info(self):
        ad = {
            'sponsor': self.sponsor,
            'image_url': self.image_url,
            'click_url': self.click_url,
        }
        return ad

    class Meta:
        verbose_name = u'广告'
        verbose_name_plural = u'广告'


class FeatureSite(models.Model):

    name = models.CharField(max_length=40, verbose_name=u'Feature站点名')
    logo_url = models.CharField(max_length=200, verbose_name=u'图片地址')
    click_url = models.URLField(verify_exists=False, verbose_name=u'目标地址')

    def __unicode__(self):
        return self.name

    def content_info(self):
        feature_site = {
            'name': self.name,
            'logo_url': self.logo_url,
            'click_url': self.click_url,
        }
        return feature_site

    class Meta:
        verbose_name = u'Feature站点'
        verbose_name_plural = u'Feature站点'


class Site(models.Model):

    name = models.CharField(max_length=40, verbose_name=u'站点名')
    click_url = models.URLField(verify_exists=False, verbose_name=u'目标地址')

    def __unicode__(self):
        return self.name

    def content_info(self):
        site = {
            'name': self.name,
            'click_url': self.click_url,
        }
        return site

    class Meta:
        verbose_name = u'站点'
        verbose_name_plural = u'站点'


class Category(models.Model):

    name = models.CharField(max_length=20, verbose_name=u'分类名')
    sites = models.ManyToManyField(Site, verbose_name=u'站点',
                                   through='CategorySiteShip')

    def __unicode__(self):
        return self.name

    def get_sites(self):
        sites_list = []
        sites = CategorySiteShip.objects.filter(category__id=self.id)
        for item in sites:
            temp = item.site.content_info()
            temp['order'] = item.order
            sites_list.append(temp)
        sites_list = sorted(sites_list, key=lambda x: x['order'])
        return sites_list

    def content_info(self):
        category = {
            'name': self.name,
            'sites': self.get_sites(),
        }
        return category

    class Meta:
        verbose_name = u'站点分类'
        verbose_name_plural = u'站点分类'


class Promotion(models.Model):

    title = models.CharField(max_length=50, verbose_name=u'标题')
    image_url = models.CharField(max_length=200, verbose_name=u'图标地址')
    click_url = models.URLField(verify_exists=False, verbose_name=u'目标地址')
    description = models.TextField(max_length=512, verbose_name=u'描述')

    def __unicode__(self):
        return self.title

    def content_info(self):
        promotion = {
            'title': self.title,
            'image_url': self.image_url,
            'click_url': self.click_url,
            'description': self.description,
        }
        return promotion

    class Meta:
        verbose_name = u'推广'
        verbose_name_plural = u'推广'


class Navigation(models.Model):

    LOCAL_CHOICES = (
        (u'zh_CN', u'zh_CN'),
        (u'en_US', u'en_US'),
        (u'unknown', u'unknown'),
    )

    OS_CHOICES = (
        (u'Android', u'Android'),
        (u'iPad', u'iPad'),
        (u'iPhone', u'iPhone'),
        (u'unknown', u'unknown'),
    )

    os = models.CharField(max_length=20, verbose_name=u'OS',
                          choices=OS_CHOICES)
    local = models.CharField(max_length=10, verbose_name=u'LOCALE',
                             choices=LOCAL_CHOICES)
    name = models.CharField(max_length=50, verbose_name=u'NAME', unique=True)
    ads = models.ManyToManyField(Ad, verbose_name=u'广告', through='AdShip')
    feature_sites = models.ManyToManyField(FeatureSite,
                                           verbose_name=u'Feature站点', through='FeatureSiteShip')
    categories = models.ManyToManyField(Category, verbose_name=u'站点分类',
                                        through='CategoryShip')
    promotion = models.ManyToManyField(Promotion, verbose_name=u'推广',
                                       through='PromotionShip')

    def __unicode__(self):
        return u'%s站点导航' % self.os

    def get_field_list(self, model_cls, field_name):
        field_list = []
        items = model_cls.objects.filter(navigation__id=self.id)
        for item in items:
            temp = getattr(item, field_name).content_info()
            temp['order'] = item.order
            field_list.append(temp)
        field_list = sorted(field_list, key=lambda x: x['order'])
        return field_list

    def content_dict(self):
        navigation = {
            'os': self.os,
            'local': self.local,
            'name': self.name,
            'timestamp': time.mktime(datetime.datetime.utcnow().timetuple()),
            'ads': self.get_field_list(AdShip, 'ad'),
            'feature_sites': self.get_field_list(FeatureSiteShip, 'feature_site'),
            'categories': self.get_field_list(CategoryShip, 'category'),
            'promotions': self.get_field_list(PromotionShip, 'promotion'),
        }
        return navigation

    class Meta:
        verbose_name = u'站点导航'
        verbose_name_plural = u'站点导航'


class AdShip(models.Model):
    ad = models.ForeignKey(Ad, verbose_name=u'广告')
    navigation = models.ForeignKey(Navigation, verbose_name=u'站点导航')
    order = models.IntegerField(verbose_name=u'此广告在站点导航中的顺序', unique=True)

    def __unicode__(self):
        return u"%s(%s)" % (self.ad.sponsor, self.ad.click_url)

    class Meta:
        verbose_name = u'站点导航所关联的广告'
        verbose_name_plural = u'站点导航所关联的广告'


class FeatureSiteShip(models.Model):
    feature_site = models.ForeignKey(FeatureSite, verbose_name=u'Feature站点')
    navigation = models.ForeignKey(Navigation, verbose_name=u'站点导航')
    order = models.IntegerField(
        verbose_name=u'此Feature站点在站点导航中的顺序', unique=True)

    def __unicode__(self):
        return u"%s(%s)" % (self.feature_site.name,
                           self.feature_site.click_url)

    class Meta:
        verbose_name = u'站点导航所关联的Feature Site'
        verbose_name_plural = u'站点导航所关联的Feature Site'


class CategoryShip(models.Model):
    category = models.ForeignKey(Category, verbose_name=u'分类')
    navigation = models.ForeignKey(Navigation, verbose_name=u'站点导航')
    order = models.IntegerField(
        verbose_name=u'此分类在站点导航中的顺序', unique=True)

    def __unicode__(self):
        return u"%s" % (self.category.name)

    class Meta:
        verbose_name = u'站点导航所关联的分类'
        verbose_name_plural = u'站点导航所关联的分类'


class PromotionShip(models.Model):
    promotion = models.ForeignKey(Promotion, verbose_name=u'推广')
    navigation = models.ForeignKey(Navigation, verbose_name=u'站点导航')
    order = models.IntegerField(
        verbose_name=u'此推广在站点导航中的顺序', unique=True)

    def __unicode__(self):
        return u"%s(%s)" % (self.promotion.title, self.promotion.click_url)

    class Meta:
        verbose_name = u'站点导航所关联的推广'
        verbose_name_plural = u'站点导航所关联的推广'


class CategorySiteShip(models.Model):
    category = models.ForeignKey(Category, verbose_name=u'分类')
    site = models.ForeignKey(Site, verbose_name=u'站点')
    order = models.IntegerField(verbose_name=u'此站点在分类中的顺序')

    def __unicode__(self):
        return u"%s(%s)" % (self.site.name, self.site.click_url)

    class Meta:
        verbose_name = u'站点分类所关联的站点'
        verbose_name_plural = u'站点分类所关联的站点'


class CategorySiteShipInline(admin.TabularInline):
    model = CategorySiteShip
    extra = 1


class AdShipInline(admin.TabularInline):
    model = AdShip
    extra = 1


class FeatureSiteShipInline(admin.TabularInline):
    model = FeatureSiteShip
    extra = 1


class CategoryShipInline(admin.TabularInline):
    model = CategoryShip
    extra = 1


class PromotionShipInline(admin.TabularInline):
    model = PromotionShip
    extra = 1

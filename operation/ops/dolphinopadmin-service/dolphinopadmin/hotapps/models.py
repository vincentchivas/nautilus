#!/usr/bin/python
# -*- coding: utf-8 -*-
# Refactored by qtgan
# Date: 2014/3/13
from datetime import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _

from dolphinopadmin.configure.models import Rule
from dolphinopadmin.resource.models import Icon
from dolphinopadmin.base.base_model import BaseStatus
from dolphinopadmin.base.content import HOTAPPS_PLATFORMS
# from dolphinopadmin.utils import string_with_title

BOOLEAN_CHOICES = (
    (1, u'yes'),
    (0, u'no'),
)

FEATURE_TYPE_CHOICES = (
    (u'App', u'App'),
    (u'Category', u'Category'),
)

class HotAppbase():
    """docstring for HotAppbase"""
    def application_title(this):
        if this.application:
            return this.application.title
        else:
            return None

    def category_title(this):
        if this.category:
            return this.category.category_name
        else:
            return None
    class Meta:
        abstract = True

class Category(BaseStatus):
    category_name = models.CharField(max_length=50, verbose_name=_("Category Name"))
    third_party_url = models.URLField(blank=True, verify_exists=False, verbose_name=_("Third Party URL"),
                                      help_text=_('Please icon URL exist!!'))
    is_third_part = models.IntegerField(choices=BOOLEAN_CHOICES, default=0, verbose_name=_("Whether Is Third Part"))
    icon = models.URLField(verify_exists=False, verbose_name=_("Icon"), help_text=_("url of the icon"))
    #icon = models.FileField(blank=True,upload_to = '/var/app/dolphinopadmin')
    brief_description = models.TextField(blank=True, max_length=256, verbose_name=_("Brief Description"))
    detail_description = models.TextField(blank=True, max_length=2048, verbose_name=_("Detail Description"))
    # order = models.BigIntegerField(verbose_name=_("Order"))      #origin order field
    platform = models.CharField(max_length=100, editable=False)
    order = models.IntegerField(blank=True, verbose_name=_("Order"))
    # platformfilter = models.CharField(max_length=100, editable=False)
    def content_dict(self, server, is_del=False):
        _sync_key = {
           "id": self.id,
           "platform": self.platform,
        }

        if is_del:
            return _sync_key
        result_dict = {
            "category_name": self.category_name,
            "icon": self.icon,
            "short_description": self.brief_description,
            "detail_description": self.detail_description,
            "order": self.order,
            "is_third_part": self.is_third_part,
            "third_party_url": self.third_party_url,
        }
        result_dict.update(_sync_key)
        return result_dict

    def __unicode__(self):
        return self.category_name

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Category')
        app_label = 'hotapps'

    def save(self, *args, **kwargs):
        if not self.id:
            self.platform = self.__class__.filters["platform"]
        super(Category, self).save(*args, **kwargs)


class ScreenShot(models.Model):
    pic_url = models.URLField(verify_exists=False, verbose_name=_("Picture URL"))
    title = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("Title"))
    platform = models.CharField(max_length=20, editable=False)
    # platformfilter = models.CharField(max_length=100, editable=False)

    def content_dict(self):
        result_dict = {
            "pic_url": self.pic_url,
            "title": self.title,
            "platform": self.platform
        }
        return result_dict

    def __unicode__(self):
        return "%s" % (self.title or self.pic_url[-16:])

    def save(self, *args, **kwargs):
        self.platform = self.__class__.filters["platform"]
        super(ScreenShot, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('ScreenShot')
        verbose_name_plural = _('ScreenShot')
        app_label = 'hotapps'


class Application(BaseStatus, HotAppbase):
    TYPE_CHOICES = (
        (u'App', u'App'),
        (u'Game', u'Game'),
    )

    PRICE_CHOICES = (
        (u'Free', u'Free'),
        (u'Limit', u'Limit'),
        (u'Charge', u'Charge'),
        (U'Discount', u'Discount'),
    )

    APP_RATE_CHOICES = (
        (3.0, u'3.0'),
        (3.5, u'3.5'),
        (4.0, u'4.0'),
        (4.5, u'4.5'),
        (5.0, u'5.0'),
    )

    title = models.CharField(max_length=50, verbose_name=_("Title"))
    icon = models.URLField(verify_exists=False, verbose_name=_("Icon"))
    #icon = models.FileField(blank=True,upload_to = '/var/app/dolphinopadmin')
    # order = models.BigIntegerField(verbose_name=_("Order"))
    is_new = models.IntegerField(default=0, choices=BOOLEAN_CHOICES, verbose_name=_("Is New?"))
    download_url = models.CharField(max_length=200, verbose_name=_("Download URL"))
    app_updatetime = models.DateTimeField(
        blank=True, default=datetime.utcnow(), verbose_name=_("Update Time"))
    app_version = models.CharField(blank=True, max_length=20, verbose_name=_("App Version"), help_text=_("Application Version"))
    app_developer = models.CharField(blank=True, max_length=100, verbose_name=_("App Developer"))
    app_rating = models.FloatField(
        blank=True, default=3.0, choices=APP_RATE_CHOICES, verbose_name=_("App Rate"))
    short_description = models.TextField(max_length=256, verbose_name=_("Brief Description"))
    detail_description = models.TextField(blank=True, max_length=1024, verbose_name=_("Detail Description"))
    app_size = models.CharField(blank=True, max_length=10, verbose_name=_("App Size"))
    app_type = models.CharField(
        max_length=20, default='App', choices=TYPE_CHOICES, verbose_name=_("App Type"))
    price = models.CharField(max_length=50, blank=True, default='0.0', verbose_name=_("Price"))
    original_price = models.CharField(max_length=50, blank=True, default='0.0', verbose_name=_("Origin Price"))
    favourable_price = models.CharField(
        max_length=50, blank=True, default='0.0', verbose_name=_("Favourable Price"))
    price_type = models.CharField(
        max_length=20, blank=True, choices=PRICE_CHOICES, verbose_name=_("Price Type"))
    price_limit_time = models.DateTimeField(
        blank=True, default=datetime.utcnow(), verbose_name=_("Price Limit Time"))
    is_third_part = models.IntegerField(default=0, verbose_name=_("Is Third Part?"))
    api_url = models.URLField(verify_exists=False, null=True, blank=True, verbose_name=_("API URL"),
                              help_text='The URL of the Third-part API!!')
    platform = models.CharField(max_length=100, editable=False)

    order = models.IntegerField(blank=True, verbose_name=_("Order"))
    category = models.ForeignKey(Category, verbose_name=_("Category"))

    def content_dict(self, server, is_del=False):
        _sync_key = {
           "id": self.id,
           "platform": self.platform,
        }

        if is_del:
            return _sync_key
        result_dict = {
            "title": self.title,
            "category": self.category.id,
            "screenshots": self.get_screenshots(),
            "icon": self.icon,
            "order": self.order,
            "download_url": self.download_url,
            "is_new": self.is_new,
            "app_updatetime": self.app_updatetime,
            "app_version": self.app_version,
            "app_developer": self.app_developer,
            "app_rating": self.app_rating,
            "short_description": self.short_description,
            "detail_description": self.detail_description,
            "app_size": self.app_size,
            "app_type": self.app_type,
            "price": self.price,
            "original_price": self.original_price,
            "favourable_price": self.favourable_price,
            "price_type": self.price_type,
            "price_limit_time": self.price_limit_time,
            "is_third_part": self.is_third_part,
            "api_url": self.api_url,
            "show_details": 0
        }
        result_dict.update(_sync_key)
        return result_dict

    def __unicode__(self):
        return self.title

    def get_screenshots(self):
        _list = []
        '''apps = AppPicShip.objects.filter(app__id=self.id)'''
        apps = self.hotapps_applicationscreenshotship_set.all().order_by("order")
        for item in apps:
            temp = item.screenshot.content_dict()
            temp["order"] = item.order
            _list.append(temp)
        return _list

    def save(self, *args, **kwargs):
        if not self.id:
            self.platform = self.__class__.filters["platform"]
        super(Application, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('Application')
        verbose_name_plural = _('Application')
        app_label = 'hotapps'


class Feature(BaseStatus, HotAppbase):
    feature_type = models.CharField(
        max_length=20, default='App', choices=FEATURE_TYPE_CHOICES, verbose_name=_("Feature Type"))
    # order = models.BigIntegerField(verbose_name=_("Order"))
    feature_on_top = models.IntegerField(default=0, choices=BOOLEAN_CHOICES, verbose_name=_("Feature On Top"))
    top_feature_pic = models.URLField(
        verify_exists=False, null=True, blank=True, verbose_name=_("Top Feature Picture"),
        help_text='The URL of the Pic on the feature top !!')
    small_pic = models.URLField(verify_exists=False, null=True, blank=True, verbose_name=_("Small Picture"))
    #picture_order = models.IntegerField(default=get_fea_pic_order, help_text='Order in the feature picture list!!')
    is_third_part = models.IntegerField(choices=BOOLEAN_CHOICES, default=0, verbose_name=_("Is Third Part?"))
    third_part_url = models.URLField(
        verify_exists=False, null=True, blank=True, verbose_name=_("Third Part URL"),
        help_text='URL of the feature top pic links to')
    platform = models.CharField(max_length=20, editable=False)
    order = models.IntegerField(blank=True, verbose_name=_("Order"))
    application = models.ForeignKey(Application, verbose_name=_("Application"))
    category = models.ForeignKey(Category, null=True, verbose_name=_("Category"))


    def content_dict(self, server, is_del=False):
        _sync_key = {
           "id": self.id,
           "platform": self.platform,
        }

        if is_del:
            return _sync_key
        result_dict = {
            "feature_type": self.feature_type,
            "order": self.order,
            "feature_on_top": self.feature_on_top,
            "top_feature_pic": self.top_feature_pic,
            "small_pic": self.small_pic,
            "is_third_part": self.is_third_part,
            "third_part_url": self.third_part_url,
        }
        result_dict.update(_sync_key)
        if self.feature_type == 'App':
            result_dict['content'] = self.application.content_dict(server)
        else:
            if not self.feature_on_top:
                raise ValueError(_('feature type is category feature on top must be true!'))

            result_dict['content'] = '%s %s' % (str(self.category.id),
                                                self.category.category_name)
        return result_dict

    def __unicode__(self):
        if self.feature_type == 'App':
            return self.application.title
        elif self.feature_type == "Category":
            return self.category.category_name

    class Meta:
        verbose_name = _('Feature')
        verbose_name_plural = _('Feature')
        app_label = 'hotapps'

    def save(self, *args, **kwargs):
        if not self.id:
            self.platform = self.__class__.filters["platform"]
        super(Feature, self).save(*args, **kwargs)


class Trending(BaseStatus, HotAppbase):
    # order = models.BigIntegerField(verbose_name=_("Order"))
    platform = models.CharField(max_length=100, editable=False)
    order = models.IntegerField(blank=True, verbose_name=_("Order"))
    application = models.ForeignKey(Application, verbose_name=_("Application"))


    def content_dict(self, server, is_del=False):
        _sync_key = {
           "id": self.id,
           "platform": self.platform,
        }

        if is_del:
            return _sync_key
        result_dict = {
            "application": self.application.content_dict(server),
            "order": self.order,
        }
        result_dict.update(_sync_key)
        return result_dict

    def __unicode__(self):
        return self.application.title

    class Meta:
        verbose_name = _('Trending')
        verbose_name_plural = _('Trending')
        app_label = 'hotapps'

    def save(self, *args, **kwargs):
        if not self.id:
            self.platform = self.__class__.filters["platform"]
        super(Trending, self).save(*args, **kwargs)


class Daily(BaseStatus, HotAppbase):
    reason = models.TextField(max_length=100, verbose_name=_("Reason"))
    application = models.ForeignKey(Application, verbose_name=_("Application"))
    platform = models.CharField(max_length=100, editable=False)

    def content_dict(self, server, is_del=False):
        _sync_key = {
           "id": self.id,
           "platform": self.platform,
        }

        if is_del:
            return _sync_key

        result_dict = {
            "reason": self.reason,
            "application": self.application.content_dict(server)
        }
        result_dict.update(_sync_key)
        return result_dict

    def __unicode__(self):
        return self.application.title

    class Meta:
        verbose_name = _('Daily Recommend')
        verbose_name_plural = _('Daily Recommend')
        app_label = 'hotapps'

    def save(self, *args, **kwargs):
        if not self.id:
            self.platform = self.__class__.filters["platform"]
        super(Daily, self).save(*args, **kwargs)


class Ads(BaseStatus, HotAppbase):

    TYPE_CHOICES = (
        (u'App', u'App'),
        (u'Game', u'Game'),
    )

    PRICE_CHOICES = (
        (u'Free', u'Free'),
        (u'Limit', u'Limit'),
        (u'Charge', u'Charge'),
    )

    APP_RATE_CHOICES = (
        (3.0, u'3.0'),
        (3.5, u'3.5'),
        (4.0, u'4.0'),
        (4.5, u'4.5'),
        (5.0, u'5.0'),
    )

    title = models.CharField(max_length=50, verbose_name=_("Title"))
    icon = models.URLField(blank=True, verify_exists=False, verbose_name=_("Icon"))
    #icon = models.FileField(blank=True,upload_to = '/var/app/dolphinopadmin')
    # order = models.BigIntegerField(verbose_name=_("Order"))
    is_new = models.BooleanField(verbose_name=_("Is New?"))
    download_url = models.CharField(max_length=200, verbose_name=_("Download URL"))
    app_updatetime = models.DateTimeField(
        blank=True, default=datetime.utcnow(), verbose_name=_("Update Time"))
    app_version = models.CharField(blank=True, max_length=20, verbose_name=_("App Version"))
    app_developer = models.CharField(blank=True, max_length=100, verbose_name=_("App Developer"))
    app_rating = models.FloatField(
        blank=True, default=3.0, choices=APP_RATE_CHOICES, verbose_name=_("Rate"))
    short_description = models.CharField(blank=True, max_length=256, verbose_name=_("Short Description"))
    detail_description = models.TextField(blank=True, max_length=1024, verbose_name=_("Detail Description"))
    app_size = models.CharField(blank=True, max_length=10, verbose_name=_("App Size"))
    app_type = models.CharField(
        max_length=20, blank=True, choices=TYPE_CHOICES, verbose_name=_("App Type"))
    price = models.FloatField(blank=True, default=0.0, verbose_name=_("Price"))
    original_price = models.FloatField(blank=True, default=0.0, verbose_name=_("Origin Price"))
    favourable_price = models.FloatField(blank=True, default=0.0, verbose_name=_("Favourable Price"))
    price_type = models.CharField(
        max_length=20, blank=True, choices=PRICE_CHOICES, verbose_name=_("Price Type"))
    price_limit_time = models.DateTimeField(
        blank=True, default=datetime.utcnow(), verbose_name=_("Price Limit Time"))
    is_third_part = models.BooleanField(verbose_name=_("Is Third Part"))
    api_url = models.URLField(verify_exists=False, null=True, blank=True,
                              help_text='The URL of the third API!!', verbose_name=_("API URL"))
    platform = models.CharField(max_length=50, editable=False)
    order = models.IntegerField(blank=True, verbose_name=_("Order"))
    category = models.ForeignKey(Category, verbose_name=_("Category"))

    picture_url = models.URLField(verify_exists=False, help_text='The URL of the Picture!!', verbose_name=_("Picture URL"))


    def content_dict(self, server, is_del=False):
        _sync_key = {
           "id": self.id,
           "platform": self.platform,
        }

        if is_del:
            return _sync_key

        result_dict = {
            "title": self.title,
            "category": self.category.id,
            "screenshots": self.get_screenshots(),
            "icon": self.icon,
            "order": self.order,
            "download_url": self.download_url,
            "is_new": self.is_new,
            "app_updatetime": self.app_updatetime,
            "app_version": self.app_version,
            "app_developer": self.app_developer,
            "app_rating": self.app_rating,
            "short_description": self.short_description,
            "detail_description": self.detail_description,
            "app_size": self.app_size,
            "app_type": self.app_type,
            "price": self.price,
            "original_price": self.original_price,
            "favourable_price": self.favourable_price,
            "price_type": self.price_type,
            "price_limit_time": self.price_limit_time,
            "is_third_part": self.is_third_part,
            "api_url": self.api_url,
            "show_details": 0,
            "picture_url": self.picture_url
        }
        result_dict.update(_sync_key)
        return result_dict

    def __unicode__(self):
        return self.title

    def get_screenshots(self):
        _list = []
        #apps = AppPicShip.objects.filter(app__id=self.id)
        apps = self.hotapps_adsscreenshotship_set.all().order_by("order")
        for item in apps:
            temp = item.screenshot.content_dict()
            temp["order"] = item.order
            _list.append(temp)
        return _list

    class Meta:
        verbose_name = _('Advertisement')
        verbose_name_plural = _('Advertisement')
        app_label = 'hotapps'

    def save(self, *args, **kwargs):
        if not self.id:
            self.platform = self.__class__.filters["platform"]
        super(Ads, self).save(*args, **kwargs)

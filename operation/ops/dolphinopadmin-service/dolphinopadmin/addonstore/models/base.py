# -*- coding:utf-8 -*-
from datetime import datetime
from django.db import models
from dolphinopadmin.base.models import BaseOnline
from dolphinopadmin.remotedb.addonstore import config as config_addonstore
from django.conf import settings

config_addonstore(servers=settings.ENV_CONFIGURATION)


BOOLEAN_CHOICES = (
    (1, u'yes'),
    (0, u'no'),
)

FEATURE_TYPE_CHOICES = (
    (u'App', u'App'),
    (u'Subject', u'Subject'),
)


class Category(BaseOnline):

    category_name = models.CharField(max_length=50, verbose_name=u"分类名称")
    icon = models.URLField(verify_exists=False, verbose_name=u"图表链接")
    brief_description = models.TextField(
        blank=True, max_length=256, verbose_name=u"简介")
    detail_description = models.TextField(
        blank=True, max_length=2048, verbose_name=u"详细描述")
    """
    is_upload_dev = models.IntegerField(default=0)
    is_upload_local = models.IntegerField(default=0)
    is_upload_online = models.IntegerField(default=0)
    """
    platform = models.CharField(max_length=20)

    def content_dict(self):
        result_dict = {
            "id": self.id,
            "category_name": self.category_name,
            "icon": self.icon,
            "short_description": self.brief_description,
            "detail_description": self.detail_description,
            "platform": self.platform
        }
        return result_dict

    def __unicode__(self):
        return self.category_name

    class Meta:
        app_label = 'addonstore'
        abstract = True


class Subject(BaseOnline):

    subject_name = models.CharField(max_length=50, verbose_name=u"专题名称")
    icon = models.URLField(verify_exists=False, verbose_name=u"图标链接")
    brief_description = models.TextField(
        blank=True, max_length=256, verbose_name=u"简介")
    detail_description = models.TextField(
        blank=True, max_length=2048, verbose_name=u"详细描述")
    is_hot = models.BooleanField(default=False, verbose_name=u"热门")
    display_update = models.BooleanField(default=True, verbose_name=u"显示更新数量")
    update_number = models.IntegerField(
        blank=True, default=1, verbose_name=u"更新数量")
    """
    is_upload_dev = models.IntegerField(default=0)
    is_upload_local = models.IntegerField(default=0)
    is_upload_online = models.IntegerField(default=0)
    """
    platform = models.CharField(max_length=20)

    def content_dict(self):
        result_dict = {
            "id": self.id,
            "subject_name": self.subject_name,
            "icon": self.icon,
            "short_description": self.brief_description,
            "detail_description": self.detail_description,
            "is_hot": self.is_hot,
            "display_update": self.display_update,
            "update_number": self.update_number,
            "platform": self.platform
        }
        return result_dict

    def __unicode__(self):
        return self.subject_name

    class Meta:
        app_label = 'addonstore'
        abstract = True


class ScreenShot(models.Model):
    pic_url = models.URLField(
        max_length=2000, verify_exists=False, verbose_name=u"大图链接")
    thumbnails = models.URLField(
        max_length=2000, blank=True, verify_exists=False, verbose_name=u"小图链接")
    title = models.CharField(
        max_length=50, null=True, blank=True, verbose_name=u"名称")
    platform = models.CharField(max_length=20)

    def content_dict(self):
        result_dict = {
            "pic_url": self.pic_url,
            "thumbnails": self.thumbnails,
        }
        return result_dict

    def __unicode__(self):
        return "%s" % (self.title or self.pic_url[-16:])

    class Meta:
        app_label = 'addonstore'
        abstract = True


class Application(BaseOnline):

    TYPE_CHOICES = (
        (u'App', u'App'),
        (u'WebApp', u'WebApp'),
    )

    APP_RATE_CHOICES = (
        (3.0, u'3.0'),
        (3.5, u'3.5'),
        (4.0, u'4.0'),
        (4.5, u'4.5'),
        (5.0, u'5.0'),
    )

    title = models.CharField(max_length=200, verbose_name=u"应用名称")
    icon = models.URLField(verify_exists=False, verbose_name=u"小图标链接")
    big_icon = models.URLField(
        verify_exists=False, blank=True, verbose_name=u"大图标链接")
    backup_icon = models.URLField(
        verify_exists=False, blank=True, verbose_name=u"备用图标")
    short_description = models.CharField(max_length=500, verbose_name=u"简介")
    is_new = models.BooleanField(default=False, verbose_name=u"新应用")
    is_hot = models.BooleanField(default=False, verbose_name=u"热门应用")
    download_url = models.CharField(max_length=2000, verbose_name=u"下载地址")
    last_modified = models.DateTimeField(auto_now=True, verbose_name=u"最后更新时间")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u"创建时间")
    app_publishtime = models.DateTimeField(
        blank=True, default=datetime.now, verbose_name=u"发布时间")
    app_update_status = models.BooleanField(
        default=False, verbose_name=u"应用更新状态")
    app_updatetime = models.DateTimeField(
        blank=True, default=datetime.now, verbose_name=u"应用更新时间")
    app_version = models.CharField(
        blank=True, max_length=100, verbose_name=u"应用版本")
    app_developer = models.CharField(
        blank=True, max_length=100, verbose_name=u"应用开发者")
    app_size = models.CharField(
        blank=True, max_length=50, verbose_name=u"应用大小")
    app_type = models.CharField(
        max_length=20, default='App', choices=TYPE_CHOICES, verbose_name=u"应用类型")
    app_rating = models.FloatField(
        blank=True, default=3.0, verbose_name=u"应用评分")
    app_ratingcount = models.IntegerField(
        blank=True, default=0, verbose_name=u"应用评分人数")
    detail_description = models.TextField(
        blank=True, max_length=10240, verbose_name=u"应用详情")
    price = models.CharField(
        max_length=50, blank=True, default='0.0', verbose_name=u"价格")
    platform = models.CharField(max_length=50)
    """
    is_upload_dev = models.IntegerField(default=0)
    is_upload_local = models.IntegerField(default=0)
    is_upload_online = models.IntegerField(default=0)
    """

    def content_dict(self):
        result_dict = {
            "id": self.id,
            "title": self.title,
            "icon": self.icon,
            "big_icon": self.big_icon,
            "backup_icon": self.backup_icon,
            "short_description": self.short_description,
            "is_new": self.is_new,
            "is_hot": self.is_hot,
            "download_url": self.download_url,
            "create_time": self.create_time,
            "app_publishtime": self.app_publishtime.strftime("%Y-%m-%d"),
            "app_update_status": self.app_update_status,
            "app_updatetime": self.app_updatetime.strftime("%Y-%m-%d"),
            "app_version": self.app_version,
            "app_developer": self.app_developer,
            "app_size": self.app_size,
            "app_type": self.app_type,
            "app_rating": self.app_rating,
            "app_ratingcount": self.app_ratingcount,
            "detail_description": self.detail_description,
            "price": self.price,
            "platform": self.platform
        }
        return result_dict

    def __unicode__(self):
        return self.title

    class Meta:
        app_label = 'addonstore'
        abstract = True


class Feature(BaseOnline):

    FEATURE_TYPE_CHOICES = (
        (u'App', u'App'),
        (u'Subject', u'Subject'),
    )

    description = models.CharField(
        max_length=200, blank=True, verbose_name=u"描述")
    platform = models.CharField(max_length=20)
    """
    is_upload_dev = models.IntegerField(default=0)
    is_upload_local = models.IntegerField(default=0)
    is_upload_online = models.IntegerField(default=0)
    """

    def content_dict(self):
        result_dict = {
            "id": self.id,
            "description": self.description,
            "platform": self.platform
        }
        return result_dict

    def __unicode__(self):
        return self.application.title

    class Meta:
        app_label = 'addonstore'
        abstract = True


class Hoting(BaseOnline):

    platform = models.CharField(max_length=20)
    """
    is_upload_dev = models.IntegerField(default=0)
    is_upload_local = models.IntegerField(default=0)
    is_upload_online = models.IntegerField(default=0)
    """

    def content_dict(self):
        result_dict = {
            "id": self.id,
            "platform": self.platform
        }
        return result_dict

    def __unicode__(self):
        return self.application.title

    class Meta:
        app_label = 'addonstore'
        abstract = True

# -*- coding:utf-8 -*-
from datetime import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _
from dolphinopadmin.base.base_model import BaseStatus, allPlatformBase
from dolphinopadmin.configure.models import Rule
from dolphinopadmin.base.content import PRICE_CHOICES, FEATURE_TYPE_CHOICES, BOOLEAN_CHOICES


class HotappsBase(allPlatformBase, BaseStatus):
    rule = models.ForeignKey(
        Rule, null=True, related_name='+', verbose_name=_('rule'))
    order = models.IntegerField(blank=True, verbose_name=_('order'))

    def content_dict(self, server, is_del):
        matchs = {
            'AndroidEN': 'Android_EN',
            'AndroidJP': 'Android_JP',
        }
        if is_del:
            return {
                "id": self.id,
                "platform": matchs[self.platform],
            }

        result_dict = {
            "platform": matchs[self.platform],
            "order": self.order,
        }
        return result_dict

    def _get_order(self):
        items = self.__class__.objects.all().order_by('-order')
        max_pos = 1 if len(items) == 0 else \
            items[0].order + 1
        return max_pos

    # def save(self, *args, **kwargs):
        # if not self.id:
            #self.order = self._get_order()
            #self.order = self.order * 1000
        #super(HotappsBase, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class Category(HotappsBase):

    title = models.CharField(max_length=50, verbose_name=_('category_name'))
    icon = models.URLField(verify_exists=False, verbose_name=_('icon'))
    brief_description = models.TextField(
        blank=True, max_length=256, verbose_name=_('brief_description'))
    detail_description = models.TextField(
        blank=True, max_length=2048, verbose_name=_('detail_description'))
    is_hot = models.BooleanField(default=False, verbose_name=_('is_hot'))
    display_update = models.BooleanField(
        default=True, verbose_name=_('display_update'))
    update_number = models.IntegerField(
        blank=True, default=1, verbose_name=_('update_number'))
    is_third_part = models.IntegerField(
        choices=BOOLEAN_CHOICES, default=0, verbose_name=_('is_third_part'))
    third_party_url = models.URLField(blank=True, verify_exists=False,
                                      help_text=_('Please icon URL exist!!'), verbose_name=_('third_party_url'))

    def get_applications(self, server):
        app_list = []
        apps = self.hotappsnew_categoryapplicationship_set.all().order_by(
            'order')
        for item in apps:
            app_dict = item.application.content_dict(server)
            app_dict['app_order'] = item.order
            app_list.append(app_dict)
        return app_list

    def content_dict(self, server, is_del=False):
        result_dict = super(Category, self).content_dict(server, is_del)
        if is_del:
            return result_dict
        result_dict.update({
            "id": self.id,
            "category_name": self.title,
            "icon": self.icon,
            "short_description": self.brief_description,
            "detail_description": self.detail_description,
            "is_hot": self.is_hot,
            "display_update": self.display_update,
            "update_number": self.update_number,
            "is_third_part": self.is_third_part,
            "third_party_url": self.third_party_url,
            "application": self.get_applications(server),
        })
        return result_dict

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('category')


class ScreenShot(models.Model):
    pic_url = models.URLField(verify_exists=False, verbose_name=_('pic_url'))
    thumbnails = models.URLField(
        verify_exists=False, verbose_name=_('thumbnails'))
    title = models.CharField(max_length=50, null=True,
                             blank=True, verbose_name=_('title'))
    platform = models.CharField(max_length=20, editable=False)

    def content_dict(self):
        result_dict = {
            "thumbnails": self.thumbnails,
            "pic_url": self.pic_url,
            "title": self.title,
        }
        return result_dict

    def __unicode__(self):
        return "%s" % (self.title or self.pic_url[-16:])

    def save(self, *args, **kwargs):
        if not self.id:
            self.platform = self.filters['platform']
        super(ScreenShot, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('screenshot')
        verbose_name_plural = _('screenshot')


class Application(HotappsBase):

    title = models.CharField(max_length=50, verbose_name=_('title'))
    icon = models.URLField(verify_exists=False, verbose_name=_('icon'))
    backup_icon = models.URLField(
        verify_exists=False, verbose_name=_('backup_icon'))
    is_new = models.IntegerField(
        default=0, choices=BOOLEAN_CHOICES, verbose_name=_('is_new'))
    download_url = models.CharField(
        max_length=200, verbose_name=_('download_url'))
    is_hot = models.BooleanField(default=False, verbose_name=_('is_hot'))
    app_update_status = models.BooleanField(
        default=False, verbose_name=_('app_update_status'))
    app_updatetime = models.DateTimeField(
        blank=True, default=datetime.now, verbose_name=_('app_updatetime'))
    app_version = models.CharField(
        blank=True, max_length=50, verbose_name=_('app_version'))
    app_developer = models.CharField(
        blank=True, max_length=100, verbose_name=_('app_developer'))
    app_rating = models.FloatField(
        blank=True, default=6.0, verbose_name=_('app_rating'))
    app_ratingcount = models.IntegerField(
        blank=True, default=0, verbose_name=_('app_ratingcount'))
    app_lovecount = models.IntegerField(
        blank=True, default=0, verbose_name=_('app_lovecount'))
    force_lovecount = models.BooleanField(
        default=False, verbose_name=_('force_lovecount'))
    short_description = models.TextField(
        max_length=256, verbose_name=_('short_description'))
    detail_description = models.TextField(
        blank=True, max_length=1024, verbose_name=_('detail_description'))
    app_size = models.CharField(
        blank=True, max_length=50, verbose_name=_('app_size'))
    price = models.CharField(max_length=50, blank=True,
                             default='0.0', verbose_name=_('price'))
    original_price = models.CharField(
        max_length=50, blank=True, default='0.0', verbose_name=_('original_price'))
    favourable_price = models.CharField(
        max_length=50, blank=True, default='0.0', verbose_name=_('favourable_price'))
    price_type = models.CharField(
        max_length=50, blank=True, choices=PRICE_CHOICES, verbose_name=('price_type'))
    price_limit_time = models.DateTimeField(
        blank=True, default=datetime.now, verbose_name=_('price_limit_time'))
    is_third_part = models.IntegerField(
        default=0, verbose_name=_('is_third_part'))
    api_url = models.URLField(verify_exists=False, null=True, blank=True,
                              help_text=_('The URL of the Third-part API!!'), verbose_name=_('api_url'))
    pub_time = models.CharField(
        max_length=100, blank=False, verbose_name=_('pub_time'))
    app_type = models.CharField(
        max_length=100, default='App', verbose_name=_('app_type'))

    def get_screenshots(self):
        _list = []
        apps = self.hotappsnew_applicationscreenshotship_set.all()
        for item in apps:
            temp = item.screenshot.content_dict()
            temp["order"] = item.order
            _list.append(temp)
        return _list

    def content_dict(self, server, is_del=False):
        result_dict = super(Application, self).content_dict(server, is_del)
        if is_del:
            return result_dict
        result_dict.update({
            "id": self.id,
            "title": self.title,
            "icon": self.icon,
            "is_new": self.is_new,
            "download_url": self.download_url,
            "is_hot": self.is_hot,
            "app_update_status": self.app_update_status,
            "app_updatetime": self.app_updatetime.strftime("%Y-%m-%d %H:%M:%S"),
            "app_version": self.app_version,
            "app_developer": self.app_developer,
            "app_rating": self.app_rating,
            "app_ratingcount": self.app_ratingcount,
            "app_lovecount": self.app_lovecount,
            "short_description": self.short_description,
            "detail_description": self.detail_description,
            "app_size": self.app_size,
            "price": self.price,
            "original_price": self.original_price,
            "favourable_price": self.favourable_price,
            "price_type": self.price_type,
            "price_limit_time": self.price_limit_time.strftime("%Y-%m-%d %H:%M:%S"),
            "is_third_part": self.is_third_part,
            "api_url": self.api_url,
            "app_type": self.app_type,
            "screenshots": self.get_screenshots(),
            "pub_time": self.pub_time,
        })
        return result_dict

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('application')
        verbose_name_plural = _('application')


class Feature(HotappsBase):
    feature_type = models.CharField(
        max_length=20, default='App', choices=FEATURE_TYPE_CHOICES, verbose_name=_('feature_type'))
    description = models.CharField(
        max_length=200, blank=True, verbose_name=_('description'))
    feature_on_top = models.IntegerField(
        default=0, choices=BOOLEAN_CHOICES, verbose_name=_('feature_on_top'))
    hot_today = models.BooleanField(default=False, verbose_name=_('hot_today'))
    top_feature_pic = models.URLField(
        verify_exists=False, null=True, blank=True,
        help_text='The URL of the Pic on the feature top !!', verbose_name=_('top_feature_pic'))
    small_pic = models.URLField(
        verify_exists=False, null=True, blank=True, verbose_name=_('small_pic'))
    is_third_part = models.IntegerField(
        choices=BOOLEAN_CHOICES, default=0, verbose_name=_('is_third_part'))
    third_part_url = models.URLField(
        verify_exists=False, null=True, blank=True,
        help_text='URL of the feature top pic links to', verbose_name=_('third_part_url'))
    application = models.ForeignKey(Application)
    category = models.ForeignKey(Category)

    def content_dict(self, server, is_del=False):
        result_dict = super(Feature, self).content_dict(server, is_del)
        if is_del:
            return result_dict
        result_dict.update({
            "id": self.id,
            "feature_type": self.feature_type,
            "description": self.description,
            "feature_on_top": self.feature_on_top,
            "hot_today": self.hot_today,
            "top_feature_pic": self.top_feature_pic,
            "small_pic": self.small_pic,
            "is_third_part": self.is_third_part,
            "third_part_url": self.third_part_url,
        })
        if self.feature_type == 'App':
            result_dict['content'] = self.application.content_dict(server)
        else:
            if not self.feature_on_top:
                raise ValueError(_('feature type is category feature on top must be true!'))

            result_dict['content'] = {'category_id': self.category.id,
                                      'category_name': self.category.title
                                      }
        return result_dict

    def title(self):
        return self.application.title if self.feature_type == 'App' else self.category.title
    title.verbose_name = _('title')

    def __unicode__(self):
        return self.feature_type

    class Meta:
        verbose_name = _('feature')
        verbose_name_plural = _('feature')


class Trending(HotappsBase):

    application = models.ForeignKey(Application, verbose_name=_('application'))

    def title(self):
        return self.application.title

    def content_dict(self, server, is_del=False):
        result_dict = super(Trending, self).content_dict(server, is_del)
        if is_del:
            return result_dict
        result_dict.update({
            "id": self.id,
            "application": self.application.content_dict(server),
        })
        return result_dict

    def __unicode__(self):
        return self.application.title

    class Meta:
        verbose_name = _('trending')
        verbose_name_plural = _('trending')

#from splash_screen import *
import time
import logging
from datetime import datetime
from django.db import models
from dolphinopadmin.resource.models import Icon
from dolphinopadmin.configure.models import Rule
from dolphinopadmin.base.base_model import BaseStatus, allPlatformBase
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger('dolphinopadmin.admin')


class BaseSplash(allPlatformBase):

    class Meta:
        abstract = True


class Screen(BaseSplash):
    title = models.CharField(max_length=200, verbose_name=_('title'))
    min_w = models.IntegerField(verbose_name=_('min width'))
    max_w = models.IntegerField(verbose_name=_('max width'))
    min_h = models.IntegerField(verbose_name=_('min height'))
    max_h = models.IntegerField(verbose_name=_('max height'))
    front_pic = models.CharField(max_length=2000, blank=True, editable=False)
    front_icon = models.ForeignKey(
        Icon, related_name="+", verbose_name=_('font picture'))
    front_wifi_only = models.BooleanField(
        default=False, verbose_name=_('load font only in wifi'))
    background_pic = models.CharField(
        max_length=2000, blank=True, editable=False)
    background_icon = models.ForeignKey(
        Icon, related_name='+', verbose_name=_('background picture'))
    background_wifi_only = models.BooleanField(
        default=False, verbose_name=_('load background only in wifi'))

    def content_dict(self, server):
        if self.front_icon_id:
            self.front_icon.upload_file(server)
        if self.background_icon_id:
            self.background_icon.upload_file(server)
        if not self.front_icon_id and not self.front_pic or not self.background_icon_id and not self.background_pic:
            raise ValueError(
                _('screen: %s front or background pic missing!' % self.title))

        result_dict = {
            "id": self.id,
            "min_w": self.min_w,
            "max_w": self.max_w,
            "min_h": self.min_h,
            "max_h": self.max_h,
            "front_pic": self.front_icon.get_url(server) if self.front_icon_id else self.front_pic,
            "front_wifi_only": self.front_wifi_only,
            "background_pic": self.background_icon.get_url(server) if self.background_icon_id else self.background_pic,
            "background_wifi_only": self.background_wifi_only
        }
        return result_dict

    def front_picture(self):
        try:
            return self.front_icon.icon_file()
        except:
            return self.front_pic
    front_picture.verbose_name = _('front picture')
    front_picture.allow_tags = True

    def background_picture(self):
        try:
            return self.background_icon.icon_file()
        except:
            return self.background_pic
    background_picture.verbose_name = _('background picture')
    background_picture.allow_tags = True

    def __unicode__(self):
        return u"%s(%d-%d * %d-%d)" % (self.title, self.min_w, self.max_w, self.min_h, self.max_h)

    class Meta:
        verbose_name = _('screen')
        verbose_name_plural = _('screen')


class Splash(BaseSplash, BaseStatus):

    title = models.CharField(max_length=200, verbose_name=_('title'))
    version = models.CharField(max_length=200, verbose_name=_('version'))
    #min_version = models.IntegerField(verbose_name=_('min version'))
    #max_version = models.IntegerField(verbose_name=_('max version'))
    initial_validity = models.DateTimeField(
        default=datetime.now, verbose_name=_('valid time'))
    validity_by = models.DateTimeField(
        default=datetime.now, verbose_name=_('invalid time'))
    description = models.TextField(
        max_length=10000, verbose_name=_('description'))
    color = models.CharField(max_length=200, verbose_name=_('color'))
    rule = models.ForeignKey(Rule, verbose_name=_('rule'))
    #package = models.ForeignKey(Package)
    #sourceset = models.ForeignKey(SourceSet)
    #screens = models.ManyToManyField(Screen, through='SplashScreenShip')

    # def get_screens(self):
    #    screen_list = []
    #    screens = self.screens.all()
    #    for item in screens:
    #        screen_list.append(item.content_dict())
    #    return screen_list

    def content_dict(self, server, is_del=False):
        if is_del:
            return {
                'id': self.id
            }
        rules = self.rule.content_dict()
        result_dict = {
            "id": self.id,
            "title": self.title,
            "min_version": rules['min_version'],
            "max_version": rules['max_version'],
            "sources": rules['sources'],
            "package": rules['packages'],
            "description": self.description,
            "color": self.color,
            "screens": [ship.screen.content_dict(server) for ship in self.splashscreen_splashscreenship_set.all()],
            "validity_by": self.validity_by.isoformat(),
            "initial_validity": self.initial_validity.isoformat(),
            "last_modified": int(time.time())
        }
        return result_dict

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('splash set')
        verbose_name_plural = _('splash set')

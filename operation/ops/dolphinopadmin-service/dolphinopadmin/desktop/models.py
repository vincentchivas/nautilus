#!/usr/bin/env python
# -*- coding:utf-8 -*-
# coder yfhe
import logging
from django.db import models
from django.utils.translation import ugettext_lazy as _

from dolphinopadmin.configure.models import Rule
from dolphinopadmin.resource.models import Icon
from dolphinopadmin.base.base_model import BaseStatus, allPlatformBase

logger = logging.getLogger('dolphinopadmin.admin')


class DesktopBase(allPlatformBase):

    class Meta:
        abstract = True


class Item(DesktopBase):
    name = models.CharField(max_length=100, verbose_name=_('name'))
    title = models.CharField(max_length=200, verbose_name=_('title'))
    url = models.CharField(max_length=2000, blank=True, verbose_name=_('url'))
    #position = models.IntegerField(verbose_name=_('position'))
    delete = models.BooleanField(verbose_name=_('enable delete'))
    last_modified = models.DateTimeField(auto_now=True)
    icon = models.ForeignKey(Icon, verbose_name=_('icon'))

    def content_dict(self, server):
        self.icon.upload_file(server)
        result_dict = {
            "ttl": self.title,
            "url": self.url,
            "ico": self.icon.get_url(server),
            "d": self.delete
        }
        return result_dict

    def __unicode__(self):
        return u'name:(%s)-title:(%s)' % (self.name, self.title)

    class Meta:
        verbose_name = _('item')
        verbose_name_plural = _('item')


class Folder(DesktopBase):
    name = models.CharField(max_length=100, verbose_name=_('name'))
    title = models.CharField(max_length=200, verbose_name=_('title'))
    #position = models.IntegerField(verbose_name=_('position'))
    delete = models.BooleanField(verbose_name=_('enable delete'))
    last_modified = models.DateTimeField(auto_now=True)
    icon = models.ForeignKey(Icon, verbose_name=_('icon'))

    def get_items(self, server):
        obj_list = []
        items = self.desktop_folderitemship_set.all().order_by('order')
        for item in items:
            webapp = item.item
            dic = webapp.content_dict(server)
            dic['p'] = item.order
            obj_list.append(dic)
        return obj_list

    def __unicode__(self):
        return self.name

    def content_dict(self, server):
        result_dict = {
            'ttl': self.title,
            'its': self.get_items(server)
        }
        return result_dict

    class Meta:
        verbose_name = _('folder')
        verbose_name_plural = _('folder')


class Screen(DesktopBase):
    name = models.CharField(max_length=200)
    sid = models.IntegerField('屏幕ID')
    last_modified = models.DateTimeField(auto_now=True)

    def get_items(self, server):
        obj_list = []
        items = self.desktop_screenitemship_set.all().order_by('order')
        folders = self.desktop_screenfoldership_set.all()

        for item in items:
            webapp = item.item
            dic = webapp.content_dict(server)
            dic['p'] = item.order
            obj_list.append(dic)

        for item in folders:
            webapp = item.folder
            dic = webapp.content_dict(server)
            dic['p'] = item.order
            obj_list.append(dic)

        obj_list.sort(cmp=lambda x, y: cmp(x['p'], y['p']))

        return obj_list

    def content_dict(self, server):
        result_dict = {
            "id": self.id,
            "its": self.get_items(server),
            "sid": self.sid
        }
        return result_dict

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('screen')
        verbose_name_plural = _('screen')


class Desktop(DesktopBase, BaseStatus):

    name = models.CharField(max_length=100, verbose_name=_('name'))
    rule = models.ForeignKey(Rule, verbose_name=_('rule'), help_text=_(
        'this is a new column, old data may not match'))

    def content_dict(self, server, is_del=False):
        if is_del:
            return {"id": self.id}

        rules = self.rule.content_dict()
        result_dict = {
            "id": self.id,
            #"sources": rules['sources'],
            #"package": rules['packages'],
            #"min_version": rules['min_version'],
            #"max_version": rules['max_version'],
            #"operators": rules['operators'],
            #"locales": rules['locales'],
            "_rule": rules,
            "data": [screen.screen.content_dict(server) for screen in self.desktop_desktopscreenship_set.all()],
            "platform": self.platform,
        }
        return result_dict

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('desktop')
        verbose_name_plural = _('desktop')

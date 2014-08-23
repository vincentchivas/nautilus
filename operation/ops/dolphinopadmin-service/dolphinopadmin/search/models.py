#!/usr/bin/env python
# -*- coding:utf-8 -*-
# coder yfhe
import time
import logging
from django.db import models
from django.utils.translation import ugettext_lazy as _
from dolphinopadmin.base.base_model import BaseStatus
from dolphinopadmin.configure.models import Rule
from dolphinopadmin.resource.models import Icon


logger = logging.getLogger('dolphinopadmin.admin')


class SearchBase(models.Model):
    platform = models.CharField(max_length=100, editable=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.platform = self.__class__.filters['platform']
        super(SearchBase, self).save(*args, **kwargs)


class Keyword(SearchBase, BaseStatus):

    name = models.CharField(max_length=100, blank=True, verbose_name=_('name'))
    priority = models.IntegerField(
        help_text=_('1-7 is avaliable,and larger num mean higher priority'), default=1)
    keyword = models.CharField(max_length=200, verbose_name=_('keyword'))
    track = models.CharField(
        max_length=500, help_text=_("track info separated by ','."))
    replace = models.BooleanField(verbose_name=_('is replace'))
    order = models.IntegerField(verbose_name=_('order'))

    rule = models.ForeignKey(Rule, verbose_name=_('rule'))
    last_modified = models.DateTimeField(auto_now=True)

    def content_dict(self, server, is_del=False):
        if is_del:
            return {
                "_sync_key": {
                    "id": self.id,
                    "platform": self.filters['platform']
                },
            }

        result_dict = {
            "_sync_key": {
                "id": self.id,
                "platform": self.filters['platform'],
            },
            "_key": {
                "order": self.order,
                "id": self.id,
            },
            "_priority": self.priority,
            "_meta": {
                "last_modified": int(time.time()),
                "order": self.order,
                "tracks": self.get_tracks(),
                "replace": self.replace,
                "keyword": self.keyword,
            },
            "_rule": self.rule.content_dict()
        }
        return result_dict

    def get_tracks(self):
        track = self.track
        tracks = []
        for item in track.split(','):
            pair = item.split('=')
            dic = {
                'key': pair[0],
                'value': pair[1],
            }
            tracks.append(dic)
        return tracks

    def __unicode__(self):
        return self.keyword

    class Meta:
        verbose_name = _('Keyword')
        verbose_name_plural = _('Keyword')


class Hotword(SearchBase):

    title = models.CharField(max_length=100, verbose_name='title')
    url = models.CharField(max_length=2000, blank=True, verbose_name=_('url'))
    color = models.CharField(max_length=200, blank=True,
                             verbose_name=_('color'), help_text=_('Red is "#FF0000"'))
    highlight = models.BooleanField(verbose_name='is hightlight')

    def content_dict(self):
        result_dict = {
            "title": self.title,
            "url": self.url,
            "highlight": self.highlight
        }
        if self.color:
            result_dict['color'] = self.color
        return result_dict

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('Hotword')
        verbose_name_plural = _('Hotword')


class Search(SearchBase):

    name = models.CharField(max_length=100, verbose_name=_('name'))
    title = models.CharField(max_length=50, verbose_name=_('title'))
    url = models.CharField(max_length=2000, verbose_name=_('url'))
    suggest = models.CharField(
        verbose_name=_('suggest address'), max_length=2000,
        blank=True, help_text=_("warning:please make sure this exactly as client give"))
    last_modified = models.DateTimeField(auto_now=True)
    extend = models.CharField(
        max_length=1024, blank=True, null=True, help_text=_("Be sure in json format"))
    icon = models.ForeignKey(Icon, verbose_name=_('icon'))

    def content_dict(self, server):
        self.icon.upload_file(server)
        result_dict = {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "suggest": self.suggest,
            "last_modified": int(time.mktime(self.last_modified.timetuple())),
            "extend": self.extend,
            "icon": self.icon.base64(),
            "icon_url": self.icon.get_url(server)
        }
        return result_dict

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Search')
        verbose_name_plural = _('Search')


class Category(SearchBase, BaseStatus):

    name = models.CharField(
        max_length=100, verbose_name=_('name'), help_text=_('use in operation'))
    title = models.CharField(
        max_length=100, verbose_name=('title'), help_text=_('display in client'))
    layout = models.IntegerField(verbose_name=_('layout'))
    priority = models.IntegerField(
        help_text=_('1-7 is avaliable,and larger num mean higher priority'), default=1)
    order = models.IntegerField()
    manual_hotword = models.BooleanField(
        default=False, verbose_name=_('manaul hot words'))
    last_modified = models.DateTimeField(auto_now=True)
    rule = models.ForeignKey(Rule, verbose_name=_('rule'))

    def get_searches(self, server):
        obj_list = []
        items = self.search_categorysearchship_set.all()
        for item in items:
            dic = item.search.content_dict(server)
            dic['order'] = item.order
            dic['default'] = item.default
            obj_list.append(dic)
        self.data_verification(obj_list)
        obj_list.sort(lambda a,b: int(a['order'] - b['order']))
        return obj_list

    def data_verification(self, obj_list):
        #if len(obj_list) < 3:
        #    raise ValueError(_('three or more searchengine needed!'))
        default = False
        dup_order = []
        for obj in obj_list:
            if obj['default']:
                if not default:
                    default = True
                else:
                    raise ValueError(_('not more than one default!'))
            if obj['order'] not in dup_order:
                dup_order.append(obj['order'])
            else:
                raise ValueError(_('order can\'t repeat'))
        if not default:
            raise ValueError(_('at lease one default'))

    def get_hotwords(self):
        obj_list = []
        items = self.search_categoryhotwordship_set.all()
        for item in items:
            dic = item.hotword.content_dict()
            obj_list.append(dic)
        return obj_list

    def content_dict(self, server, is_del=False):
        if is_del:
            return {
                "_sync_key": {
                    "id": self.id,
                    "platform": self.filters['platform']
                },
            }

        result_dict = {
            "_sync_key": {
                "id": self.id,
                "platform": self.filters['platform']
            },
            "_key": {
                "layout": self.layout
            },
            "_priority": self.priority,
            "_meta": {
                "last_modified": int(time.time()),
                "order": self.order,
                "manual_hotword": self.manual_hotword,
                "title": self.title
            },
            "_rule": self.rule.content_dict()
        }
        result_dict['_meta_extend.searches'] = self.get_searches(server)
        if self.manual_hotword:
            result_dict['_meta_extend.hotwords'] = self.get_hotwords()
            result_dict['_meta_extend.hotword_modified'] = int(time.time())
        return result_dict

    def __unicode__(self):
        return self.name or self.title

    class Meta:
        verbose_name = _('Search Category')
        verbose_name_plural = _('Search Category')

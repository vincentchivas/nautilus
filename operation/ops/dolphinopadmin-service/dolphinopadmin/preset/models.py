#!/usr/bin/env python
# -*- coding:utf-8 -*-
# coder yfhe@bainainfo.com
import logging
import json
from time import time
from django.db import models
from dolphinopadmin.configure.models import Rule
from django.utils.translation import ugettext_lazy as _
from dolphinopadmin.base.base_model import BaseStatus, allPlatformBase
from dolphinopadmin.resource.models import Icon

logger = logging.getLogger('dolphinopadmin.admin')

DEFAULT_PALTFORM = 'Android'
FILE_PATH = 'adplist/file'


class presetBase(allPlatformBase):

    class Meta:
        abstract = True

class Bookmark(presetBase):
    name = models.CharField(max_length=500, verbose_name=_('name'), help_text=_('for operation'))
    title = models.CharField(max_length=500, verbose_name=_('title'), help_text=_('for client'))
    url = models.CharField(max_length=500, verbose_name=_('url'))
    #order = models.IntegerField()
    #directory = models.BooleanField(default=False)

    def content_dict(self, server):
        result_dict = {
            "name": self.name,
            "url": self.url,
        }
        return result_dict

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('bookmark')
        verbose_name_plural = _('bookmark')

class BookmarkFolder(presetBase):
    name = models.CharField(max_length=500, verbose_name=_('name'), help_text=_('for operation'))
    title = models.CharField(max_length=500, verbose_name=_('title'), help_text=_('for client'))

    def content_dict(self, server):
        items = []
        for item in self.preset_bookmarkfolderbookmarkship_set.all():
            tmp = item.bookmark.content_dict(server)
            tmp.update({'order': item.order})
            items.append(tmp)

        items.sort(lambda a, b: cmp(a['order'], b['order']))
        result_dict = {
            "name": self.title,
            "bookmarks": items
        }
        return result_dict

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('bookmark folder')
        verbose_name_plural = _('bookmark folder')


class Speeddial(presetBase):
    name = models.CharField(max_length=500, verbose_name=_('name'), help_text=_('for operation'))
    title = models.CharField(max_length=500, verbose_name=_('title'), help_text=_('for client'))
    icon = models.ForeignKey(Icon, verbose_name=_('icon'))
    favicon = models.CharField(max_length=500, blank=True, editable=False)
    url = models.CharField(max_length=2000, verbose_name=_('url'))

    def content_dict(self, server):
        result_dict = {
            "title": self.title,
            "url": self.url
        }
        if(self.icon):
            self.icon.upload_file(server);
            result_dict['favicon'] = self.icon.get_url(server);
        else:
            result_dict['favicon'] = self.favicon
        return result_dict

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('Speeddial')
        verbose_name_plural = _('Speeddial')
        app_label = 'preset'


class Strategy(presetBase):
    name = models.CharField(max_length=200, verbose_name=_('name'))
    duration = models.IntegerField(verbose_name=_('duration'))
    strategy_test = models.BooleanField(default=False, verbose_name=_('is test'))
    tutorials = models.CharField(
        max_length=1000, help_text=_('You can specify a list of tutorials separated by \',\''))

    def content_dict(self, server):
        result_dict = {
            "id": self.id,
            "duration": self.duration,
            "strategy_test": self.strategy_test,
            "tutorials": self.tutorials.split(',')
        }
        return result_dict

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Strategy')
        verbose_name_plural = _('Strategy')
        app_label = 'preset'


class Gesture(BaseStatus, presetBase):
    title = models.CharField(max_length=200, verbose_name=_('title'))
    gesture_file = models.FileField(
        upload_to='files/preset', verbose_name=_('gesture file'), help_text=_('please upload gesture!'))
    user_gesture_file = models.CharField(max_length=2000, blank=True, verbose_name=_('user gesture file'), help_text=_('auto complete when publish!'))
    marked_file = models.CharField(max_length=2000, verbose_name=_('marked file'))

    def upload_file(self, server, is_del=False):
        if getattr(self, 'is_upload_%s' % server) is not is_del:
            return (True,)

        if self.gesture_file:
            file_obj = self.gesture_file.name
            result = self.transfer_file(file_obj, server, is_del)
            if not result[0]:
                    raise ValueError(_('operation %s fail!') % self.title)
            setattr(self, 'is_upload_%s' % server, not is_del)
            self.user_gesture_file = '' if is_del else result[1]
            self.save(False)
            return (True,)
        else:
            raise ValueError(_('without upload getsture_file!'))


    def special_content_dict(self,server):
        result_dict = {
            "user_gesture_file": self.user_gesture_file,
            "marked_file": self.marked_file
        }
        return result_dict

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('Gesture')
        verbose_name_plural = _('Gesture')


class Adblock(BaseStatus):
    adp_file = models.FileField(
        upload_to='adplist/file', verbose_name=_('adblock list'), help_text=_('please upload zip file!'))
    rule = models.ForeignKey(Rule, related_name='+')
    local_url = models.CharField(max_length=1000, blank=True, editable=False)
    ec2_url = models.CharField(max_length=1000, blank=True, editable=False)
    china_url = models.CharField(max_length=1000, blank=True, editable=False)
    last_modified = models.DateTimeField(auto_now_add=True, editable=False)

    def special_upload_file(self, server, is_del=False):
        if getattr(self, 'is_upload_%s' % server) is not is_del:
            return (True,)

        if self.adp_file:
            file_obj = self.adp_file.name
            result = self.transfer_file(file_obj, server, is_del)
            if not result[0]:
                    raise ValueError(_('operation %s fail!') % self.title)
            setattr(self, 'is_upload_%s' % server, not is_del)
            setattr(self, '%s_url' % server, '' if is_del else result[1])
            self.save(False)
            return (True,)

    def content_dict(self, server, is_del=False):
        self.special_upload_file(server, is_del)
        if is_del:
            return {
                'id': self.id
            }

        result_dict = {
            'id': self.id,
            'last_modified': int(time()),
            '_rule': self.rule.content_dict(),
        }
        result_dict['download_url'] = eval('self.%s_url' % server)
        return result_dict

    def __unicode__(self):
        return self.adp_file.name

    class Meta:
        verbose_name = u'advertise block list'
        verbose_name_plural = u'advertise block list'
        app_label = 'preset'


class Preset(BaseStatus, presetBase):
    OS_CHOICES = (
        (u'android', u'android'),
        (u'iPhone', u'iPhone'),
        (u'iPad', u'iPad'),
        (u'wPhone', u'wPhone')
    )
    title = models.CharField(max_length=200, verbose_name=_('title'))
    os = models.CharField(max_length=200, choices=OS_CHOICES, verbose_name=_('os'))
    #package = models.CharField(max_length=200)
    #locale = models.CharField(max_length=200)
    #max_version = models.IntegerField()
    #min_version = models.IntegerField()
    data_test = models.BooleanField(default=False, verbose_name=_('is test'))
    homepage = models.CharField(max_length=1000, verbose_name=_('homepage'))
    hotapps = models.CharField(max_length=1000, blank=True, verbose_name=_('hotapps'))
    tutorial = models.CharField(max_length=1000, verbose_name=_('tutorial'))
    about = models.CharField(max_length=1000, verbose_name=_('about'))
    more_addon_link = models.CharField(max_length=1000, blank=True, verbose_name=_('more addon link'))
    more_theme_link = models.CharField(max_length=1000, blank=True, verbose_name=_('more theme link'))
    check_update_link = models.CharField(max_length=1000, blank=True, verbose_name=_('check update link'))
    show_download_translate = models.BooleanField(verbose_name=_('show download translate'))
    rate_me_link = models.CharField(max_length=1000, blank=True, verbose_name=_('rate me link'))
    rule = models.ForeignKey(Rule, related_name="+", verbose_name=_('rule'))
    gesture = models.ForeignKey(Gesture, verbose_name=_('gesture'))

    old_platform = models.CharField(max_length=100, default=DEFAULT_PALTFORM, verbose_name=_('platform'))

    def content_dict(self, server, is_del=False):
        if is_del:
            return {
                'id': self.id
            }
        strategies = self.preset_presetstrategyship_set.all()
        strategy_num = len(strategies)
        if strategy_num == 0 or strategy_num > 2:
            raise ValueError(_('strategy number should be 1 or 2.'))
        else:
            if strategy_num == 2 and not (strategies[0].strategy.strategy_test == strategies[1].strategy.strategy_test == True):
                raise ValueError(_('strategy test info should be true when there are 2 strategies.'))
            elif self.data_test == strategies[0].strategy.strategy_test == True:
                raise ValueError(_('data and strategy test should not be true at the same time'))

        rules = self.rule.content_dict()

        bookmarks = []
        for item in self.preset_presetbookmarkship_set.all().order_by('order'):
            tmp = item.bookmark.content_dict(server)
            tmp['order'] = item.order
            bookmarks.append(tmp)

        for item in self.preset_presetbookmarkfoldership_set.all():
            tmp = item.bookmarkfolder.content_dict(server)
            tmp['order'] = item.order
            bookmarks.append(tmp)
        bookmarks.sort(cmp=lambda x, y: cmp(x['order'], y['order']))

        speeddials = []
        for item in self.preset_presetspeeddialship_set.all().order_by('order'):
            tmp = item.speeddial.content_dict(server)
            tmp['order'] = item.order
            speeddials.append(tmp)

        search_engines = []
        for item in self.preset_presetcategoryship_set.all():
            datas = []
            for search in item.category.get_searches(server):
                if search.get('extend') != None:
                    try:
                        extend = search.pop('extend')
                        search.update(json.loads(extend))
                    except Exception,e:
                        print e
                search.pop('last_modified')
                search['icon'] = search.pop('icon_url')
                datas.append(search)

            search_engines.append({
                'searches': datas,
                'layout': item.category.layout,
                'title': item.category.title,
            })

        strategys = [item.strategy.content_dict(server) for item in self.preset_presetstrategyship_set.all()]

        result_dict = {
            "id": self.id,
            "os": self.os.lower(),
            "package": rules['packages'][0],
            "locale": rules['locales']['include'],
            "sources": rules['sources']['include'],
            "data_test": self.data_test,
            "max_version": rules['max_version'],
            "min_version": rules['min_version'],
            "home_page": self.homepage,
            "hotapps": self.hotapps,
            "tutorial": self.tutorial,
            "about": self.about,
            "more_addon_link": self.more_addon_link,
            "more_theme_link": self.more_theme_link,
            "check_update_link": self.check_update_link,
            "show_download_translate": self.show_download_translate,
            "rate_me_link": self.rate_me_link,
            "bookmarks": bookmarks,
            "speeddials": speeddials,
            "strategies": strategys,
            'gesture': self.gesture.special_content_dict(server),
            'platform': self.old_platform,
            'search_engines': search_engines,
        }
        return result_dict

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('Preset')
        verbose_name_plural = _('Preset')

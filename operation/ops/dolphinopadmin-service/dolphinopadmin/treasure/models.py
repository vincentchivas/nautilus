# -*- coding:utf-8 -*-
import logging
import time
from datetime import datetime
from django.db import models
#import base64
#from dolphinopadmin.base.models import BaseOnline, BaseFile, OTHER
#from operator import attrgetter
#from dolphinopadmin.base.admin import EnhancedAdminInline
from dolphinopadmin.configure.models import Rule
from dolphinopadmin.base.base_model import BaseStatus, allPlatformBase
from dolphinopadmin.resource.models import Icon
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger('dolphinopadmin.admin')


class BaseTreasure(allPlatformBase):

    class Meta:
        abstract = True


class Treasure(BaseTreasure, BaseStatus):

    name = models.CharField(max_length=100, verbose_name=_('name'))
    rule = models.ForeignKey(Rule, related_name='+', verbose_name=_('rule'))

    def get_items(self, server):
        obj_list = []
        items = self.treasure_treasureitemship_set.all().order_by('order')
        for item in items:
            dic = item.item.content_dict(server)
            dic['order'] = item.order
            obj_list.append(dic)
        return obj_list

    def content_dict(self, server, is_del=False):
        if is_del:
            return {
                "id": self.id
            }

        rules = self.rule.content_dict()
        result_dict = {
            "id": self.id,
            "operators": rules['operators'],
            "package": rules['packages'],
            "sources": rules['sources'],
            "max_version": rules['max_version'],
            "min_version": rules['min_version'],
            "items": self.get_items(server),
            "last_modified": int(time.time()),
        }
        return result_dict

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _("treasure set")
        verbose_name_plural = _("treasure set")


class Section(BaseTreasure, BaseStatus):

    PROMOTE_CHOICES = (
        (-1, u'manual'),
        (0, u'none'),
        (1, u'new'),
        (2, u'hot'),
    )
    name = models.CharField(max_length=100, verbose_name=_('name'))
    title = models.CharField(
        blank=True, max_length=100, verbose_name=_('title'))
    icon = models.URLField(max_length=1000, verbose_name=_('icon'))
    promote = models.IntegerField(
        default=u'none', choices=PROMOTE_CHOICES, verbose_name=_('promote'))
    rule = models.ForeignKey(Rule, related_name='+', verbose_name=_('rule'))
    #cmcc = models.BooleanField(default=True, verbose_name='移动')
    #unicom = models.BooleanField(default=True, verbose_name='联通')
    #telecom = models.BooleanField(default=True, verbose_name='电信')
    #other_operator = models.BooleanField(default=True, verbose_name='其它运营商')
    last_modified = models.DateTimeField(auto_now=True)
    #package = models.ForeignKey(Package)
    #sourceset = models.ForeignKey(SourceSet)
    #groups = models.ManyToManyField(Group, through='SectionGroupShip')
    #items = models.ManyToManyField(Item, through='SectionItemShip')
#    hot_icon = models.ForeignKey(Icon)

    def get_groups(self):
        obj_list = []
        items = self.treasure_sectiongroupship_set.all().order_by('order')
        for item in items:
            dic = item.group.content_dict()
            dic['order'] = item.order
            obj_list.append(dic)
        return obj_list

    def get_items(self):
        ids = []
        groups = self.get_groups()
        for group in groups:
            for cat in group['cats']:
                for it in cat['items']:
                    ids.append(it['id'])
        obj_list = []
        items = self.treasure_sectionitemship_set.all().order_by('id')
        for item in items:
            if item.item.id not in ids:
                dic = item.item.content_dict()
                obj_list.append(dic)
        return obj_list

    def content_dict(self, server, is_del=False):
        if is_del:
            return {
                'id': self.id
            }
        rules = self.rule.content_dict()
        result_dict = {
            "id": self.id,
            "title": self.title,
            "icon": self.icon,
            "time": int(time.time()),
            "hot": self.promote,
            "operators": rules['operators'],
            "package": rules['packages'][0],
            "sources": rules['sources'],
            "groups": self.get_groups(),
            "updates": self.get_items(),
        }
        return result_dict

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('treasure section(for old)')
        verbose_name_plural = _('treasure section(for old)')


class Group(BaseTreasure):

    name = models.CharField(max_length=100, verbose_name=_('name'))
    title = models.CharField(
        max_length=100, blank=True, verbose_name=_('title'))

    def get_categorys(self):
        obj_list = []
        items = self.treasure_groupcategoryship_set.all().order_by('order')
        for item in items:
            dic = item.category.content_dict()
            dic['order'] = item.order
            obj_list.append(dic)
        return obj_list

    def content_dict(self):
        result_dict = {
            "group": self.title,
            "cats": self.get_categorys()
        }
        return result_dict

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('group')
        verbose_name_plural = _('group')
        app_label = 'treasure'


class Category(BaseTreasure):

    name = models.CharField(max_length=100, verbose_name=_('name'))
    title = models.CharField(
        max_length=100, blank=True, verbose_name=_('title'))
    url = models.CharField(
        max_length=2000, blank=True, verbose_name=_('url'))

    def get_items(self):
        obj_list = []
        items = self.treasure_categoryitemship_set.all().order_by('order')
        order_list = []
        for item in items:
            if item.order not in order_list:
                order_list.append(item.order)
        for position in order_list:
            filter_list = []
            filter_list = [item for item in items if item.order == position]
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
        result_dict = {
            "title": self.title,
            "url": self.url,
            "items": self.get_items()
        }
        return result_dict

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('category')


class Item(BaseTreasure):

    title = models.CharField(max_length=50, verbose_name=_('title'))
    url = models.CharField(max_length=2000, verbose_name=_('url'))
    promotion = models.TextField(
        max_length=256, blank=True, verbose_name=_('promotion'))
    last_modified = models.DateTimeField(
        auto_now=True, verbose_name=_('modified time'))
    icon = models.ForeignKey(Icon, related_name="+", verbose_name=_('icon'))

    def content_dict(self, server=None):
        result_dict = {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "promotion": self.promotion,
            "last_modified": int(time.mktime(self.last_modified.timetuple()))
        }
        if server:
            self.icon.upload_file(server)
            result_dict['icon'] = self.icon.get_url(server)
        else:
            result_dict['icon'] = self.icon.base64(True)

        return result_dict

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('Item')
        verbose_name_plural = _('Item')

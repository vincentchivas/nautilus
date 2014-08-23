#! -*- coding:utf-8 -*-
import time
import logging
import json
from django.db import models
from django.utils.translation import ugettext_lazy as _

from dolphinopadmin.configure.models import Rule
from dolphinopadmin.resource.models import Icon
from dolphinopadmin.base.base_model import BaseStatus
from dolphinopadmin.base.content import PUSH_METHOD
from dolphinopadmin.utils import string_with_title
from dolphinopadmin.search.models import Search
from dolphinopadmin.utils import toTimestampMs

logger = logging.getLogger('dolphinopadmin.admin')
PUSH_TYPES = [('speed_dial', unicode(_('speeddial'))),
              ('bookmark', unicode(_('bookmark'))),
              ('engineswitch', unicode(_('engineswitch'))),
              ('searchengine', unicode(_('search engine'))),
              ('trafficclean', unicode(_('traffic_clean'))),
              ('newhome_notify', unicode(_('news home notify')))]

ENGINE_SWITCH = ((0, _('switch off')), (1, _('switch on')))
TRAFFIC_CLEAN = ((0, _('traffic_clean_disable')), (1, _('traffic_clean_enable')))

class PushBase(models.Model):
    platform = models.CharField(max_length=100, editable=False)
    types = models.CharField(max_length=100, editable=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.platform = self.__class__.filters['platform']
        self.types = self.__class__.filters['types']
        super(PushBase, self).save(*args, **kwargs)


class Item(PushBase):
    url = models.URLField(max_length=200, verbose_name=_('url'))
    title = models.CharField(max_length=100, verbose_name=_('title'))
    icon = models.ForeignKey(Icon, blank=True, null=True,
                             verbose_name=_('icon'), related_name="+")

    def content_dict(self, server):
        self.icon.upload_file(server)
        result_dict = {
            'url': self.url,
            'title': self.title,
            'icon': self.icon.get_url(server)
        }
        return result_dict

    def __unicode__(self):
        return self.url

    class Meta:
        verbose_name = _('Item')
        verbose_name_plural = _('Item')
        app_label = string_with_title("push", _("push messages"))


class Folder(PushBase):
    title = models.CharField(max_length=100, verbose_name=_('title'))

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('Folder')
        verbose_name_plural = _('Folder')
        app_label = string_with_title("push", _("push messages"))


class FolderItemShip(models.Model):
    folder = models.ForeignKey(
        Folder, related_name='folderitems', verbose_name='folder')
    item = models.ForeignKey(Item, verbose_name='item')
    order = models.IntegerField(verbose_name=_('order'))

    def __unicode__(self):
        return "%s(%s)" % (self.folder, self.item.title)

    class Meta:
        verbose_name = _('folder link item')
        verbose_name_plural = _('folder link item')
        app_label = string_with_title("push", _("push messages"))


class EngineStatus(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("StatusName"))
    serial_number = models.IntegerField(verbose_name=_("SerialNumber"))

    def __unicode__(self):
        return u"%d %s" % (self.serial_number, self.name)

    class Meta:
        verbose_name = _("EngineStatus")
        verbose_name_plural = _("EngineStatus")
        app_label = 'push'


class PushCommon(BaseStatus, PushBase):
    title = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('title'))
    method = models.IntegerField(
        choices=PUSH_METHOD, blank=True, null=True, default=0, verbose_name=_('operation'))
    item = models.ForeignKey(
        Item, blank=True, null=True, verbose_name=_('item'))
    folder = models.ForeignKey(
        Folder, blank=True, null=True, verbose_name=_('folder'))
    search = models.ForeignKey(
        Search, blank=True, null=True, verbose_name=_('search'))
    modify_url = models.CharField(
        max_length=200, blank=True, verbose_name=_('url'))
    order = models.IntegerField(blank=True, default=1, verbose_name=_('order'))
    can_delete = models.BooleanField(
        default=True, verbose_name=_('enable deleted'))
    unique_name = models.CharField(max_length=200, blank=True, verbose_name=_('search engine unique name'), help_text=_('required'))
    is_default = models.BooleanField(
        default=False, verbose_name=_('is default'))
    is_force = models.BooleanField(
        default=False, verbose_name=_('is force'))

    rule = models.ForeignKey(Rule, verbose_name=_('push rule'))

    # add for new demand
    engine_switch = models.IntegerField(
        choices=ENGINE_SWITCH, null=True, blank=True, default=0, verbose_name=_("EngineSwitch"))
    target_engine = models.ManyToManyField(
        EngineStatus, blank=True, verbose_name=_("TargetStatus"))

    # add for new demand of traffic clear
    traffic_clean = models.IntegerField(choices=TRAFFIC_CLEAN, null=True, blank=True, default=1, verbose_name=_("traffic_clean"))
    search_engine = models.CharField(max_length=50, blank=True, verbose_name=_('traffic_clean_search_engine'))
    partner_id_name = models.CharField(max_length=50, blank=True, verbose_name=_('partner_id_key'))
    partner_id_value = models.CharField(max_length=50, blank=True, verbose_name=_('partner_id_value'))
    start_time = models.DateTimeField(blank=True, verbose_name=_('traffic_clean_start_time'),  help_text=_("only_valid_for_enable_traffic_clean"))
    end_time = models.DateTimeField(blank=True, verbose_name=_('traffic_clean_end_time'), help_text=_("only_valid_for_enable_traffic_clean"))

    class Meta:
        verbose_name = _('push messages')
        verbose_name_plural = _('push messages')
        app_label = string_with_title("push", _("push messages"))

    def all_target(self):
        if self.__class__.filters['types'] is 'engineswitch':
            result_list = []
            for obj in self.target_engine.all():
                result_list.append(u"%s" % obj)
            return " | ".join(result_list)

    def save(self, *args, **kwargs):
        if self.__class__.filters['types'] is 'engineswitch':
            self.method = 0
            self.order = 1
        else:
            self.engine_switch = -1
        super(PushCommon, self).save(*args, **kwargs)

    def content_dict(self, server, is_del=False):
        if is_del:
            return {
                "_sync_key": {
                    'id': self.id,
                },
            }
        if self.__class__.filters['types'] is 'newhome_notify':
            return {
                "_sync_key": {
                    "id": self.id,
                },
                "_rule": self.rule.content_dict(),
                "_meta":{
                    "id": self.id,
                    "type": 15,
                    "data":{}
                },
            }

        if self.__class__.filters['types'] is 'engineswitch':
            if self.engine_switch is None:
                raise ValueError(_("engineswitch should be of a valid value"))
            if self.target_engine.all().count() == 0:
                raise ValueError(_("no target engine status is selected"))
            result_dict = {
                "_sync_key": {
                    "id": self.id
                },
                "_rule": self.rule.content_dict(),
                "_meta": {
                    "id": self.id,
                    "type": 9,
                    "text": self.engine_switch,
                },
            }
            result_dict['_rule'].update({"target_engine": [i.serial_number for
                                                           i in self.target_engine.all()]})
            return result_dict
        if self.__class__.filters['types'] is 'trafficclean':
            if self.search_engine is None or self.partner_id_name is None or self.partner_id_value is None \
                    or str.strip(str(self.search_engine)) == '' or str.strip(str(self.partner_id_name)) == '' \
                    or str.strip(str(self.partner_id_value)) == '':
                raise ValueError(_("trafficclean_must_be_filled"))
            if self.traffic_clean == 1:
                if self.start_time >= self.end_time:
                    raise ValueError(_("end_time_must_be_later"))
                result_dict = {
                "_sync_key": {
                    "id": self.id
                    },
                    "_rule": self.rule.content_dict(),
                    "_meta": {
                        "id": self.id,
                        "type": 13,
                        "data": {
                            "search_engine": self.search_engine,
                            "partner_id_name": self.partner_id_name,
                            "partner_id_value": self.partner_id_value,
                            "start_time": toTimestampMs(self.start_time),
                            "end_time": toTimestampMs(self.end_time),
                        },
                    },
                }
            elif self.traffic_clean == 0:
                result_dict = {
                "_sync_key": {
                    "id": self.id
                    },
                    "_rule": self.rule.content_dict(),
                    "_meta": {
                        "id": self.id,
                        "type": 14,
                        "data": {
                            "search_engine": self.search_engine,
                            "partner_id_name": self.partner_id_name,
                            "partner_id_value": self.partner_id_value,
                        },
                    },
                }
            else:
                raise ValueError(_("trafficclean_must_be_chosen"))
            return result_dict
        push_matchs = [
            'add_bookmark', 'delete_bookmark', 'modify_bookmark', 'add_bookmark_folder', 'add_speed_dial',
            'delete_speed_dial', 'modify_speed_dial', 'add_speed_dial_folder','placeholder', 'placeholder',
            'add_searchengine', 'modify_searchengine', 'delete_searchengine', 'enable_trafficclean', 'disable_trafficclean', 'newhome_notify']
        method = "%s_%s" % (['modify', 'add', 'delete']
                            [self.method], self.types)
        data = {}
        if self.__class__.filters['types'] is 'searchengine':

            if self.rule and self.rule.min_version <= 278:
                raise ValueError(_('min version can\'t lower than 278, more info please chat with pm!'))
            if not self.unique_name:
                raise ValueError(_('unique name can\'t be empty!'))
            data['default_engine'] = '';
            if self.method != 2:
                if not self.search:
                    raise ValueError(_('you need point the target!'))

                search_content = self.search.content_dict(server)
                data.update({
                    'title': search_content.get('title',''),
                    'id': search_content.get('id',0),
                    'url': search_content.get('url', ''),
                    'suggest': search_content.get('suggest', ''),
                    'color': search_content.get('color', ''),
                    'icon': search_content.get('icon_url'),
                })
                if search_content['extend']:
                    try:
                        data.update(json.loads(search_content['extend']))
                    except:
                        pass
                data['default_engine'] = self.unique_name if self.is_default else '';

            data.update({
                'unique_name': self.unique_name,
                'is_force': int(self.is_force),
            })
        elif self.folder:
            method += '_folder'
            item_type = push_matchs.index('add_%s' % self.types)
            itemships = self.folder.folderitems.order_by('order')
            items = []
            for i, itemship in enumerate(itemships):
                item = itemship.item
                item_dict = {
                    'type': item_type,
                    'order': i,
                    'can_delete': 1,
                    'url': item.url,
                    'title': item.title,
                    'modify_url': ''
                }
                if item.icon:
                    item.icon.upload_file(server)
                    item_dict['icon'] = item.icon.get_url(server)
                else:
                    item_dict['icon'] = ''
                items.append(item_dict)
            data.update({
                'order': self.order,
                'can_delete': int(self.can_delete),
                'title': self.folder.title,
                'items': items
            })
        else:
            data.update({
                'url': self.item.url,
                'order': self.order,
                'can_delete': int(self.can_delete),
                'title': self.item.title,
                'modify_url': self.modify_url,
            })
            if self.item.icon:
                self.item.icon.upload_file(server)
                data['icon'] = self.item.icon.get_url(server)
            else:
                data['icon'] = ''

        try:
            push_type = push_matchs.index(method)
        except Exception:
            assert False, 'push method error'
        result_dict = {
            "_sync_key": {
                'id': self.id,
            },
            "_meta": {
                'id': self.id,
                'data': data,
                'type': push_type,
            },
            "_rule": self.rule.content_dict()
        }
        return result_dict


class Push(BaseStatus):
    name = models.CharField(max_length=100, blank=True, verbose_name=_('name'))
    push_type = models.CharField(max_length=200, verbose_name=_('push type'))
    content1 = models.CharField(
        max_length=500, help_text=_("Be sure in json format"))
    content2 = models.CharField(
        max_length=500, blank=True, null=True, help_text=_("Be sure in json format"))
    content3 = models.CharField(
        max_length=500, blank=True, null=True, help_text=_("Be sure in json format"))
    content4 = models.CharField(
        max_length=500, blank=True, null=True, help_text=_("Be sure in json format"))
    order = models.IntegerField()
    platform = models.CharField(max_length=100, editable=False)
    rule = models.ForeignKey(Rule)
    last_modified = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.platform = self.__class__.filters['platform']
        super(Push, self).save(*args, **kwargs)

    def content_dict(self, server, is_del=False):
        if is_del:
            return {
                "id": self.id
            }

        result_dict = {
            "id": self.id,
            "_key": {
                "message_id": self.id,
            },
            "_meta": {
                "last_modified": int(time.time()),
                "push_type": self.push_type,
                "content1": self.content1,
                "content2": self.content2,
                "content3": self.content3,
                "content4": self.content4,
            },
            "_rule": self.rule.content_dict()
        }
        return result_dict

    class Meta:
        verbose_name = unicode(_("push messages"))
        verbose_name_plural = unicode(_("push messages"))

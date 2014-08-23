#! -*- coding:utf-8 -*-
import logging
from django.db import models
from dolphinopadmin.configure.models import Rule
from dolphinopadmin.resource.models import Icon

from django.utils.translation import ugettext_lazy as _
from dolphinopadmin.base.base_model import BaseStatus, datetime2timestamp

logger = logging.getLogger('dolphinopadmin.admin')


class SmsBase(models.Model):
    name = models.CharField(
        max_length=200, verbose_name=_('name'), help_text=_('only for operation'))
    platform = models.CharField(max_length=100, editable=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.platform = self.__class__.filters['platform']
        super(SmsBase, self).save(*args, **kwargs)


class PhoneNumber(SmsBase):
    title = models.CharField(
        max_length=200, verbose_name=_('title'), help_text=_('for client'))
    number = models.CharField(max_length=200, verbose_name=_(
        'phone number'), help_text=_('phone number for match'))
    icon = models.ForeignKey(Icon, verbose_name=_('icon'), related_name="+")

    def content_dict(self, server):
        result_dict = {
            'title': self.title,
            'num': self.number,
            'icon': '',
        }
        if self.icon:
            self.icon.upload_file(server)
            result_dict['icon'] = self.icon.get_url(server)
        return result_dict

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('phone number')


class KeyWord(SmsBase):
    key_value = models.CharField(max_length=200, verbose_name=_(
        'key words'), help_text=_('keyword for client match'))

    def content_dict(self):
        return self.key_value

    def __unicode__(self):
        return '%s(%s)' % (self.name, self.key_value)

    class Meta:
        verbose_name = _('key words')


class SmsFilters(SmsBase, BaseStatus):
    collect_switch = models.BooleanField(default=True, verbose_name=_(
        'msm collect switch'), help_text=_('select mean disable'))
    pop_switch = models.BooleanField(default=False, verbose_name=_(
        'msm popup switch'), help_text=_('select mean disable'))
    main_switch = models.BooleanField(default=False, verbose_name=_('main switch'), help_text=_(
        'warning:select mean disable,and select this may not recover!'))
    interval_time = models.IntegerField(default=24, verbose_name=_(
        'client check interval'), help_text=_('adjust client check data frequency'))
    rule = models.ForeignKey(
        Rule, verbose_name=_('rules'), help_text=_('detail manage rules'))

    def content_dict(self, server, is_del=False):
        result = {
            'id': self.id,
            'collect': int(self.collect_switch),
            'pop': int(self.pop_switch),
            'complete_close': int(self.main_switch),
            'interval': self.interval_time,
            'keywords': [i.keyword.key_value for i in self.sms_smsfilterskeywordship_set.all()],
            'numbers': [i.phonenumber.content_dict(server) for i in self.sms_smsfiltersphonenumbership_set.all()],
            '_rule': self.rule.content_dict(),
            'mt': datetime2timestamp(self.modified_time)
        }
        return result

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('msm filter')

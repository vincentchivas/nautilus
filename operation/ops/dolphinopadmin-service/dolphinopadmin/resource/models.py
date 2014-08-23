#!/usr/bin/env python
# -*- coding:utf-8 -*-
#    coder yfhe
import os
import time
import base64
import logging
from datetime import datetime
from PIL import Image
from django.db import models
from django.conf import settings
from dolphinopadmin.utils import scp
#from dolphinopadmin.remotedb import config, basedb
from dolphinopadmin.base.models import BaseOnline
from django.utils.translation import ugettext_lazy as _
from dolphinopadmin.base.base_model import BaseStatus

#config(basedb, settings.ENV_CONFIGURATION)

logger = logging.getLogger('dolphinopadmin.admin')

SERVERS = settings.ENV_CONFIGURATION
BASE_DIR = 'icon/'


class Icon(BaseStatus):

    icon = models.FileField(upload_to='icon/')
    title = models.CharField(max_length=200)
    local_url = models.CharField(max_length=1000)
    china_url = models.CharField(max_length=1000)
    ec2_url = models.CharField(max_length=1000)
    width = models.IntegerField(default=0, blank=True, help_text='不必填写，自动识别')
    height = models.IntegerField(default=0, blank=True, help_text='不必填写，自动识别')
    last_modified = models.DateTimeField(auto_now_add=True)
    upload_local = models.DateTimeField(
        auto_now_add=True, verbose_name="上传到本地服务器时间")
    upload_china = models.DateTimeField(
        auto_now_add=True, verbose_name="上传到中国服务器时间")
    upload_ec2 = models.DateTimeField(
        auto_now_add=True, verbose_name="上传到国外服务器时间")

    def upload_file(self, server, is_del=False):
        file_obj = self.icon.name
        if not getattr(self, 'is_upload_%s' % server):
            if not is_del:
                result = self.transfer_file(file_obj, server)
                print result
                if not result[0]:
                    raise ValueError(_('upload %s fail!') % self.title)
                setattr(self, 'is_upload_%s' % server, True)
                setattr(self, '%s_url' % server, result[1])
                self.save(False)
                return (True,)
            else:
                return (False, _('warning: file %s not delete because file not uploaded' % self.title))
        else:
            if is_del:
                result = self.transfer_file(file_obj, server, True)
                print result
                if not result[0]:
                    raise ValueError(_('delete %s fail') % self.title)
                setattr(self, 'is_upload_%s' % server, False)
                setattr(self, '%s_url' % server, '')
                self.save(False)
                return (True,)
            else:
                return (False, _('warning: file %s not upload because file had been upload' % self.title))

    def icon_name(self):
        return os.path.basename(self.icon.name)

    def icon_file(self):
        return '<img src="%s"/>' % self.icon.url
    icon_file.allow_tags = True

    def get_url(self, server):
        return getattr(self, '%s_url' % server)

    def base64(self, pic=True):
        content = self.icon.read()
        icon = base64.b64encode(content)
        result_dict = {
            "id": self.id,
            "last_modified": int(time.mktime(self.last_modified.timetuple()))
        }
        if pic:
            result_dict['icon'] = icon
        return result_dict

    def _check_name(self):
        name = self.icon.name
        logger.info(name)
        logger.info(len(name))
        logger.info(len(name.encode('utf-8')))
        if len(name.encode('utf-8')) != len(name):
            raise ValueError('图标名不能有汉字等字符')

    def save(self, modified=True):
        try:
            self._check_name()
        except Exception, e:
            return e
        if modified:
            self.last_modified = datetime.now()
        super(Icon, self).save()
        icon_file = os.path.join(settings.MEDIA_ROOT, self.icon.name)
        logger.info(icon_file)
        try:
            image = Image.open(icon_file)
            self.height, self.width = image.size
        except:
            self.height, self.width = (0, 0)
        super(Icon, self).save()

    def __unicode__(self):
        return "%s(%s)" % (self.title, os.path.basename(self.icon.name))

    class Meta:
        app_label = 'resource'


class ResourceBase(BaseStatus):
    file_obj = models.FileField(upload_to='resources/', verbose_name=_('file'),
                                help_text=_('valid file name must be in [a-zA-Z0-9_]'))
    types = models.CharField(max_length=100, editable=False)
    local_url = models.CharField(max_length=1000)
    china_url = models.CharField(max_length=1000)
    ec2_url = models.CharField(max_length=1000)
    title = models.CharField(max_length=200, verbose_name=_('title'))
    width = models.IntegerField(default=0, blank=True, verbose_name=_(
        'width'), help_text=_('please ignore,auto reconize'))
    height = models.IntegerField(default=0, blank=True, verbose_name=_(
        'height'), help_text=_('please ignore,auto reconize'))

    def __unicode__(self):
        return "%s(%s)" % (self.title, os.path.basename(self.file_obj.name))

    class Meta:
        verbose_name = _('file')
        verbose_name_plural = _('file')

    def upload_file(self, server, is_del=False):
        file_obj = self.file_obj.name
        if not getattr(self, 'is_upload_%s' % server):
            if not is_del:
                result = self.transfer_file(file_obj, server)
                print result
                if not result[0]:
                    raise ValueError(_('upload %s fail!') % self.title)
                setattr(self, 'is_upload_%s' % server, True)
                setattr(self, '%s_url' % server, result[1])
                self.save(False)
                return (True,)
            else:
                return (False, _('warning: file %s not delete because file not uploaded' % self.title))
        else:
            if is_del:
                result = self.transfer_file(file_obj, server, True)
                print result
                if not result[0]:
                    raise ValueError(_('delete %s fail') % self.title)
                setattr(self, 'is_upload_%s' % server, False)
                setattr(self, '%s_url' % server, '')
                self.save(False)
                return (True,)
            else:
                return (False, _('warning: file %s not upload because file had been upload' % self.title))

    def file_name(self):
        return os.path.basename(self.file_obj.name)

    def img_file(self):
        return '<img src="%s"/>' % self.file_obj.url
    img_file.allow_tags = True

    def get_url(self, server):
        return getattr(self, '%s_url' % server)

    def _check_name(self):
        name = self.file_obj.name
        logger.info('name:%s, len:%d, len_utf:%d' %
                    (name, len(name), len(name.encode('utf-8'))))
        if len(name.encode('utf-8')) != len(name):
            raise ValueError(_('valid file name must be in [a-zA-Z0-9_]'))

    def save(self, *args, **kwargs):
        # print dir(self.file_obj)
        #base_path = self.file_obj.upload_to
        #self.file_obj.upload_to = os.path.join(base_path, self.types)
        try:
            self._check_name()
        except Exception, e:
            return e
        super(ResourceBase, self).save(*args, **kwargs)

        if self.filters['types'] in ('icon', 'screenshot'):
            img_obj = os.path.join(settings.MEDIA_ROOT, self.file_obj.name)
            logger.info(img_obj)
            image = Image.open(img_obj)
            self.height, self.width = image.size
            super(ResourceBase, self).save(*args, **kwargs)

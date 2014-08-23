# -*- coding:utf-8 -*-
'''
Copyright (c) 2011 Baina Info Inc. All rights reserved.
@Author : Wenyuan Wu
@Date : 2011-11-23
'''
from django.db import models
from django.conf import settings
from dolphinopadmin.remotedb import config, feedback

config(feedback, settings.ENV_CONFIGURATION)


class FeedbackBase(models.Model):

    FEEDBACK_LOCAL_CHOICES = (
        (u'zh_CN', u'zh_CN'),
        (u'en_US', u'en_US'),
        (u'unknown', u'unknown'),
    )

    FEEDBACK_OS_CHOICES = (
        (u'Android', u'Android'),
        (u'iPad', u'iPad'),
        (u'iPhone', u'iPhone'),
        (u'unknown', u'unknown'),
        (u'PC', u'PC')
    )

    BOOLEAN_CHOICES = (
        (0, u'no'),
    )

    remote_address = models.CharField(max_length=16)
    name = models.CharField(max_length=50)
    contact_info = models.CharField(max_length=50)
    feedback_type = models.CharField(max_length=20)
    message = models.TextField(max_length=512)
    os = models.CharField(max_length=20, choices=FEEDBACK_OS_CHOICES)
    locale = models.CharField(max_length=10, choices=FEEDBACK_LOCAL_CHOICES)
    package = models.CharField(max_length=100)
    source = models.CharField(max_length=100)
    version = models.IntegerField('版本号')
    vname = models.CharField('版本名称', max_length=100, blank=True)
    time = models.DateTimeField()
    deleted = models.BooleanField(choices=BOOLEAN_CHOICES)

    def __unicode__(self):
        return self.message

    def content_info(self):
        result = {
            'remote_address': self.remote_address,
            'message': self.message,
            'contact_info': self.contact_info,
            'os': self.os,
            'locale': self.locale,
            'time': self.time,
            'name': self.name,
            'feedback_type': self.feedback_type,
            'deleted': self.deleted,
        }
        return result

    def get_content_list(self):
        feedback_list = [
            self.package, self.source, self.feedback_type, self.version, self.remote_address, self.message,
            self.contact_info, self.os, self.locale, self.time.strftime('%Y-%m-%d %H:%M:%S')]
        return feedback_list

    class Meta:
        abstract = True


class Feedback(FeedbackBase):

    class Meta:
        verbose_name = u"feedback_cn"
        verbose_name_plural = u"feedback_cn"


class Feedback_en(FeedbackBase):

    class Meta:
        verbose_name = u"feedback_en"
        verbose_name_plural = u"feedback_en"


class VersionCode(models.Model):
    product = models.CharField(max_length=100, verbose_name='包名', unique=True)
    vname = models.CharField('版本名称', max_length=200)
    version = models.IntegerField('版本号')

    def __unicode__(self):
        return '%s-%d' % (self.vname, self.version)

    class Meta:
        verbose_name = '版本名称和版本号映射'
        verbose_name_plural = '版本名称和版本号映射'
        app_label = 'feedback'

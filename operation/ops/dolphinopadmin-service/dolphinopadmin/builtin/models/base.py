#-*- coding:utf-8 -*-
from django.db import models
from dolphinopadmin.resource.models import Icon
from dolphinopadmin.base.models import BaseOnline, OTHER


class Bookmark_item(models.Model):
    title = models.CharField(max_length=100)
    url = models.URLField(max_length=2000, verify_exists=False)
    order = models.IntegerField()

    def content_dict(self):
        result_dict = {
            "order": self.order,
            "title": self.title,
            "url": self.url,
        }
        return result_dict

    def __unicode__(self):
        return "%s(%.50s)" % (self.title, self.url)

    class Meta:
        abstract = True


class WebzineColumn(models.Model):

    Local_CHOICES = (
        (u'zh-cn', u'zh-cn'),
        (u'en-us', u'en-us'),
    )

    Type_CHOICES = (
        (u'rss', u'rss'),
        (u'atom', u'atom'),
        (u'ftrss', u'ftrss'),
        (u'gallery', u'gallery'),
        (u'sinatuku', u'sinatuku'),
        (u'163pic', u'163pic'),
        (u'sohupic', u'sohupic'),
        (u'moko', u'moko'),
        (u'portal', u'portal'),
        (u'twitter', u'twitter'),
        (u'facebook', u'facebook'),
        (u'weibo', u'weibo'),
        (u'fgrss', u'fgrss'),
        (u'wbselection', u'wbselection'),
    )

    Columntype_CHOICES = (
        (u'html', u'html'),
        (u'text', u'text'),
        (u'summary', u'summary'),
    )

    Category_CHOICES = (
        (u'教育', u'教育'),
        (u'新闻', u'新闻'),
        (u'Science & Tech', u'Science & Tech'),
        (u'博客', u'博客'),
        (u'娱乐', u'娱乐'),
        (u'财经', u'财经'),
        (u'Top Media on Twitter', u'Top Media on Twitter'),
        (u'科技', u'科技'),
        (u'Top Twitter Users', u'Top Twitter Users'),
        (u'报刊', u'报刊'),
        (u'体育', u'体育'),
        (u'女性', u'女性'),
        (u'游戏', u'游戏'),
        (u'时尚', u'时尚'),
        (u'News', u'News'),
        (u'Family & Education', u'Family & Education'),
        (u'微媒体', u'微媒体'),
        (u'Sports', u'Sports'),
        (u'微博名人堂', u'微博名人堂'),
        (u'Health', u'Health'),
        (u'门户首页', u'门户首页'),
        (u'Business & Finance', u'Business & Finance'),
        (u'Politics', u'Politics'),
        (u'Entertainment', u'Entertainment'),
        (u'Travel', u'Travel'),
        (u'Fashion', u'Fashion'),
        (u'Science & Technology', u'Science & Technology'),
        (u'Businese & Finance', u'Businese & Finance'),
        (u'微媒体', u'微媒体'),
        (u'图片', u'图片'),
        (u'Photo & Art', u'Photo & Art'),
        (u'微博精选', u'微博精选'),
        (u'图趣', u'图趣'),
        (u'生活', u'生活'),
        (u'人文', u'人文'),
    )

    Category = models.CharField(max_length=100, choices=Category_CHOICES)
    Columntype = models.CharField(max_length=20, choices=Columntype_CHOICES)
    Description = models.TextField(max_length=512)
    Name = models.CharField(max_length=100)
    Type = models.CharField(max_length=20, choices=Type_CHOICES)
    Locale = models.CharField(max_length=10, choices=Local_CHOICES)
    Uri = models.URLField(verify_exists=False)
    Favicon = models.URLField(verify_exists=False)
    uID = models.BigIntegerField()

    def content_dict(self):
        result_dict = {
            "Category": self.Category,
            "ColumnType": self.Columntype,
            "Description": self.Description,
            "Locale": self.Locale,
            "Uri": self.Uri,
            "Fasion": self.Favicon,
            "Type": self.Type,
            "ID": self.uID,
            "Name": self.Name,
        }
        return result_dict

    def __unicode__(self):
        return "%s(%s)" % (self.Name, str(self.uID))

    class Meta:
        abstract = True


class SpeedDial(models.Model):
    title = models.CharField(max_length=100)
    url = models.CharField(max_length=512)
    favicon = models.URLField(verify_exists=False)
    thumbnail = models.CharField(max_length=2000, blank=True)
    color = models.CharField(blank=True, max_length=200)
    order = models.IntegerField()

    def content_dict(self):
        result_dict = {
            "favicon": self.favicon,
            "order": self.order,
            "title": self.title,
            "url": self.url,
            "thumbnail": self.thumbnail,
        }
        if self.color:
            result_dict['color'] = self.color
        return result_dict

    def __unicode__(self):
        return "%s(%.50s)" % (self.title, self.url)

    class Meta:
        abstract = True


class Webapp(models.Model):

    OS_CHOICES = (
        (u'android', u'android'),
        (u'ios', u'ios'),
    )

    BOOLEAN_CHOICES = (
        (1, u'yes'),
        (0, u'no'),
    )

    Local_CHOICES = (
        (u'zh_CN', u'zh_CN'),
        (u'0', u'N/A'),
    )

    category = models.CharField(max_length=100)
    description = models.TextField(max_length=512)
    enabled = models.IntegerField(choices=BOOLEAN_CHOICES)
    icon = models.URLField(verify_exists=False)
    local_id = models.IntegerField()
    locale = models.CharField(max_length=10, choices=Local_CHOICES)
    order = models.IntegerField()
    os = models.CharField(max_length=100, choices=OS_CHOICES)
    recommend = models.IntegerField(choices=BOOLEAN_CHOICES)
    title = models.CharField(max_length=100)
    url = models.URLField(verify_exists=False)

    def __unicode__(self):
        return self.title

    def content_dict(self):
        result_dict = {
            "category": self.category,
            "description": self.description,
            "enabled": self.enabled,
            "icon": self.icon,
            "locale": self.locale,
            "order": self.order,
            "os": self.os,
            "recommend": self.recommend,
            "title": self.title,
            "uri": self.url,
        }
        return result_dict

    class Meta:
        abstract = True


class promotionAction(models.Model):
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    icon = models.ForeignKey(Icon, related_name='+')
    action = models.CharField(max_length=200, help_text='url or dolphin url')

    def __unicode__(self):
        return self.name

    def content_dict(self, server):
        self.icon.upload_file(server)
        result_dict = {
            'icon': self.icon.get_url(server),
            'title': self.title,
            'action': self.action
        }

        return result_dict

    class Meta:
        verbose_name = 'promotion action'
        app_label = 'builtin'


class Builtin(BaseOnline):

    BOOLEAN_CHOICES = (
        (u'ture', u'ture'),
        (u'false', u'false'),
    )

    Local_CHOICES = (
        (u'zh_CN', u'zh_CN'),
        (u'en_US', u'en_US'),
        (u'0', u'N/A'),
    )

    locale = models.CharField(max_length=10, choices=Local_CHOICES)
    name = models.CharField(max_length=20)
    pname = models.CharField(max_length=100)
    source = models.CharField(max_length=20)
    force = models.CharField(max_length=10, choices=BOOLEAN_CHOICES)
    weibo = models.CharField(max_length=512, blank=True)
    cmcc = models.BooleanField(default=True, verbose_name='移动')
    unicom = models.BooleanField(default=True, verbose_name='联通')
    telecom = models.BooleanField(default=True, verbose_name='电信')
    other_operator = models.BooleanField(default=True, verbose_name='其它运营商')
    platform = models.CharField(max_length=200, blank=True)
    fish = models.CharField(max_length=200, blank=True)

    def __unicode__(self):
        return self.name

    def get_operators(self):
        operators = []
        if self.cmcc:
            operators.extend(['00', '02'])
        if self.unicom:
            operators.append('01')
        if self.telecom:
            operators.append('03')
        if self.other_operator:
            operators.append(OTHER)
        return operators

    def content_dict(self):
        result_dict = {
            "id": self.id,
            "locale": self.locale,
            "force": self.force,
            "name": self.name,
            "pname": self.pname,
            "source": self.source,
            "weibo": self.weibo,
            "operators": self.get_operators(),
        }
        return result_dict

    def get_m2m_field_list(self, field_cls, field_name):
        _list = []
        apps = field_cls.objects.filter(
            builtin__id=self.id).order_by('%s_order' % field_name)
        for item in apps:
            temp = getattr(item, field_name).content_dict()
            temp["order"] = getattr(item, '%s_order' % field_name)
            if field_name == 'wbz':  # webzine upper case first character
                temp["Order"] = getattr(item, '%s_order' % field_name)
            if field_name == 'spd':
                temp["position"] = item.position
                temp["permanent"] = item.permanent
            _list.append(temp)
        return _list

    class Meta:
        abstract = True

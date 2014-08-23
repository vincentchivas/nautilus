# encoding: utf-8
import datetime
from django.utils.translation import ugettext_lazy as _
from django.db import models
from dolphinopadmin.base.models import BaseOnline
from dolphinopadmin.base.utils import now, forever
#from dolphinopadmin.configure.models import Package, SourceSet
from dolphinopadmin.configure.models import Rule


class Publisher(models.Model):
    company = models.CharField(max_length=100)
    # 负责人
    person = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    adress = models.CharField(max_length=200)
    is_on = models.BooleanField(default=True)
    remark = models.TextField(blank=True)
    last_modify = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.company

    class Meta:
        verbose_name = u'发布商'
        verbose_name_plural = u'发布商'
        app_label = 'advert'


# 大分类, 广告id和客户端栏目id无关
class PositionCategory(models.Model):

    name = models.CharField(max_length=100, verbose_name="产品名称")
    cid = models.IntegerField(unique=True, verbose_name="产品ID")
    #bind_id = models.IntegerField()
    last_modify = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

    def content_dict(self):
        result_dict = {
            "cid": self.cid
        }
        return result_dict

    class Meta:
        verbose_name = u'产品'
        verbose_name_plural = u'产品'
        ordering = ['last_modify', ]
        app_label = 'advert'


# 小分类
class PositionItem(models.Model):

    name = models.CharField(max_length=100, verbose_name="广告位置")
    pid = models.IntegerField(unique=True, verbose_name="广告位置ID")
    last_modify = models.DateTimeField(auto_now=True)
    #bind_id = models.IntegerField()

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['last_modify', ]
        app_label = 'advert'


class Position(models.Model):
    category = models.ForeignKey(PositionCategory, verbose_name="产品名称")
    location = models.ForeignKey(PositionItem, verbose_name="广告位置")

    def __unicode__(self):
        return u"%s(%s)-%s(%s)" % (self.category, self.category.cid, self.location, self.location.pid)

    def content(self):
        return "%s-%s" % (self.category.cid, self.location.pid)

    class Meta:
        verbose_name = _('position')
        verbose_name_plural = _('position')
        app_label = 'advert'


class Cooperation(BaseOnline):

    name = models.CharField("运营标题", max_length=100)
    title = models.CharField("广告显示标题", max_length=100)
    url = models.CharField("url地址(http:// or https://)", max_length=500)
    # 图片链接
    images = models.TextField(blank=True, max_length=2000)
    # 有效期
    starttime = models.DateTimeField(verbose_name=_("valid time"))
    finishtime = models.DateTimeField(verbose_name=_("invalid time"))
    # 设置权重（以便控制客户端轮播广告的次数）
    weight = models.IntegerField("权重", default=1)
    # 运营商，可以多选
    #cmcc = models.BooleanField(default=True, verbose_name='移动')
    #unicom = models.BooleanField(default=True, verbose_name='联通')
    #telecom = models.BooleanField(default=True, verbose_name='电信')
    #other_operator = models.BooleanField(default=True, verbose_name='其它')
    # 渠道，推送渠道
    #sourceset =  models.ForeignKey(SourceSet)
    # 对包名进行订制推送
    #package = models.ForeignKey(Package)
    #min_version = models.IntegerField("最小版本")
    #max_version = models.IntegerField("最大版本")
    rule = models.ForeignKey(Rule, verbose_name=_('rule'), help_text=_(
        'this is a new column, old data may not match'))
    # 卖家
    publisher = models.ForeignKey(Publisher)
    position = models.ManyToManyField(Position, verbose_name="广告所属产品和位置")
    author = models.CharField(verbose_name="作者", max_length=200, blank=True)
    #summary = models.TextField(verbose_name = "摘要", max_length=1000, blank=True)
    #last_modify = models.DateTimeField(auto_now = True)

    def __unicode__(self):
        return self.title

    """
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
    """

    def get_positions(self):
        obj_list = self.position.all()
        pos_list = [obj.content() for obj in obj_list]
        return pos_list

    def content_dict(self):
        rule = self.rule.content_dict()
        rule.update({
            "start_time": self.starttime + datetime.timedelta(hours=-8) if self.starttime else now(),
            "end_time": self.finishtime + datetime.timedelta(hours=-8) if self.finishtime else forever(),
        })
        result_dict = {
            "id": self.id,
            "title": self.title,
            "link": self.url,
            "weight": self.weight,
            "position": self.get_positions(),
            #"sources": self.sourceset.content_dict(),
            #"operators": self.get_operators(),
            #"valid_time": int(time.mktime(self.starttime.timetuple())),
            #"invalid_time": int(time.mktime(self.finishtime.timetuple())),
            "images": self.images.split(',') if self.images else [],
            "_rule": rule,
            #"package": self.package.uid,
            #"min_version": self.min_version,
            #"max_version": self.max_version,
        }
        if self.author:
            result_dict['author'] = self.author
        # if self.summary:
        #    result_dict['summary'] = self.summary
        return result_dict

    class Meta:
        app_label = 'advert'

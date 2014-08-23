# -*- coding:utf-8 -*-
from django.db import models
from base import *
from dolphinopadmin.base.admin import EnhancedAdminInline
from dolphinopadmin.treasure.models import Group

_PLATFORM = 'iOS'
_FISH = 'tunny'

OS_CHOICES = (
    (u'iPhone', u'iPhone'),
    (u'iPad', u'iPad'),
)


class iOS_Bookmark_item(Bookmark_item):

    class Meta:
        verbose_name = u'iOS 书签'
        verbose_name_plural = u'iOS 书签'
        app_label = 'builtin'


class iOS_WebzineColumn(WebzineColumn):

    class Meta:
        verbose_name = u'iOS 海豚阅读'
        verbose_name_plural = u'iOS 海豚阅读'
        app_label = 'builtin'


class iOS_SpeedDial(SpeedDial):

    class Meta:
        verbose_name = u'iOS 快速访问'
        verbose_name_plural = u'iOS 快速访问'
        app_label = 'builtin'


class iOS_Webapp(Webapp):

    class Meta:
        verbose_name = u'iOS 网页应用'
        verbose_name_plural = u'iOS 网页应用'
        app_label = 'builtin'


class iOS_Builtin(Builtin):

    os = models.CharField(max_length=50, choices=OS_CHOICES)
    speedDials = models.ManyToManyField(
        iOS_SpeedDial, through='iOS_Spd_built_ship')
    bookmarks = models.ManyToManyField(
        iOS_Bookmark_item, through='iOS_Bkm_built_ship')
    webapps = models.ManyToManyField(iOS_Webapp, through='iOS_Wba_built_ship')
    webzine = models.ManyToManyField(
        iOS_WebzineColumn, through='iOS_Wbz_built_ship')
    treasure = models.ForeignKey(Group, blank=True)

    class Meta:
        verbose_name = u'iOS 预置内容'
        verbose_name_plural = u'iOS 预置内容'
        app_label = 'builtin'

    def content_dict(self):
        result_dict = super(iOS_Builtin, self).content_dict()
        result_dict['platform'] = self.platform or _PLATFORM
        result_dict['fish'] = self.fish or _FISH
        result_dict['os'] = self.os
        result_dict['speedDials'] = self.get_m2m_field_list(
            iOS_Spd_built_ship, 'spd')
        result_dict['bookmarks'] = self.get_m2m_field_list(
            iOS_Bkm_built_ship, 'bkm')
        result_dict['webapps'] = self.get_m2m_field_list(
            iOS_Wba_built_ship, 'wba')
        result_dict['webzineColumns'] = self.get_m2m_field_list(
            iOS_Wbz_built_ship, 'wbz')
        return result_dict

    def save(self, *args, **kwargs):
        if not self.id:
            self.platform = _PLATFORM
            self.fish = _FISH
        super(iOS_Builtin, self).save(*args, **kwargs)


class iOS_Spd_built_ship(models.Model):
    POSITION_CHOICES = (
        (0, 0),
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
        (7, 7),
        (-1, -1),
    )
    spd = models.ForeignKey(iOS_SpeedDial, verbose_name=u"speedDial名")
    builtin = models.ForeignKey(iOS_Builtin, verbose_name=u"built-in名")
    spd_order = models.IntegerField(verbose_name=u"此speedDial项在built-in中的顺序")
    position = models.IntegerField(default=-1, choices=POSITION_CHOICES)
    permanent = models.IntegerField(default=-1, choices=POSITION_CHOICES)

    def __str__(self):
        return "%s(%s)" % (self.spd.title.encode('utf-8'), self.spd.url.encode('utf-8'))

    class Meta:
        verbose_name = u"iOS built_in所关联的speedDial"
        verbose_name_plural = u"iOS built_in所关联的speedDial"
        app_label = 'builtin'


class iOS_Wba_built_ship(models.Model):
    wba = models.ForeignKey(iOS_Webapp, verbose_name=u"webapp名")
    builtin = models.ForeignKey(iOS_Builtin, verbose_name=u"built-in名")
    wba_order = models.IntegerField(verbose_name=u"此webapp在built中的顺序")

    def __str__(self):
        return "built_in%d(%s)" % (self.builtin.id, self.wba.title.encode('utf-8'))

    class Meta:
        verbose_name = u"iOS built_in所关联的webapps"
        verbose_name_plural = u"iOS built_in所关联的webapps"
        app_label = 'builtin'


class iOS_Bkm_built_ship(models.Model):
    bkm = models.ForeignKey(iOS_Bookmark_item, verbose_name=u"bookmark名")
    builtin = models.ForeignKey(iOS_Builtin, verbose_name=u"built-in名")
    bkm_order = models.IntegerField(verbose_name=u"此bookmark在built-in中的顺序")

    def __str__(self):
        return "%s(%s)" % (self.bkm.title.encode('utf-8'), self.bkm.url.encode('utf-8'))

    class Meta:
        verbose_name = u"iOS built_in所关联的bookmarks"
        verbose_name_plural = u"iOS built_in所关联的bookmarks"
        app_label = 'builtin'


class iOS_Wbz_built_ship(models.Model):
    wbz = models.ForeignKey(iOS_WebzineColumn, verbose_name=u"webzine名")
    builtin = models.ForeignKey(iOS_Builtin, verbose_name=u"built-in名")
    wbz_order = models.IntegerField(verbose_name=u"此webzine在built-in中的顺序")

    def __str__(self):
        return "%s(%s)" % (self.wbz.Name.encode('utf-8'), self.wbz.uID)

    class Meta:
        verbose_name = u"iOS built_in所关联的webzine"
        verbose_name_plural = u"iOS built_in所关联的webzine"
        app_label = 'builtin'


class iOS_Wbz_built_shipInline(EnhancedAdminInline):
    model = iOS_Wbz_built_ship
    raw_id_fields = ['wbz']
    extra = 1


class iOS_Bkm_built_shipInline(EnhancedAdminInline):
    model = iOS_Bkm_built_ship
    raw_id_fields = ['bkm']
    extra = 1


class iOS_Spd_built_shipInline(EnhancedAdminInline):
    model = iOS_Spd_built_ship
    raw_id_fields = ['spd']
    extra = 1


class iOS_Wba_built_shipInline(EnhancedAdminInline):
    model = iOS_Wba_built_ship
    raw_id_fields = ['wba']
    extra = 1

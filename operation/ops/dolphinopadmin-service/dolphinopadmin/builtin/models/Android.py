# -*- coding:utf-8 -*-
from django.db import models
from base import *
from dolphinopadmin.base.admin import EnhancedAdminInline
from dolphinopadmin.treasure.models import Group

_PLATFORM = 'Android'
_FISH = 'tunny'

OS_CHOICES = (
    (u'android', u'android'),
    (u'androidpad', u'androidpad')
)


class Android_Bookmark_item(Bookmark_item):

    class Meta:
        verbose_name = u'Android 书签'
        verbose_name_plural = u'Android 书签'
        app_label = 'builtin'


class Android_WebzineColumn(WebzineColumn):

    class Meta:
        verbose_name = u'Android 海豚阅读'
        verbose_name_plural = u'Android 海豚阅读'
        app_label = 'builtin'


class Android_SpeedDial(SpeedDial):

    class Meta:
        verbose_name = u'Android 快速访问'
        verbose_name_plural = u'Android 快速访问'
        app_label = 'builtin'


class Android_Webapp(Webapp):

    class Meta:
        verbose_name = u'Android 网页应用'
        verbose_name_plural = u'Android 网页应用'
        app_label = 'builtin'


class Android_Builtin(Builtin):

    os = models.CharField(max_length=50, choices=OS_CHOICES)
    is_promotion = models.BooleanField(default=False)
    promotion_flag = models.CharField(
        max_length=100, blank=True, verbose_name='promotion flag')
    sub_flag = models.CharField(
        max_length=100, blank=True, verbose_name='promotion subflag')
    preset_url = models.CharField(
        max_length='150', blank=True, help_text='url or dolphin url')
    speedDials = models.ManyToManyField(
        Android_SpeedDial, through='Android_Spd_built_ship')
    bookmarks = models.ManyToManyField(
        Android_Bookmark_item, through='Android_Bkm_built_ship')
    webapps = models.ManyToManyField(
        Android_Webapp, through='Android_Wba_built_ship')
    webzine = models.ManyToManyField(
        Android_WebzineColumn, through='Android_Wbz_built_ship')
    treasure = models.ForeignKey(Group)
    promotion = models.ForeignKey(
        promotionAction, blank=True, null=True, verbose_name='promotion action(option)')

    class Meta:
        verbose_name = u'Android 预置内容'
        verbose_name_plural = u'Android 预置内容'
        app_label = 'builtin'

    def content_dict(self, server):
        result_dict = super(Android_Builtin, self).content_dict()
        if self.is_promotion and self.promotion and self.preset_url:
            result_dict.update({
                'is_promotion': True if self.promotion_flag and self.sub_flag else False,
                'promotion_flag': '%s_%s' % (self.promotion_flag, self.sub_flag),
                'preset_url': self.preset_url,
                'promotion': self.promotion.content_dict(server)
            })

        result_dict.update({
            'platform': self.platform or _PLATFORM,
            'fish': self.fish or _FISH,
            'os': self.os,
            'speedDials': self.get_m2m_field_list(Android_Spd_built_ship, 'spd'),
            'bookmarks': self.get_m2m_field_list(Android_Bkm_built_ship, 'bkm'),
            'webapps': self.get_m2m_field_list(Android_Wba_built_ship, 'wba'),
            'webzineColumns': self.get_m2m_field_list(Android_Wbz_built_ship, 'wbz'),
            'treasure_favs': self.treasure.content_dict(pic=False)
        })
        return result_dict

    def save(self, *args, **kwargs):
        self.platform = _PLATFORM
        self.fish = _FISH
        super(Android_Builtin, self).save(*args, **kwargs)


class Android_Spd_built_ship(models.Model):
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
    spd = models.ForeignKey(Android_SpeedDial, verbose_name=u"speedDial名")
    builtin = models.ForeignKey(Android_Builtin, verbose_name=u"built-in名")
    spd_order = models.IntegerField(verbose_name=u"此speedDial项在built-in中的顺序")
    position = models.IntegerField(default=-1, choices=POSITION_CHOICES)
    permanent = models.IntegerField(default=-1, choices=POSITION_CHOICES)

    def __str__(self):
        return "%s(%s)" % (self.spd.title.encode('utf-8'), self.spd.url.encode('utf-8'))

    class Meta:
        verbose_name = u"Android built_in所关联的speedDial"
        verbose_name_plural = u"Android built_in所关联的speedDial"
        app_label = 'builtin'


class Android_Wba_built_ship(models.Model):
    wba = models.ForeignKey(Android_Webapp, verbose_name=u"webapp名")
    builtin = models.ForeignKey(Android_Builtin, verbose_name=u"built-in名")
    wba_order = models.IntegerField(verbose_name=u"此webapp在built中的顺序")

    def __str__(self):
        return "built_in%d(%s)" % (self.builtin.id, self.wba.title.encode('utf-8'))

    class Meta:
        verbose_name = u"Android built_in所关联的webapps"
        verbose_name_plural = u"Android built_in所关联的webapps"
        app_label = 'builtin'


class Android_Bkm_built_ship(models.Model):
    bkm = models.ForeignKey(
        Android_Bookmark_item, verbose_name=u"bookmark名")
    builtin = models.ForeignKey(Android_Builtin, verbose_name=u"built-in名")
    bkm_order = models.IntegerField(verbose_name=u"此bookmark在built-in中的顺序")

    def __str__(self):
        return "%s(%s)" % (self.bkm.title.encode('utf-8'), self.bkm.url.encode('utf-8'))

    class Meta:
        verbose_name = u"Android built_in所关联的bookmarks"
        verbose_name_plural = u"Android built_in所关联的bookmarks"
        app_label = 'builtin'


class Android_Wbz_built_ship(models.Model):
    wbz = models.ForeignKey(Android_WebzineColumn, verbose_name=u"webzine名")
    builtin = models.ForeignKey(Android_Builtin, verbose_name=u"built-in名")
    wbz_order = models.IntegerField(verbose_name=u"此webzine在built-in中的顺序")

    def __str__(self):
        return "%s(%s)" % (self.wbz.Name.encode('utf-8'), self.wbz.uID)

    class Meta:
        verbose_name = u"Android built_in所关联的webzine"
        verbose_name_plural = u"Android built_in所关联的webzine"
        app_label = 'builtin'


class Android_Wbz_built_shipInline(EnhancedAdminInline):
    model = Android_Wbz_built_ship
    raw_id_fields = ['wbz']
    extra = 1


class Android_Bkm_built_shipInline(EnhancedAdminInline):
    model = Android_Bkm_built_ship
    raw_id_fields = ['bkm']
    extra = 1


class Android_Spd_built_shipInline(EnhancedAdminInline):
    model = Android_Spd_built_ship
    raw_id_fields = ['spd']
    extra = 1


class Android_Wba_built_shipInline(EnhancedAdminInline):
    model = Android_Wba_built_ship
    raw_id_fields = ['wba']
    extra = 1

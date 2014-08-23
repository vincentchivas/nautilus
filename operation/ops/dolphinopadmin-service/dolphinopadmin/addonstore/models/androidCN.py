# -*- coding:utf-8 -*-
import time
import logging
from datetime import datetime
from django.db import models
from dolphinopadmin.base.admin import EnhancedAdminInline
from base import \
    Subject, Category, Application, Feature, Hoting, \
    ScreenShot

_PLATFORM = 'Android_CN'

_TIME_ZONE = 0

logger = logging.getLogger('dolphinopadmin.admin')


def getsub_position():
    categories = AndroidCNSubject.objects.order_by('-position')
    max_pos = 1 if len(categories) == 0 else \
        categories[0].position + 1
    return max_pos


def getcate_position():
    categories = AndroidCNCategory.objects.order_by('-position')
    max_pos = 1 if len(categories) == 0 else \
        categories[0].position + 1
    return max_pos


def getapp_position():
    applications = AndroidCNApplication.objects.order_by('-position')
    max_pos = 1 if len(applications) == 0 else \
        applications[0].position + 1
    return max_pos


def getfea_position():
    features = AndroidCNFeature.objects.order_by('-position')
    max_pos = 1 if len(features) == 0 else \
        features[0].position + 1
    return max_pos


def gettre_position():
    trends = AndroidCNHoting.objects.order_by('-position')
    max_pos = 1 if len(trends) == 0 else \
        trends[0].position + 1
    return max_pos


class AndroidCNScreenShot(ScreenShot):

    def save(self, *args, **kwargs):
        if not self.id:
            self.platform = _PLATFORM
        super(AndroidCNScreenShot, self).save(*args, **kwargs)

    class Meta:
        verbose_name = u"Android CN 截图"
        verbose_name_plural = u"Android CN 截图"
        app_label = 'addonstore'


class AndroidCNCategory(Category):

    online_time = models.DateTimeField(
        default=datetime.now, verbose_name=u"上线时间")
    offline = models.BooleanField(default=False, verbose_name=u"定时下线")
    offline_time = models.DateTimeField(
        default=datetime.now, verbose_name=u"下线时间")
    position = models.IntegerField(
        default=getcate_position, blank=True, verbose_name=u"位置")

    class Meta:
        verbose_name = u'Android CN 分类'
        verbose_name_plural = u'Android CN 分类'
        app_label = 'addonstore'

    def content_dict(self):
        result_dict = super(AndroidCNCategory, self).content_dict()
        result_dict["online_time"] = time.mktime(
            self.online_time.timetuple()) + _TIME_ZONE
        result_dict["offline"] = self.offline
        result_dict["offline_time"] = time.mktime(
            self.offline_time.timetuple()) + _TIME_ZONE
        result_dict["position"] = self.position
        return result_dict

    def save(self, *args, **kwargs):
        if not self.id:
            self.position = getcate_position()
            self.platform = _PLATFORM
        super(AndroidCNCategory, self).save(*args, **kwargs)


class AndroidCNApplication(Application):

    category = models.ForeignKey(AndroidCNCategory, verbose_name=u"分类")
    online_time = models.DateTimeField(
        default=datetime.now, verbose_name=u"上线时间")
    offline = models.BooleanField(default=False, verbose_name=u"定时下线")
    offline_time = models.DateTimeField(
        default=datetime.now, verbose_name=u"下线时间")
    position = models.IntegerField(
        default=getapp_position, blank=True, verbose_name=u"位置")
    top_ranking = models.BooleanField(default=False, verbose_name=u"排行置顶")
    ranking_position = models.IntegerField(
        blank=True, default=0, verbose_name=u"排行位置")
    top_new = models.BooleanField(default=False, verbose_name=u"最新上架置顶")
    new_position = models.IntegerField(
        blank=True, default=0, verbose_name=u"最新上架位置")
    top_web = models.BooleanField(default=False, verbose_name=u"网页应用置顶")
    web_position = models.IntegerField(
        blank=True, default=0, verbose_name=u"网页应用位置")
    screenshots = models.ManyToManyField(AndroidCNScreenShot,
                                         through='AndroidCNAppPicShip', verbose_name=u"截图")

    def get_screenshots(self):
        _list = []
        apps = AndroidCNAppPicShip.objects.filter(
            app__id=self.id).order_by("pic_order")
        for item in apps:
            temp = item.pic.content_dict()
            temp["order"] = item.pic_order
            _list.append(temp)
        return _list

    def content_dict(self):
        result_dict = super(AndroidCNApplication, self).content_dict()
        result_dict['category'] = self.category.id
        result_dict["online_time"] = time.mktime(
            self.online_time.timetuple()) + _TIME_ZONE
        result_dict["offline"] = self.offline
        result_dict["offline_time"] = time.mktime(
            self.offline_time.timetuple()) + _TIME_ZONE
        result_dict["position"] = self.position
        result_dict["top_ranking"] = self.top_ranking
        result_dict["ranking_position"] = self.ranking_position
        result_dict["top_new"] = self.top_new
        result_dict["new_position"] = self.new_position
        result_dict["top_web"] = self.top_web
        result_dict["web_position"] = self.web_position
        result_dict['screenshots'] = self.get_screenshots()
        return result_dict

    class Meta:
        verbose_name = u'Android CN 应用'
        verbose_name_plural = u'Android CN 应用'
        app_label = 'addonstore'

    def save(self, *args, **kwargs):
        if not self.id:
            self.position = getapp_position()
            self.platform = _PLATFORM
        super(AndroidCNApplication, self).save(*args, **kwargs)


class AndroidCNSubject(Subject):

    online_time = models.DateTimeField(
        default=datetime.now, verbose_name=u"上线时间")
    offline = models.BooleanField(default=False, verbose_name=u"定时下线")
    offline_time = models.DateTimeField(
        default=datetime.now, verbose_name=u"下线时间")
    position = models.IntegerField(
        default=getsub_position, blank=True, verbose_name=u"位置")
    applications = models.ManyToManyField(
        AndroidCNApplication, through='AndroidCNSubjectAppsShip', verbose_name=u"应用")

    def get_applications(self):
        app_list = []
        apps = AndroidCNSubjectAppsShip.objects.filter(
            subject__id=self.id).order_by('app_order')
        for item in apps:
            app_dict = item.app.content_dict()
            app_dict['app_order'] = item.app_order
            app_list.append(app_dict)
        return app_list

    def content_dict(self):
        result_dict = super(AndroidCNSubject, self).content_dict()
        result_dict["online_time"] = time.mktime(
            self.online_time.timetuple()) + _TIME_ZONE
        result_dict["offline"] = self.offline
        result_dict["offline_time"] = time.mktime(
            self.offline_time.timetuple()) + _TIME_ZONE
        result_dict["position"] = self.position
        result_dict['application'] = self.get_applications()
        return result_dict

    class Meta:
        verbose_name = u'Android CN 专题'
        verbose_name_plural = u'Android CN 专题'
        app_label = 'addonstore'

    def save(self, *args, **kwargs):
        if not self.id:
            self.position = getcate_position()
            self.platform = _PLATFORM
        super(AndroidCNSubject, self).save(*args, **kwargs)


class AndroidCNFeature(Feature):

    online_time = models.DateTimeField(
        default=datetime.now, verbose_name=u"上线时间")
    offline = models.BooleanField(default=False, verbose_name=u"定时下线")
    offline_time = models.DateTimeField(
        default=datetime.now, verbose_name=u"下线时间")
    position = models.IntegerField(
        default=getfea_position, blank=True, verbose_name=u"位置")
    application = models.ForeignKey(AndroidCNApplication, verbose_name=u"应用")

    def content_dict(self):
        result_dict = super(AndroidCNFeature, self).content_dict()
        result_dict["online_time"] = time.mktime(
            self.online_time.timetuple()) + _TIME_ZONE
        result_dict["offline"] = self.offline
        result_dict["offline_time"] = time.mktime(
            self.offline_time.timetuple()) + _TIME_ZONE
        result_dict["position"] = self.position
        result_dict["content"] = self.application.content_dict()
        return result_dict

    class Meta:
        verbose_name = u'Android CN 推荐'
        verbose_name_plural = u'Android CN 推荐'
        app_label = 'addonstore'

    def save(self, *args, **kwargs):
        if not self.id:
            self.position = getfea_position()
            self.platform = _PLATFORM
        super(AndroidCNFeature, self).save(*args, **kwargs)


class AndroidCNHoting(Hoting):

    online_time = models.DateTimeField(
        default=datetime.now, verbose_name=u"上线时间")
    offline = models.BooleanField(default=False, verbose_name=u"定时下线")
    offline_time = models.DateTimeField(
        default=datetime.now, verbose_name=u"下线时间")
    position = models.IntegerField(
        default=gettre_position, blank=True, verbose_name=u"位置")
    application = models.ForeignKey(
        AndroidCNApplication, unique=True, verbose_name=u"应用")

    def content_dict(self):
        result_dict = super(AndroidCNHoting, self).content_dict()
        result_dict["online_time"] = time.mktime(
            self.online_time.timetuple()) + _TIME_ZONE
        result_dict["offline"] = self.offline
        result_dict["offline_time"] = time.mktime(
            self.offline_time.timetuple()) + _TIME_ZONE
        result_dict["position"] = self.position
        result_dict['application'] = self.application.content_dict()
        return result_dict

    class Meta:
        verbose_name = u'Android CN 热门应用'
        verbose_name_plural = u'Android CN 热门应用'
        app_label = 'addonstore'

    def save(self, *args, **kwargs):
        if not self.id:
            self.position = gettre_position()
            self.platform = _PLATFORM
        super(AndroidCNHoting, self).save(*args, **kwargs)


class AndroidCNAppPicShip(models.Model):
    pic = models.ForeignKey(AndroidCNScreenShot, verbose_name=u"截图")
    app = models.ForeignKey(AndroidCNApplication, verbose_name=u"应用")
    pic_order = models.IntegerField(verbose_name=u"截图排序")

    class Meta:
        app_label = 'addonstore'


class AndroidCNAppPicShipInline(EnhancedAdminInline):
    model = AndroidCNAppPicShip
    extra = 1


class AndroidCNSubjectAppsShip(models.Model):
    subject = models.ForeignKey(AndroidCNSubject, verbose_name=u"专题")
    app = models.ForeignKey(AndroidCNApplication, verbose_name=u"应用")
    app_order = models.IntegerField(default=1, verbose_name=u"应用排序")

    class Meta:
        verbose_name = u'专题应用'
        verbose_name_plural = u'专题应用'
        app_label = 'addonstore'

    def save(self, *args, **kwargs):
        super(AndroidCNSubjectAppsShip, self).save(*args, **kwargs)


class AndroidCNSubjectAppsShipInline(EnhancedAdminInline):
    model = AndroidCNSubjectAppsShip
    extra = 1

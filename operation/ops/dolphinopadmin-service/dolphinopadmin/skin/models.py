#! /usr/bin/python
# -*- coding:utf-8 -*-
# Author: Qingtian Gan

import time
import os
import subprocess
import re
import logging
from xml.dom import minidom

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from dolphinopadmin.configure.models import Rule
from dolphinopadmin.resource.models import Icon
from dolphinopadmin.base.content import ALL_FLAG, PROMOTE_CHOICES, TYPE_CHOICES,  \
    TAG_CHOICES, BANNER_TYPES_CHOICES
from dolphinopadmin.remotedb.skin import config as config_skin
from dolphinopadmin.base.base_model import BaseStatus
from dolphinopadmin.utils import scp


logger = logging.getLogger('dolphinopadmin.admin')

config_skin(servers=settings.ENV_CONFIGURATION)
SERVERS = settings.ENV_CONFIGURATION
DOWN_SERVERS = {
    'local': settings.ENV_CONFIGURATION['local']['domain'],
    'ec2': 'opsen.dolphin-browser.com',
    'china': 'download.dolphin-browser.cn',
}

MEDIA_ROOT = settings.MEDIA_ROOT
SKIN_PATH = 'skin/file'
SKIN_FILE = 'skin'


class BaseFilter(BaseStatus):
    platform = models.CharField(max_length=100, editable=False)

    def save(self, *args, **kwargs):
        self.platform = self.__class__.filters['platform']
        super(BaseFilter, self).save(*args, **kwargs)

    class Meta:
        abstract = True

# 需要上传到服务器上得数据，添加继承BaseStatus


class SkinCommon(BaseFilter):
    uid = models.CharField(
        max_length=200, editable=False, verbose_name=_("UID"))
    name = models.CharField(max_length=200, verbose_name=_("Name"))
    compatible_version = models.IntegerField(
        editable=False, default=1, verbose_name=_("Compatible Version"))
    downloads = models.IntegerField(
        default=0, help_text=_("any number large than 0 mean manual set"), verbose_name=_("Downloads"))
    download_url = models.CharField(
        max_length=2000, blank=True, editable=False, verbose_name=_("Download URL"))
    version = models.IntegerField(
        editable=False, default=1, verbose_name=_("Version"))
    badge = models.IntegerField(
        default=0, choices=PROMOTE_CHOICES, verbose_name=_("Badge"))
    promote = models.BooleanField(default=False, verbose_name=_("Promote"))
    description = models.TextField(
        max_length=2000, verbose_name=_("Description"))
    update_time = models.CharField(
        max_length=200, verbose_name=_("Update Time"))
    size = models.CharField(
        max_length=50, help_text=_('unit is require!'), verbose_name=_("Size"))
    theme_type = models.CharField(
        max_length=200, default='skin', choices=TYPE_CHOICES, verbose_name=_("Theme Type"))
    # last_modified = models.DateTimeField(auto_now=True, verbose_name=_("Last Modified"))
    upload_user = models.CharField(
        max_length=100, blank=True, verbose_name=_("Upload User"))
    tag = models.CharField(max_length=20, choices=TAG_CHOICES,
                           default='unknown', verbose_name=_("Tag"))
    order = models.IntegerField(verbose_name=_("Order"))
    update_file = models.FileField(upload_to=SKIN_FILE,
                                   help_text=_('id and version will be set when save automally'), verbose_name=_("Update File"))
    rule = models.ForeignKey(Rule, related_name='+', verbose_name=_("Rule"))
    client_icon = models.ForeignKey(
        Icon, blank=True, null=True, related_name='+',
        help_text=u'推荐字体客户端显示icon', verbose_name=_("Client Icon"))
    icon = models.ForeignKey(Icon, related_name='+', verbose_name=_("Icon"))

    # this attribute is out of use
    # screenshots = models.ManyToManyField(AndroidScreenshot, through='AndroidSkinScreenshotShip')

    style = models.CharField(
        max_length=100, blank=True, verbose_name=_("Style"))
    color = models.CharField(
        max_length=100, blank=True, verbose_name=_("Color"))
    # add for filters

    def __unicode__(self):
        return self.name

    def save(self, form=None, request=None, *args, **kwargs):
        super(SkinCommon, self).save(*args, **kwargs)
        if form is None:
            return None
        logger.info('run here')
        try:
            special_confs = {
                'font': 'font.config',
            }
            current_file = os.path.join(MEDIA_ROOT, self.update_file.name)
            skin_path = os.path.join(MEDIA_ROOT, SKIN_PATH)
            logger.info(current_file)
            command = "unzip -o %s -d %s" % (current_file, skin_path)
            logger.info(command)
            result = subprocess.call(command, shell=True)
            logger.info(result)
            xml_file = os.path.join(skin_path, '%s' % special_confs[
                                    self.theme_type] if self.theme_type in special_confs else 'theme.config')
            logger.info(xml_file)
            try:
                xml_dom = minidom.parse(xml_file)
                os.remove(xml_file)
                # logger.info(xml_dom.toxml())
            except Exception, e:
                logger.info(e)
                raise ValueError(u'%s包内缺失配置文件' % self.update_file.name)
            tmp_doms = xml_dom.getElementsByTagName('id')
            if not tmp_doms:
                raise ValueError(u'%s包内的配置文件缺失Uid' % self.update_file.name)
            self.uid = tmp_doms[0].firstChild.wholeText
            if self.theme_type == 'skin':
                try:
                    self.__dict__.update({
                        'compatible_version': xml_dom.getElementsByTagName('compatibility')[0].firstChild.wholeText,
                        'version': xml_dom.getElementsByTagName('version')[0].firstChild.wholeText,
                    })
                except Exception, e:
                    logger.exception(e)
                    raise ValueError(
                        u'%s包内version及compatible_version不全或格式错误，请检查' %
                        self.update_file.name)
                ukey = '%s_%s' % (self.uid, self.compatible_version)
                skins = form.model.objects.all()
                skin_keys = ['%s_%s' % (item.uid, item.compatible_version)
                             for item in skins]
                if ukey in skin_keys:
                    raise ValueError(u'uid及compatible_version重复')
                down_url = xml_dom.getElementsByTagName('url')
                if down_url:
                    self.download_url = down_url[0].firstChild.wholeText
            else:
                try:
                    self.__dict__.update({
                        'compatible_version': xml_dom.getElementsByTagName('compatibility')[0].firstChild.wholeText,
                    })
                except:
                    self.__dict__.update({
                        'compatible_version': 1,
                        'version': 1,
                    })
            self.save()
            return None
        except Exception, e:
            logger.exception(e)
            return e

    def file_upload(self, server):
        file_obj = self.update_file
        local_base = settings.MEDIA_ROOT
        local = os.path.join(local_base, file_obj.name)
        remote_base = '/home/static/resources'
        remote = os.path.join(remote_base, file_obj.name)
        result = scp.scp(SERVERS[server]['statics'], 'static',
                         '/var/app/data/dolphinopadmin-service/static.pem', local, remote)
        if not result:
            raise ValueError(u'上传文件%s失败' % file_obj)
        url = 'http://%s/resources/%s' % (DOWN_SERVERS[server], file_obj.name)
        self.download_url = url
        setattr(self, '%s_url' % server, url)
        self.save()

    def get_screenshots(self, server):
        obj_list = []
        items = self.skin_skincommonscreenshotship_set.all().order_by('order')
        for item in items:
            dic = item.screenshot.content_dict(server)
            dic['order'] = item.order
            obj_list.append(dic)
        return obj_list

    def content_dict(self, server, is_del=False):
        if is_del:
            return {
                "id": self.id,
            }
        if self.__dict__.get('is_upload_%s' % server):
            raise ValueError(u"请先从%s删除，再重复上传" % server)

        result_dict = {
            "id": self.id,
            "uid": self.uid,
            "name": self.name,
            "c_version": self.compatible_version,
            "version": self.version,
            "badge": self.badge,
            "promote": self.promote,
            "description": self.description,
            "update_time": self.update_time,
            "theme_type": self.theme_type,
            "last_modified": int(time.time()),
            "uploader": self.upload_user,
            "tag": self.tag,
            "order": self.order,
            "downloads": self.downloads,
            "size": self.size
        }
        if self.download_url and re.match(r'^market://', self.download_url):
            result_dict['download_url'] = self.download_url
        else:
            self.file_upload(server)
            result_dict['download_url'] = self.download_url

        if self.theme_type == 'font':
            assert not self.promote or self.client_icon, u'推荐字体必须选择client icon'

        if self.client_icon:
            self.client_icon.upload_file(server)
            result_dict['client_icon'] = self.client_icon.get_url(server)

        self.icon.upload_file(server)
        rules = self.rule.content_dict()
        result_dict.update({
            'package': rules['packages'],
            'sources': rules['sources'],
            'locales':rules['locales']['include'],
            'icon': self.icon.get_url(server),
            'screenshots': self.get_screenshots(server),
            'style': self.style,
            'color': self.color,
            "_rule": rules,
        })
        return result_dict

    class Meta:
        verbose_name = _('Skin')
        verbose_name_plural = _('Skin')
        app_label = 'skin'


class Screenshot(models.Model):
    name = models.CharField(max_length=200, verbose_name=_("Name"))
    # remain but out of use
    url = models.CharField(max_length=2000, blank=True, editable=False,
                           null=True, verbose_name=_("URL"), help_text=u'新版本中请请废弃此字段，改用预览图字段')
    pic_file = models.ForeignKey(Icon, verbose_name=_("Screenshot File"))
    platform = models.CharField(max_length=100, editable=False)

    def save(self, *args, **kwargs):
        self.platform = self.__class__.filters['platform']
        super(Screenshot, self).save(*args, **kwargs)

    def content_dict(self, server):
        try:
            self.pic_file.upload_file(server)
            result_dict = {
                "url": self.pic_file.get_url(server)
            }
        except:
            result_dict = {
                "url": self.url
            }
        return result_dict

    def display_screenshot(self):
        try:
            return self.pic_file.icon_file()
        except:
            return self.url
    display_screenshot.verbose_name = _("Screenshot File")
    display_screenshot.verbose_name_plural = _("Screenshot File")
    display_screenshot.allow_tags = True

    def __unicode__(self):
        return self.name or self.pic_file[-80:]

    class Meta:
        app_label = 'skin'
        verbose_name = _("Screenshot")
        verbose_name_plural = _("Screenshot")


class SubjectSkin(BaseFilter):
    desc = models.CharField(max_length=200, blank=True,
                            verbose_name=_("Description"))
    order = models.IntegerField(verbose_name=_("Order"))
    rule = models.ForeignKey(Rule, related_name='+', verbose_name=_("Rule"))
    icon = models.ForeignKey(Icon, related_name='+', verbose_name=_("Icon"))

    def get_items(self, server):
        obj_list = []
        need_keys = ('id', 'uid', 'name', 'theme_type', 'download_url',
                     'tag', 'size')
        items = self.skin_subjectskinskincommonship_set.all().order_by('order')
        for item in items:
            # item = SubjectItemSkin.objects.get(id=item_s.subjectitemskin_id)
            print item.__dict__
            item_dict = {
                'desc': item.desc,
                'icon': item.skincommon.icon.get_url(server)
            }
            try:
                skin_dict = item.skincommon.content_dict(server)
            except:
                skin_dict = item.skincommon.__dict__
            for key in need_keys:
                item_dict[key] = skin_dict.get(key)
            obj_list.append(item_dict)

        return obj_list

    def get_compatible_version(self):
        # subject.c_version: 0 means compatible for all, or compatible version
        compatible_version = 0
        items = self.skin_subjectskinskincommonship_set.all()
        for item in items:
            if item.skincommon.theme_type != 'skin':
                continue
            if compatible_version != 0 and compatible_version != item.skincommon.compatible_version:
                raise Exception('inconsistent compatible version: skin %d, cv %d != %d' % (
                    item.skincommon.id, item.skincommon.compatible_version, compatible_version))
            compatible_version = item.skincommon.compatible_version
        return compatible_version

    def content_dict(self, server, is_del=False):
        if is_del:
            return {
                "id": self.id,
            }
        self.icon.upload_file(server)
        result_dict = {
            'id': self.id,
            'title': self.icon.title,
            'order': self.order,
            'desc': self.desc,
            'icon': self.icon.get_url(server),
            'c_version': self.get_compatible_version(),
            'items': self.get_items(server),
            "_rule": self.rule.content_dict(),
        }
        return result_dict

    def __unicode__(self):
        return "%s" % self.id

    class Meta:
        verbose_name = _('Subject Skin')
        verbose_name_plural = _('Subject Skin')
        app_label = 'skin'


class BannerSkin(BaseFilter):
    order = models.IntegerField(verbose_name=_("Order"))
    rule = models.ForeignKey(Rule, related_name='+', verbose_name=_("Rule"))
    icon = models.ForeignKey(Icon, related_name='+', verbose_name=_("Icon"))
    action = models.IntegerField(
        default=0, choices=BANNER_TYPES_CHOICES, verbose_name=_("Action"))
    value = models.CharField(max_length=1024, verbose_name=_("Value"))

    def __unicode__(self):
        return u"(%s,%s)" % (self.action, self.value)

    def content_dict(self, server, is_del=False):
        if is_del:
            return {
                "id": self.id,
            }

        self.icon.upload_file(server)
        rules = self.rule.content_dict()
        result_dict = {
            'package': rules['packages'][0],
            'sources': rules['sources'],
            'locales': rules['locales']['include'],
            'order': self.order,
            'icon': self.icon.get_url(server),
            'title': self.icon.title,
            'id': self.id,
            'action': self.action,
            'value': self.value,
            "_rule": rules,
        }
        if self.action == 0:
            items = SkinCommon.objects.filter(id=int(self.value))
            if not items:
                raise Exception('invalid skin: %s' % self.value)
            result_dict['c_version'] = items[0].compatible_version if items[
                0].theme_type == 'skin' else 0
        elif self.action == 1:
            items = SubjectSkin.objects.filter(id=int(self.value))
            if not items:
                raise Exception('invalid subject: %s' % self.value)
            result_dict['c_version'] = items[0].get_compatible_version()
        else:
            raise Exception('unknown action')

        return result_dict

    class Meta:
        verbose_name = _('Banner Skin')
        verbose_name_plural = _('Banner Skin')
        app_label = 'skin'

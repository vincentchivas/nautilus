# -*- coding:utf-8 -*-
#/usr/bin/env python
# coding: utf-8
import time
import logging
from django.contrib import admin
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.actions import delete_selected
from admin_enhancer import admin as enhanced_admin
from dolphinopadmin.remotedb.addonstore import \
    update_category, update_subject, update_application, update_feature, update_hoting, \
    delete_category, delete_subject, delete_application, delete_feature, delete_hoting

from dolphinopadmin.addonstore.models.androidEN import \
    AndroidENCategory, AndroidENSubject, AndroidENApplication, AndroidENFeature, \
    AndroidENHoting, AndroidENScreenShot, AndroidENAppPicShipInline, \
    AndroidENSubjectAppsShip, AndroidENSubjectAppsShipInline

from dolphinopadmin.addonstore.models.androidCN import \
    AndroidCNCategory, AndroidCNSubject, AndroidCNApplication, AndroidCNFeature, \
    AndroidCNHoting, AndroidCNScreenShot, AndroidCNAppPicShipInline, \
    AndroidCNSubjectAppsShip, AndroidCNSubjectAppsShipInline
from dolphinopadmin.base.admin import OnlineAdmin
from dolphinopadmin.utils.sites import custom_site

_DB_SERVERS_IP = settings.ENV_CONFIGURATION

logger = logging.getLogger('dolphinopadmin.admin')


def set_positon(obj):
    obj_list = obj.__class__.objects.order_by('position')
    max_order = len(obj_list)
    new_order = obj.position
    if new_order > max_order:
        new_order = max_order
    elif new_order < 1:
        new_order = 1
    for item in obj_list:
        if item.position >= new_order:
            item.position += 1
            item.save()
    obj.app_order = new_order
    obj.save()
    new_obj_list = obj.__class__.objects.order_by('position')
    order = 1
    for item in new_obj_list:
        item.position = order
        order += 1
        item.save()


class CategoryAdmin(OnlineAdmin):

    collection = 'addon_category'
    list_display = ('id', 'category_name', 'position', 'icon',
                    'brief_description', 'online_time', 'offline', 'offline_time')
    list_display_links = ('category_name',)
    search_fields = ['category_name',
                     'brief_description', 'detail_description', ]
    list_filter = ['category_name', ]
    ordering = ['position', ]
    fieldsets = (
        ('Basic Info', {
            'fields': ('category_name', 'icon', 'brief_description',
                       'detail_description', 'position',
                       'online_time', 'offline', 'offline_time')
        }),
    )
    save_as = True
    save_on_top = True

    def get_actions(self, request):
        actions = super(CategoryAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def save_model(self, request, obj, form, change):
        if change:
            set_positon(obj)
        else:
            obj.save()


class SubjectAdmin(OnlineAdmin):

    collection = 'addon_subject'

    list_display = ('id', 'subject_name', 'position', 'icon',
                    'brief_description', 'online_time', 'offline', 'offline_time')
    list_display_links = ('subject_name',)
    search_fields = ['subject_name',
                     'brief_description', 'detail_description', ]
    list_filter = ['subject_name', ]
    filter_vertical = ('applications',)
    ordering = ['position', ]
    raw_id_fields = ('applications',)
    fieldsets = (
        ('Basic Info', {
            'fields': ('subject_name', ('icon', 'is_hot'), 'brief_description',
                       'detail_description', 'position',
                       'online_time', 'offline', 'offline_time')
        }),
        ('Addition Info', {
            'classes': ('collapse',),
            'fields': ('display_update', 'update_number')
        })
    )
    save_as = True
    save_on_top = True

    def save_model(self, request, obj, form, change):
        if change:
            set_positon(obj)
        else:
            obj.save()


class ScreenShotAdmin(admin.ModelAdmin):
    delete_selected_confirmation_template = 'admin/addonstore/delete_selected_confirmation_screenshot.html'
    list_display = ('id', 'title', 'thumbnails', 'pic_url',)
    ordering = ['id', ]
    search_fields = ['id', 'pic_url']
    fieldsets = (
        ('Basic Info', {
            'fields': ('thumbnails', 'pic_url', 'title',)
        }),
    )


class ApplicationAdmin(OnlineAdmin):

    collection = 'addon_application'

    list_display = ('id', 'title', 'position', 'is_hot', 'is_new',
                    'online_time', 'offline', 'offline_time', 'top_ranking', 'ranking_position',
                    'top_new', 'new_position', 'top_web', 'web_position')
    list_editable = ['is_hot', 'is_new', 'top_ranking', 'ranking_position',
                     'top_new', 'new_position', 'top_web', 'web_position',
                     'online_time', 'offline', 'offline_time']
    list_display_links = ('title',)
    list_filter = ['is_new', 'is_hot', 'app_type',
                   'top_ranking', 'top_new', 'top_web', 'category']
    ordering = ['position', ]
    search_fields = ['title', 'short_description']
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'app_ratingcount', 'online_time', 'offline', 'offline_time',
                       'app_developer', 'category',
                       'icon', 'big_icon', 'app_version', 'backup_icon', 'is_new', 'app_size', 'is_hot',
                       'download_url', 'top_ranking', 'ranking_position', 'top_new', 'new_position',
                       'top_web', 'web_position', 'short_description', 'detail_description')
        }),
        ('Other Info', {
            'classes': ('collapse',),
            'fields': ('app_updatetime', 'app_rating', 'position',
                       'app_update_status', 'app_type', 'price')
        }),
    )
    save_as = True
    save_on_top = True

    def save_model(self, request, obj, form, change):
        if change:
            set_positon(obj)
        else:
            obj.save()


class FeatureAdmin(OnlineAdmin):

    collection = 'addon_feature'

    list_display = ('position', 'application', 'id')
    search_fields = ['application__title', ]
    ordering = ['position', ]
    list_display_links = ('id',)
    raw_id_fields = ('application',)
    fieldsets = (
        ('Basic Info', {
            'fields': ('position', 'application', 'description')
        }),
        ('Addition Info', {
            'classes': ('collapse',),
            'fields': ('online_time', 'offline', 'offline_time')
        }),
    )
    save_as = True
    save_on_top = True

    def save_model(self, request, obj, form, change):
        if change:
            set_positon(obj)
        else:
            obj.save()


class HotingAdmin(OnlineAdmin):

    collection = 'addon_hoting'

    list_display = ('position', 'application', 'id',
                    'online_time', 'offline', 'offline_time')
    search_fields = ['application__title', ]
    ordering = ['position', 'id']
    list_display_links = ('application',)
    raw_id_fields = ('application',)
    fieldsets = (
        ('Basic Info', {
            'fields': ('application', 'position', 'online_time', 'offline', 'offline_time')
        }),
    )
    save_as = True
    save_on_top = True

    def save_model(self, request, obj, form, change):
        if change:
            set_positon(obj)
        else:
            obj.save()


class AndroidSubjectAppsShipAdmin(OnlineAdmin):
    list_display = ('id', 'app_order', 'subject', 'app')
    list_editable = ['subject', 'app', 'app_order']
    list_filter = ['subject']
    search_fields = ['subject', 'app']
    ordering = ['app_order']
    list_display_links = ('id',)
    raw_id_fields = ('app',)
    save_as = True
    save_as_top = True

    def save_model(self, request, obj, form, change):
        if change:
            obj_list = obj.__class__.objects.filter(
                subject=obj.subject).order_by('app_order')
            max_order = len(obj_list)
            new_order = obj.app_order
            if new_order > max_order:
                new_order = max_order
            elif new_order < 1:
                new_order = 1
            for item in obj_list:
                if item.app_order >= new_order:
                    item.app_order += 1
                    item.save()
            obj.app_order = new_order
            obj.save()
            new_obj_list = obj.__class__.objects.filter(
                subject=obj.subject).order_by('app_order')
            order = 1
            for item in new_obj_list:
                item.app_order = order
                order += 1
                item.save()
        else:
            obj_list = obj.__class__.objects.filter(
                subject=obj.subject).order_by('app_order')
            max_order = len(obj_list)
            new_order = obj.app_order
            if new_order > max_order:
                new_order = max_order
            if new_order < 1:
                new_order = 1
            for item in obj_list:
                if item.app_order >= new_order:
                    item.app_order += 1
                    item.save()
            obj.app_order = new_order
            obj.save()
            new_obj_list = obj.__class__.objects.filter(
                subject=obj.subject).order_by('app_order')
            order = 1
            for item in new_obj_list:
                item.app_order = order
                order += 1
                item.save()


class AndroidCNApplicationAdmin(ApplicationAdmin):
    list_display = ('id', 'title', 'position', 'is_hot', 'is_new',
                    'online_time', 'offline', 'offline_time', 'top_ranking', 'ranking_position',
                    'top_new', 'new_position', 'top_web', 'web_position', 'is_upload_china')
    inlines = (AndroidCNAppPicShipInline,)


class AndroidENApplicationAdmin(ApplicationAdmin):
    list_display = ('id', 'title', 'position', 'is_hot', 'is_new',
                    'online_time', 'offline', 'offline_time', 'top_ranking', 'ranking_position',
                    'top_new', 'new_position', 'top_web', 'web_position', 'is_upload_ec2')
    inlines = (AndroidENAppPicShipInline,)


class AndroidSubjectAdmin(SubjectAdmin):
    inlines = (AndroidENSubjectAppsShipInline,)


#custom_site.register(AndroidENSubject, AndroidSubjectAdmin)
custom_site.register(AndroidENCategory, CategoryAdmin)
custom_site.register(AndroidENApplication, AndroidENApplicationAdmin)
#custom_site.register(AndroidENFeature, FeatureAdmin)
custom_site.register(AndroidENHoting, HotingAdmin)
custom_site.register(AndroidENScreenShot, ScreenShotAdmin)
# custom_site.register(AndroidENSubjectAppsShip,AndroidSubjectAppsShipAdmin)

#custom_site.register(AndroidCNSubject, AndroidSubjectAdmin)
custom_site.register(AndroidCNCategory, CategoryAdmin)
custom_site.register(AndroidCNApplication, AndroidCNApplicationAdmin)
#custom_site.register(AndroidCNFeature, FeatureAdmin)
custom_site.register(AndroidCNHoting, HotingAdmin)
custom_site.register(AndroidCNScreenShot, ScreenShotAdmin)
# custom_site.register(AndroidCNSubjectAppsShip,AndroidSubjectAppsShipAdmin)

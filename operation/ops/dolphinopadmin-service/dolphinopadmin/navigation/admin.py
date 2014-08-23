# -*- coding:utf-8 -*-
'''
Copyright (c) 2011 Baina Info Inc. All rights reserved.
@Author : Wenyuan Wu
@Date : 2011-11-28
'''
import logging
from django.contrib import admin
from django.conf import settings
from dolphinopadmin.navigation import models
from dolphinopadmin.remotedb.navigation import NAVIGATION_DB
from dolphinopadmin.utils.sites import custom_site
logger = logging.getLogger("dolphinopadmin.admin")


def _remote_action(admin_cls, request, queryset, env, action):
    try:
        items = [i.content_dict() for i in queryset]
        action_method = getattr(NAVIGATION_DB[env], action)
        error_info = action_method(items)
        if not error_info:
            message = '[%s]:%s successfully!\n' % (env.upper(), action)
        else:
            message = error_info
    except Exception, e:
        logger.error('%s Exception:%s' % (message, e))
    admin_cls.message_user(request, message)


def _get_actions(envs, actions=None):
    if not actions:
        actions = []
    for env in envs:
        actions.append('sync_to_%s' % env)
    return actions

_MESSAGE_SYNC_FORMAT = 'Sync navigation to %s server'
_MESSAGE_SYNC_SUCCESSED_FORMAT = 'Sync Navigation to %s Successfully!'
_ENV_CHINA = "china"
_ENV_EC2 = "ec2"
_ENV_LOCAL = "local"
_ENV_DEV = "dev"


class AdAdmin(admin.ModelAdmin):
    list_display = ('id', 'sponsor', 'click_url')
    list_filter = ['sponsor', ]
    list_display_links = ('sponsor',)
    ordering = ['id', ]
    search_fields = ['sponsor', ]


class FeatureSiteAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'click_url')
    list_filter = ['name', ]
    list_display_links = ('name',)
    ordering = ['id', ]
    search_fields = ['name', ]


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_filter = ['name', ]
    list_display_links = ('name',)
    inlines = (models.CategorySiteShipInline,)
    ordering = ['id', ]
    search_fields = ['name', ]


class SiteAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'click_url')
    list_filter = ['name', ]
    list_display_links = ('name',)
    ordering = ['id', ]
    search_fields = ['name', ]


class PromotionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'image_url', 'click_url')
    list_filter = ['title', ]
    list_display_links = ('title',)
    ordering = ['id', ]
    search_fields = ['title', ]


class NavigationAdmin(admin.ModelAdmin):

    def sync_to_china(self, request, queryset):
        _remote_action(self, request, queryset, _ENV_CHINA, 'save_navigations')
    sync_to_china.short_description = _MESSAGE_SYNC_FORMAT % _ENV_CHINA.upper()

    def sync_to_ec2(self, request, queryset):
        _remote_action(self, request, queryset, _ENV_EC2, 'save_navigations')
    sync_to_ec2.short_description = _MESSAGE_SYNC_FORMAT % _ENV_EC2.upper()

    def sync_to_local(self, request, queryset):
        _remote_action(self, request, queryset, _ENV_LOCAL, 'save_navigations')
    sync_to_local.short_description = _MESSAGE_SYNC_FORMAT % _ENV_LOCAL.upper(
    )

    def sync_to_dev(self, request, queryset):
        _remote_action(self, request, queryset, _ENV_DEV, 'save_navigations')
    sync_to_dev.short_description = _MESSAGE_SYNC_FORMAT % _ENV_DEV.upper()

    inlines = (models.AdShipInline, models.FeatureSiteShipInline,
               models.CategoryShipInline, models.PromotionShipInline)
    list_display = ('id', 'name', 'os', 'local')
    list_display_links = ('name',)
    list_filter = ['os', 'local']
    ordering = ['id', ]
    search_fields = ['name', ]
    save_as = True
    save_on_top = True

    actions = _get_actions(settings.ENV_CONFIGURATION.keys())


custom_site.register(models.Ad, AdAdmin)
custom_site.register(models.FeatureSite, FeatureSiteAdmin)
custom_site.register(models.Category, CategoryAdmin)
custom_site.register(models.Site, SiteAdmin)
custom_site.register(models.Promotion, PromotionAdmin)
custom_site.register(models.Navigation, NavigationAdmin)

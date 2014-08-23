#!/user/bin/python
# -*- coding:utf-8 -*-
# Refactored by qtgan
# Date: 2014/3/13

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from dolphinopadmin.hotapps.models import Category, ScreenShot, Application,\
        Feature, Trending, Daily, Ads
from dolphinopadmin.base.base_admin import EntityModelAdmin, AllplatformsAdminT,\
        custom_register
from dolphinopadmin.base.content import HOTAPPS_PLATFORMS as platforms


message = "Please input the correct order value"

class BaseHotappsAdmin(AllplatformsAdminT, EntityModelAdmin):
    auto_sort = True
    order_init = True
    keys = ['id', 'platform']

    def save_model(self, request, obj, form, change):
        if super(BaseHotappsAdmin, self).save_model(request, obj, form, change):
            setattr(self, "manual_error", True)
            messages.error(request, message)


class CategoryAdmin(BaseHotappsAdmin):
    collection = 'category'
    list_display = ('category_name', 'order', 'icon', 'brief_description', 'detail_description')
    search_fields = ['category_name', 'brief_description', 'detail_description', ]
    list_filter = ['category_name', ]
    ordering = ['order', ]
    fieldsets = (
        ('Basic Info', {
            'fields': ('category_name', 'icon', 'brief_description', 'detail_description', 'order')
        }),
        ('Addition Info', {
            'classes': ('collapse',),
            'fields': ('is_third_part', 'third_party_url')
        })
    )

class ScreenShotAdmin(AllplatformsAdminT):
    auto_sort = True
    order_init =True
    list_display = ('id', 'title', 'pic_url',)
    ordering = ['id', ]
    fieldsets = (
        ('Basic Info', {
            'fields': ('pic_url', 'title',)
        }),
    )


class ApplicationAdmin(BaseHotappsAdmin):
    collection = 'application'
    list_display = ('title', 'category_title', 'order',
                    'icon', 'download_url', 'short_description')
    list_filter = ['app_type', 'category__category_name']
    ordering = ['order', ]
    search_fields = ['title', 'short_description']
    raw_id_fields = ('category',)
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'icon', 'category', 'app_type', 'is_new',
                       'download_url', 'short_description', 'order')
        }),
        ('Other Info', {
            'classes': ('collapse',),
            'fields': (('app_updatetime', 'app_version'), (
                'app_developer', 'app_rating'), 'detail_description',
                'app_size', 'price', 'original_price',
                'favourable_price', 'price_type', 'price_limit_time',)
        }),
        ('Addition Info', {
            'classes': ('collapse',),
            'fields': ('is_third_part', 'api_url')
        }),
    )

class FeatureAdmin(BaseHotappsAdmin):
    collection = 'feature'
    list_display = ('feature_type', 'order',
                    'application_title', 'feature_on_top')
    search_fields = ['application__title', ]
    ordering = ['order', ]
    list_filter = ['feature_type', 'feature_on_top', ]
    list_display_links = ('feature_type',)
    raw_id_fields = ('application',)
    fieldsets = (
        ('Basic Info', {
            'fields': ('feature_type', 'application', 'category',
                       'feature_on_top', 'top_feature_pic', 'small_pic', 'order')
        }),
        ('Addition Info', {
            'classes': ('collapse',),
            'fields': ('is_third_part', 'third_part_url')
        }),
    )


class TrendingAdmin(BaseHotappsAdmin):
    collection = 'trending'
    list_display = ('order', 'application_title', 'id',)
    search_fields = ['application__title', ]
    ordering = ['order', 'id']
    list_display_links = ('application_title',)
    raw_id_fields = ('application',)
    fieldsets = (
        ('Basic Info', {
            'fields': ('application', 'order')
        }),
    )


class DailyAdmin(BaseHotappsAdmin):
    collection = 'daily'
    auto_sort = False
    order_init = False
    list_display = ('id', 'application_title',)
    search_fields = ['application__title', ]
    ordering = ['id']
    list_display_links = ('application_title',)
    raw_id_fields = ('application',)
    fieldsets = (
        ('Basic Info', {
            'fields': ('application', 'reason',)
        }),
    )

class AdsAdmin(BaseHotappsAdmin):
    collection = 'ad'
    list_display = ('title', 'category_title', 'order',
                    'icon', 'download_url', 'short_description')
    list_filter = ['category__category_name', ]
    ordering = ['order', ]
    search_fields = ['title', 'short_description']
    raw_id_fields = ('category',)
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'picture_url', 'download_url', 'category',)
        }),
        ('Other Info', {
            'classes': ('collapse',),
            'fields': ('icon', 'is_new', 'short_description', 'order',
                       ('app_updatetime', 'app_version'), ('app_developer',
                                                           'app_rating'), 'detail_description',
                       ('app_size', 'app_type'), 'price', 'original_price',
                       'favourable_price', 'price_type', 'price_limit_time',)
        }),
        ('Addition Info', {
            'classes': ('collapse',),
            'fields': ('is_third_part', 'api_url')
        }),
    )


label = ("hotapps", _("hostapps"))

base_model_admin = (
    (ScreenShot, ScreenShotAdmin),
    (Application, ApplicationAdmin),
    (Feature, FeatureAdmin),
    (Trending, TrendingAdmin),
    (Daily, DailyAdmin),
    (Ads, AdsAdmin),
    (Category, CategoryAdmin)
)

foreign_filter = (
    (
        "Application",
        ("category",)
    ),
    (
        "Feature",
        ("application", "category")
    ),
    (
        "Trending",
        ("application",)
    ),
    (
        "Daily",
        ("application",)
    ),
    (
        "Ads",
        ("category",)
    )
)

inlines = (
    (Application, ScreenShot, "(self.%s.title, self.%s.pic_url)"),
    (Ads, ScreenShot, "(self.%s.title, self.%s.pic_url)")
)

for platform in platforms:
    filters = {"platform": platform[0]}
    class_name = "%s" % platform[1]
    model_name =  "%s" % platform[0]
    custom_register(base_model_admin, filters, class_name, model_name,
                label, inlines, foreign_filter)

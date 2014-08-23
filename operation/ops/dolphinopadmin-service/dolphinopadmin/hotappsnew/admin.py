# -*- coding:utf-8 -*-
#/usr/bin/env python
# coder yfhe

#import logging
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from dolphinopadmin.hotappsnew.models import Category, ScreenShot, Application, \
    Feature, Trending

from dolphinopadmin.base.base_admin import AllplatformsAdminT, EntityModelAdmin, \
    custom_register, query_platforms


class HotappsAdmin(AllplatformsAdminT, EntityModelAdmin):

    keys = ['id', 'platform']
    auto_sort = True
    order_init = True


class CategoryAdmin(HotappsAdmin):

    collection = 'category_new'

    list_display = ('id', 'title', 'order', 'icon', 'update_number',
                    'brief_description')
    list_editable = ('title', 'order', 'icon', 'update_number')
    search_fields = ['title', 'brief_description', 'detail_description', ]
    list_filter = ['title', ]
    ordering = ['order', ]
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', ('icon', 'is_hot'), 'brief_description',
                       'detail_description', 'order', 'rule')
        }),
        ('Addition Info', {
            'classes': ('collapse',),
            'fields': ('display_update', 'update_number', 'is_third_part', 'third_party_url')
        })
    )


class ScreenshotAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'thumbnails', 'pic_url',)
    fieldsets = (
        ('Basic Info', {
            'fields': ('thumbnails', 'pic_url', 'title',)
        }),
    )


class ApplicationAdmin(HotappsAdmin):

    collection = 'application_new'

    list_display = ('id', 'title', 'order', 'is_hot',
                    'is_new', 'short_description')
    list_display_links = ('title',)
    list_filter = ['is_new', 'is_hot', 'app_type']
    ordering = ['order', ]
    search_fields = ['title', 'short_description']
    fieldsets = (
        (_('Basic Info'), {
            'fields': ('title', 'app_type', 'app_developer', 'rule', 'app_rating',
                       'app_ratingcount', 'icon', 'is_hot', 'order', 'backup_icon',
                       'is_new', 'app_size', 'download_url', 'pub_time', 'short_description',
                       'detail_description')
        }),
        (_('Other Info'), {
            'classes': ('collapse',),
            'fields': ('app_updatetime', 'app_update_status', 'app_lovecount',
                       'force_lovecount', 'app_version', 'price', 'original_price',
                       'favourable_price', 'price_type', 'price_limit_time')
        }),
        (_('Addition Info'), {
            'classes': ('collapse',),
            'fields': ('is_third_part', 'api_url')
        }),
    )


class FeatureAdmin(HotappsAdmin):

    collection = 'feature_new'

    list_display = ('id', 'feature_type', 'title', 'order',
                    'feature_on_top', 'hot_today', 'description')
    search_fields = ['application__title', ]
    ordering = ['order', ]
    list_filter = ['feature_type', 'feature_on_top', ]
    list_display_links = ('feature_type',)
    raw_id_fields = ['application', 'category']
    fieldsets = (
        ('Basic Info', {
            'fields': ('feature_type', 'rule', 'feature_on_top', 'hot_today', 'description',
                       'top_feature_pic', 'small_pic', 'application', 'category', 'order')
        }),
        ('Addition Info', {
            'classes': ('collapse',),
            'fields': ('is_third_part', 'third_part_url')
        }),
    )


class TrendingAdmin(HotappsAdmin):

    collection = 'trending_new'

    list_display = ('id', 'title', 'order')
    search_fields = ['application__title', ]
    list_display_links = ('id',)
    ordering = ['order', ]
    raw_id_fields = ['application']
    fieldsets = (
        ('Basic Info', {
            'fields': ('application', 'order', 'rule')
        }),
    )

    def get_ordering(self, request):
        return self.ordering

inlines = (
    (Application, ScreenShot, '(self.%s.title,self.%s.url)'),
    (Category, Application, '(self.%s.title,self.%s.title)'),
)

base_model_admin = (
    (Application, ApplicationAdmin),
    (Category, CategoryAdmin),
    (Feature, FeatureAdmin),
    (Trending, TrendingAdmin),
    (ScreenShot, ScreenshotAdmin)
)

foreign_filter = (
    (
        'Feature',
        ('application', 'category')
    ), (
        'Trending',
        ('application',)
    )
)


label = ("hotappsnew", _("new hotapps"))

for platform in query_platforms(['IosEN', 'IosCN', 'AndroidCN'], [(('AndroidJP', 'AosJp'))]):
    filters = {'platform': platform[0]}
    class_name = platform[1]
    model_name = platform[0]
    custom_register(
        base_model_admin, filters, class_name, model_name, label, inlines,
        foreign_filter)

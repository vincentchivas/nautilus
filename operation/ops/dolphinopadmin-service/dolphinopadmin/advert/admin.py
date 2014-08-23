# -*- coding: utf-8 -*-
import logging
#from django.contrib import admin
from dolphinopadmin.advert.models import Cooperation, \
    Publisher, PositionCategory, PositionItem, Position
from dolphinopadmin.base.admin import ToolAdmin, OnlineAdmin
from dolphinopadmin.utils.sites import custom_site

logger = logging.getLogger("dolphinopadmin.admin")


class PublisherAdmin(ToolAdmin):
    list_display = ('company', 'remark',  'last_modify',)
    list_filter = ('company',)
    search_fields = ('company',)


class PositionCategoryAdmin(ToolAdmin):
    list_display = ('name', 'cid',)
    list_filter = ('name',)
    search_fields = ('name',)


class PositionItemAdmin(ToolAdmin):
    list_display = ('name', 'pid',)
    list_filter = ('name',)
    search_fields = ('name',)


class PositionAdmin(ToolAdmin):
    list_display = ('category', 'location')


class CooperationAdmin(OnlineAdmin):

    collection = 'advert'

    list_display = ('id', 'name', 'title', 'weight', 'is_upload_china')
    list_filter = ('publisher', )
    ordering = ['-id']
    search_fields = ('name', 'title')
    #filter_horizontal = ('position', )


custom_site.register(Publisher, PublisherAdmin)
custom_site.register(Cooperation, CooperationAdmin)
custom_site.register(PositionCategory, PositionCategoryAdmin)
custom_site.register(PositionItem, PositionItemAdmin)
custom_site.register(Position, PositionAdmin)

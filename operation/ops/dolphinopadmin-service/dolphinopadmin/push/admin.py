#!/usr/bin/env python
# -*- coding:utf-8 -*-
# coder yfhe
import logging
from forms import PushAdminForm
from django.utils.translation import ugettext_lazy as _
from dolphinopadmin.base.base_admin import EntityModelAdmin, AllplatformsAdminT, \
    custom_register, query_platforms
from dolphinopadmin.push.models import Push, Item, Folder, PUSH_TYPES, PushCommon, EngineStatus
from dolphinopadmin.search.models import Search

logger = logging.getLogger('dolphinopadmin.admin')


class PushAdmin(AllplatformsAdminT, EntityModelAdmin):

    keys = ['id']
    form = PushAdminForm
    collection = 'push_messages'
    list_display = ['id', 'name', 'push_type',
                    'is_upload_china', 'is_upload_ec2']
    list_display_links = ['name']
    list_filter = ['rule', 'push_type']

    # def get_content(self, request, item, server):
    #    return item.content_dict(server)


class PushCommonAdmin(AllplatformsAdminT, EntityModelAdmin):

    keys = ['id']
    collection = "push_messages_new"
    list_filter = ['rule', ]
    filter_horizontal = ['target_engine', ]
    ordering = ['order']

    def get_list_display(self, request):
        if self.model.filters['types'] is 'newhome_notify':
            list_display = ('id', 'title', 'rule')
        elif self.model.filters['types'] is 'engineswitch':
            list_display = ('id', 'engine_switch', 'rule', 'all_target')
        elif self.model.filters['types'] is 'searchengine':
            list_display = ('method', 'search', 'is_force', 'is_default')
        elif self.model.filters['types'] is 'trafficclean':
            list_display = ('id', 'traffic_clean', 'search_engine', 'partner_id_name', 'partner_id_value', 'start_time', 'end_time', 'rule')
        else:
            list_display = ('id', 'order', 'method', 'item', 'folder', )
        return list_display

    def get_list_display_links(self, request, list_display):
        if self.model.filters['types'] is 'newhome_notify':
            list_display_links = ('id', 'title')
        elif self.model.filters['types'] is 'engineswitch':
            list_display_links = ('id', 'engine_switch')
        elif self.model.filters['types'] is 'trafficclean':
            list_display_links = 'id'
        elif self.model.filters['types'] is 'searchengine':
            list_display_links = ('method', 'search')
        else:
            list_display_links = ('order', 'item')
        return list_display_links

    def get_fieldsets(self, request, obj=None):
        if self.model.filters['types'] is 'newhome_notify':
            fieldsets = (('Basic Info', {
                'fields': ('title', 'rule','is_upload_china', 'is_upload_ec2',
                           'is_upload_local')
            }),
            )
        elif self.model.filters['types'] is 'engineswitch':
            fieldsets = (('Basic Info', {
                'fields': ('engine_switch', 'target_engine', 'rule',
                           'is_upload_china', 'is_upload_ec2', 'is_upload_local')
            }),
            )
        elif self.model.filters['types'] is 'trafficclean':
            fieldsets = (('Basic Info', {
                'fields': ('traffic_clean', 'search_engine', 'partner_id_name',
                           'partner_id_value', 'start_time', 'end_time', 'rule')
            }),
            )
        elif self.model.filters['types'] is 'searchengine':
            fieldsets = (('Basic Info', {
                'fields': ('method', 'unique_name', 'search', 'is_force', 'is_default', 'rule',
                           'is_upload_china', 'is_upload_ec2', 'is_upload_local')
            }),
            )
        else:
            fieldsets = (('Basic Info', {
                'fields': ('method', 'item', 'folder', 'modify_url', 'order', 'can_delete', 'rule',
                           'is_upload_china', 'is_upload_ec2', 'is_upload_local')
            }),
            )
        return fieldsets


class ItemAdmin(AllplatformsAdminT):

    raw_id_fields = ['icon']
    list_display = ['url', 'title']
    list_display_links = ['url']
    search_fields = ['url', 'title']


class FolderAdmin(AllplatformsAdminT):
    list_display = ['title']
    list_display_links = ['title']


class EngineStatusAdmin(AllplatformsAdminT):
    list_display = ['serial_number', 'name']
    list_display_links = ['serial_number', 'name']
    ordering = ['-serial_number']

class SearchEngineAdmin(AllplatformsAdminT):
    list_display = ['id', 'name', 'title', 'url']
    search_fields = ['title', 'url']
    ordering = ['-id']
    raw_id_fields = ['icon']

inlines = ((Folder, Item, '(self.%s.title, self.%s.title)'),)

foreign_filter = (
    (
        'PushCommon',
        ('item', 'folder', 'search')
    ),
)
label = ("push", _("push messages"))


def query_types():
    return PUSH_TYPES

for platform in query_platforms([]):
    filters = {'platform': platform[0]}
    class_name = 'old %s' % platform[1]
    model_name = 'old%s' % platform[0]
    custom_register(((Push, PushAdmin),), filters,
                    class_name, model_name, label)

base_model_admin = {}

base_model_admin['newhome_notify'] = base_model_admin['searchengine'] = base_model_admin['engineswitch'] = base_model_admin['trafficclean'] = (
    (PushCommon, PushCommonAdmin),
)

base_model_admin['speed_dial'] = base_model_admin['bookmark'] = (
    (PushCommon, PushCommonAdmin),
    (Item, ItemAdmin),
    (Folder, FolderAdmin),
)

for platform in query_platforms(['IosEN', 'IosCN', 'AndroidCN']):
    for tmp_type in query_types():
        filters = {'platform': platform[0], 'types': tmp_type[0]}
        class_name = "%s %s" % (platform[1], tmp_type[1])
        model_name = "%s%s" % (platform[0], tmp_type[0])
        if tmp_type[0] is 'searchengine':
            custom_register(
                base_model_admin[tmp_type[0]], filters, class_name, model_name, label, inlines, \
                foreign_filter, {'platform': platform[0]})
        elif tmp_type[0] in ['trafficclean', 'newhome_notify']:
             custom_register(
                base_model_admin[tmp_type[0]], filters, class_name, model_name, label)
        else:
            custom_register(
                base_model_admin[tmp_type[0]], filters, class_name, model_name, label, inlines, \
                foreign_filter)

    custom_register(((Search, SearchEngineAdmin),),
                      {'platform': platform[0]}, "%s %s" % (platform[1], unicode(_('search engine'))), \
                      platform[0], label)

custom_register(((EngineStatus, EngineStatusAdmin),), {}, '', "", label)

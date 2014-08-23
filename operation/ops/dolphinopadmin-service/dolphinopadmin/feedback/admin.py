# -*- coding:utf-8 -*-
'''
Copyright (c) 2011 Baina Info Inc. All rights reserved.
@Author : Wenyuan Wu
@Date : 2011-11-23
'''

import os
import time
import logging
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib import admin
from django.conf.urls.defaults import patterns
from excel import export_data_to_excel
from dolphinopadmin.base.admin import ToolAdmin
from dolphinopadmin.utils import utc2local
from dolphinopadmin.remotedb.feedback import get_feedbacks, get_feedbacks_en
from dolphinopadmin.feedback.models import Feedback, VersionCode, Feedback_en
from dolphinopadmin.base.base_admin import AllplatformsAdminT
from dolphinopadmin.utils.sites import custom_site

_TABLE_COLUMN_NAMES = [
    'Package', 'Source', 'Feedback Type', 'Version', 'IP Address', 'Message', 'Contact Info',
    'OS', 'Locale', 'Time']

_OS = {
    'android': 'Android',
    'ipad': 'iPad',
    'iphone': 'iPhone',
    'unknown': 'unknown',
    'pc': 'PC'
}

_LOCALE = {
    'zh_cn': 'zh_CN',
    'en_us': 'en_US',
    'unknown': 'unknown'
}

_FILE_NAME = '%s.xls' % time.strftime('%Y%m%d', time.localtime())

_SAVE_PATH = os.path.join('/tmp', _FILE_NAME)


logger = logging.getLogger("dolphinopadmin.admin")


class VersionCodeAdmin(ToolAdmin):

    list_display = ('id', 'version', 'vname')
    ordering = ['-id']


class FeedbackBaseAdmin(AllplatformsAdminT):

    # override the queryset method in ModelAdmin
    def queryset(self, request):
        qs = super(FeedbackBaseAdmin, self).queryset(request)
        return qs.filter(deleted=False)

    # override the get_urls method in ModelAdmin

    def _sync_feedbacks_from_remotedb(self, request, env):
        message = ''
        if env == 'sync_en':
            feedbacks = get_feedbacks_en('ec2')
            target_model = Feedback_en
        else:
            feedbacks = get_feedbacks(env)
            target_model = Feedback
        logger.debug(feedbacks)
        if len(feedbacks) <= 0:
            message += 'There is no feedback data to update!'
        else:
            try:
                # insert the feedback data into mysql
                for feedback in feedbacks:
                    try:
                        logger.info(feedback)
                        temp_os = feedback['os'].lower()
                        temp_os = _OS[temp_os] if temp_os in _OS else 'unknown'
                        temp_locale = feedback['locale'].lower()
                        temp_locale = _LOCALE[
                            temp_locale] if temp_locale in _LOCALE else 'unknown'
                        try:
                            product = VersionCode.objects.get(
                                product=feedback['package'], version=int(feedback['version']))
                            vname = product.vname
                        except:
                            vname = 'unknown'

                        f = target_model(
                            name=feedback['name'], contact_info=feedback[
                                'contact_info'],
                            locale=temp_locale, message=feedback[
                                'message'],
                            time=utc2local(feedback['time']),
                            os=temp_os, remote_address=feedback[
                                'remote_address'],
                            feedback_type=feedback[
                                'feedback_type'], deleted=False,
                            package=feedback[
                                'package'], source=feedback['source'],
                            version=feedback['version'], vname=vname)

                        f.save()
                    except Exception, e:
                        logger.exception(e)
                message += 'Update Feedbacks Successfully!'
            except Exception, e:
                message += 'sync feedbacks failed!'
                logger.exception(e)
        self.message_user(request, message)

    # Update Feedbacks from Database
    def sync_feedbacks_from_local(self, request):
        self._sync_feedbacks_from_remotedb(request, 'local')
        return HttpResponseRedirect('../')

    # Update Feedbacks from Database
    def sync_feedbacks_from_china(self, request):
        self._sync_feedbacks_from_remotedb(request, 'china')
        return HttpResponseRedirect('../')

    # Update Feedbacks from Database
    def sync_feedbacks_from_ec2(self, request):
        self._sync_feedbacks_from_remotedb(request, 'ec2')
        return HttpResponseRedirect('../')

    # Update Feedbacks from Database
    def sync_feedbacks_from_dev(self, request):
        self._sync_feedbacks_from_remotedb(request, 'dev')
        return HttpResponseRedirect('../')

    def sync_en_feedbacks(self, request):
        self._sync_feedbacks_from_remotedb(request, 'sync_en')
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

    # Export Selected Feedback Data to Excel
    """
    def export_selected_feedbacks(self, request, queryset):
        feedback_data = []
        for item in queryset:
            feedback_data.append(item.get_content_list())
        export_data_to_excel(_TABLE_COLUMN_NAMES, feedback_data, _SAVE_PATH)
        export_data = open(_SAVE_PATH, 'rb').read()
        response = HttpResponse(
            export_data, mimetype='application/vnd.ms-excel')
        response[
            'Content-Disposition'] = 'attachment; filename=%s' % _FILE_NAME
        return response
    export_selected_feedbacks.short_description = 'export selected feedbacks'
    """

    def remove_selected_items(self, request, queryset):
        count = queryset.count()
        queryset.update(deleted=True)
        self.message_user(
            request, 'Remove %d Selected Feedbacks Successfully!' % count)
    remove_selected_items.short_description = 'remove selected feedbacks'

    actions = ['remove_selected_items', 'export_select_data']
    list_display = (
        'package', 'source', 'feedback_type', 'version', 'remote_address', 'message', 'contact_info',
        'os', 'locale', 'time')
    list_filter = ['feedback_type', 'os',
                   'locale', 'package', 'source', 'version']
    ordering = ['-time']
    search_fields = ['message']


class FeedbackCnAdmin(FeedbackBaseAdmin):

    def get_urls(self):
        urls = super(FeedbackBaseAdmin, self).get_urls()
        urls += patterns('', (r'^update$', self.sync_feedbacks_from_china))
        return urls


class FeedbackEnAdmin(FeedbackBaseAdmin):

    def get_urls(self):
        urlpatterns = super(FeedbackEnAdmin, self).get_urls()
        from django.conf.urls.defaults import url
        info = self.model._meta.app_label, self.model._meta.module_name
        urlpatterns += (
            url(r'^update$', self.sync_en_feedbacks,
                name='%s_%s_sync_to_production' % info),
        )
        return urlpatterns
"""
    def get_urls(self):
        urls = super(FeedbackBaseAdmin, self).get_urls()
        from django.conf.urls.defaults import url
        urls += (url(r'^update/', self.sync_en_feedbacks,name='sync_en_feedback'),)
        return urls
"""

custom_site.register(VersionCode, VersionCodeAdmin)
custom_site.register(Feedback, FeedbackCnAdmin)
custom_site.register(Feedback_en, FeedbackEnAdmin)

# -*- coding:utf-8 -*-
# coder yfhe
import logging
from django.utils.translation import ugettext_lazy as _
from dolphinopadmin.base.base_admin import EntityModelAdmin, AllplatformsAdminT, \
    custom_register, query_platforms
from dolphinopadmin.sms.models import SmsFilters, PhoneNumber, KeyWord

logger = logging.getLogger('dolphinopadmin.admin')


class SmsFiltersAdmin(AllplatformsAdminT, EntityModelAdmin):

    collection = 'sms_listen'
    keys = ['id']

    list_display = ['id', 'name', 'is_upload_china', 'rule']
    list_display_links = ['name']
    list_filter = ['rule']
    #ordering = ['-id']


class PhoneNumberAdmin(AllplatformsAdminT):

    list_display = ('name', 'title', 'number', 'icon')
    list_display_links = ('name',)
    raw_id_fields = ('icon',)
    #ordering = ['-id']


class KeyWordAdmin(AllplatformsAdminT):
    list_display = ('name', 'key_value')
    list_display_links = ('name',)
    #ordering = ['-id']

inlines = (
    (SmsFilters, PhoneNumber, '(self.%s.name,self.%s.title)'),
    (SmsFilters, KeyWord, 'self.%s.name,self.%s.key_value')
)

foreign_filter = (
    (
        'SmsFilters',
        ('PhoneNumber', 'KeyWord')
    ),
)

label = ("sms", _("sms listen"))


#    model_class = model_factory(class_name, model_name,Push, string_with_title("push", _("push messages")),filters)
#    model_form = allplatformsAdmin_factory(class_name, model_name,PushAdmin,filters)
    #custom_site.register(model_class, model_form)

for platform in query_platforms(['AndroidEN', 'IosEN', 'IosCN']):
        filters = {'platform': platform[0]}
        class_name = platform[1]
        model_name = platform[0]
        base_model_admin = (
            (SmsFilters, SmsFiltersAdmin),
            (PhoneNumber, PhoneNumberAdmin),
            (KeyWord, KeyWordAdmin)
        )
        custom_register(
            base_model_admin, filters, class_name, model_name, label, inlines,
            foreign_filter)

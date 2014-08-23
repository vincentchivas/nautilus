# -*- coding: utf-8 -*-
import logging
import sys
#import os
import time
from datetime import datetime
from pyExcelerator import Workbook

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.actions import delete_selected
from django.contrib.admin.models import LogEntry
from django.utils.encoding import force_unicode
from django.http import HttpResponseRedirect, HttpResponse
from admin_enhancer.admin import EnhancedModelAdminMixin
from django.contrib.contenttypes.models import ContentType

from dolphinopadmin.base.base_model import model_factory, ship_factory
from dolphinopadmin.utils import string_with_title
from dolphinopadmin.utils.sites import custom_site
from content import LAYOUT_CHOICES, PLATFORMS
from dolphinopadmin.remotedb import basedb

logger = logging.getLogger("dolphinopadmin.admin")
DB_SERVERS = settings.ENV_CONFIGURATION
_ONLINE = ['local', 'china', 'ec2']

def query_platforms(disable, extra=[]):
    platforms = PLATFORMS.copy()
    platforms.update(extra)
    return [(key, platforms[key]) for key in platforms if key not in disable]

class BasePrototype():

    def _init_order(self, request):
        items = self.queryset(request).order_by('-order')
        next_order = 1 if not items else items[0].order + 1
        return next_order

    def _set_order(self, request, obj):

        if obj.pk and obj.order == self.queryset(request).get(pk__exact=obj.id).order:
            return None
        items = self.queryset(request).order_by('order')
        max_order = len(items)
        new_order = obj.order
        new_order = max_order if new_order > max_order else new_order
        if new_order == -1 or new_order == 0:
            return None
        sort_list = [i for i in items if obj.id != i.id]
        sort_list.insert(new_order - 1, obj)
        order = 1
        for item in sort_list:
            item.order = order
            order += 1
            if hasattr(item, 'modifier'):
                item.modified_time = datetime.now()
                item.modifier = request.user

            item.save()


class EntityModelAdmin(admin.ModelAdmin):

    def _get_actions(envs, actions=[]):
        for env in envs:
            actions.append('upload_to_%s' % env)
            actions.append('delete_from_%s' % env)
        return actions

    keys = ['id']
    actions = _get_actions(
        DB_SERVERS.keys(), ['delete_selected_from_admin'])
    readonly_fields = ['is_upload_local', 'is_upload_china', 'is_upload_ec2']
    replace = True


    def delete_selected_from_admin(self, request, queryset):
        message = ''
        for item in queryset:
            if not hasattr(item, 'is_upload_local'):
                break
            for key in DB_SERVERS.keys():
                if eval('item.is_upload_%s' % key):
                    message += _(
                        "Warning: %(item)s has been upload to %(server)s, please delete it from %(server)s first!") % {"item": item,
                                                                                                                       "server": key}
                    messages.warning(request, message)
                    logger.debug(message)
                    return None
        return delete_selected(self, request, queryset)
    delete_selected_from_admin.short_description = _('delete from admin')

    def log_publish(self, request, obj, message, action):
        LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=ContentType.objects.get_for_model(obj).pk,
            object_id=obj.pk,
            object_repr=force_unicode(obj),
            action_flag=action,
            change_message=message
        )

    def _update_selected(self, env, querysets, value):
        for queryset in querysets:
            setattr(queryset, 'is_upload_%s' % env, value)
            queryset.save()

    def _sync_mongodb(self, request, queryset, server, method):
        message = ''
        mongo_pk = {}
        success_queryset = []
        is_del = method is 'delete'
        try:
            for item in queryset:
                try:
                    if hasattr(item, 'upload_file') and item.upload_file:
                        result = item.upload_file(server, is_del=is_del)
                        if not hasattr(item, 'content_dict'):
                            if isinstance(result, tuple) and not result[0]:
                                messages.warning(request, result[1])
                            else:
                                success_queryset.append(item)
                                self.log_publish(
                                    request, item, _(
                                        '%(method)s to %(server)s successfully' %
                                        {'method': method, 'server': server}), 4 if is_del else 3)
                            continue

                    if hasattr(item, 'content_dict'):
                        mongo_data = item.content_dict(
                            server, is_del=is_del)
                    else:
                        raise ValueError(_('can\'t orginize mongo data'))

                    if '_sync_key' in mongo_data and isinstance(mongo_data['_sync_key'], dict):
                        mongo_pk = {'_sync_key': mongo_data['_sync_key']}
                    elif hasattr(self, 'keys'):
                        for key in self.keys:
                            mongo_pk[key] = mongo_data[key]
                    else:
                        raise ValueError(_('missing mognodb sync keys'))

                    if hasattr(self, 'collection'):
                        if is_del:
                            basedb.delete_data(
                                self.collection, mongo_pk, server)
                        else:
                            basedb.update_data(
                                self.collection, mongo_pk, mongo_data, server, self.replace)
                    else:
                        raise ValueError(
                            _('not assign target monogodb table'))

                    if server in _ONLINE:
                        logger.info(
                            _('User: %(name)s %(method)s data from %(server)s') %
                            {'method': method, 'name': request.user.username, 'server': server})
                        logger.info(mongo_data)
                    else:
                        raise ValueError(
                            _('assign server:%(server)s can\'t %(method)s ' % {'server': server, 'method': method}))

                    success_queryset.append(item)
                    self.log_publish(
                        request, item, _(
                            '%(method)s to %(server)s successfully' %
                            {'method': method, 'server': server}), 4 if is_del else 3)

                except Exception, e:
                    self.log_publish(
                        request, item, _(
                            '%(method)s %(item)s fail,fail reason is %(e)s' %
                            {'method': method, 'item': unicode(item), 'e': e}), 4 if is_del else 3)
                    messages.error(
                        request, _('%(method)s %(item)s fail,fail reason is %(e)s') %
                        {'method': method, 'item': item, 'e': e})
                    continue

            count = len(success_queryset)
            if count:
                self._update_selected(server, success_queryset, not is_del)
                message = unicode(
                    _('%(method)s %(count)s %(name)s from %(server)s successfully!\n')) % {'method': method, 'count': count,
                                                                                           "name": success_queryset[0].__class__.__name__, "server": server}
                messages.success(request, message)

        except Exception, e:
            message += unicode(_(
                            'Error:some unexcepted cause %(method)s failed, error is %(event)s!' %
                            {'method': method, 'event': e}))
            messages.error(request, message)
            logger.exception(e)

    def get_actions(self, request):
        actions = super(EntityModelAdmin, self).get_actions(request)
        if not request.POST.get('post'):
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions

    def save_model(self, request, obj, form, change):
        now = datetime.now()
        user = request.user
        if not change:
            obj.creator = user
            obj.created_time = now

        obj.modified_time = now
        obj.modifier = user


class EnhancedAdminInline(BasePrototype, EnhancedModelAdminMixin, admin.TabularInline):

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(EnhancedAdminInline,
                          self).formfield_for_dbfield(db_field, **kwargs)
        if hasattr(self, 'filter_include'):
            key = db_field.name
            if key in self.filter_include:
                queryset = formfield._get_queryset().filter(
                    **self.filter_include[key])
                formfield._set_queryset(queryset)

        return formfield

    def save_model(self, request, obj, form, change):
        super(EnhancedAdminInline, self).save_model(request, obj, form, change)
        if not obj.pk:
            if hasattr(obj, 'order') and not obj.order and hasattr(self, 'order_init'):
                obj.order = self._init_order(request)
        else:
            if hasattr(obj, 'order') and hasattr(self, 'auto_sort') and change:
                self._set_order(request, obj)

        obj.save()


class AllplatformsAdminT(BasePrototype, EnhancedModelAdminMixin, admin.ModelAdmin):

    save_as = True
    save_on_top = True

    def _save_path(self):
        return '/tmp/%s.xls' % time.strftime('%Y%m%d', time.localtime())

    def get_ordering(self, request):
        order = list(super(AllplatformsAdminT, self).get_ordering(request))
        try:
            order.remove('id')
            order.remove('-id')
        except Exception:
            pass
        order.append('-id')
        return order

    def _export_data_to_excel(self, export_data, path):
        sample = export_data[0]
        column_names = [[key, 0]
                        for key in self.list_display if hasattr(sample, key)]
        for item in column_names:
            try:
                getattr(sample, item[0])()
                item[1] = 1
            except:
                pass
        workbook = Workbook()
        sheet = workbook.add_sheet('sheet0')
        length = len(column_names)
        for i in range(length):
            sheet.write(0, i, column_names[i][0])

        for i in range(len(export_data)):
            for j in range(length):
                try:
                    if column_names[j][1]:
                        value = getattr(export_data[i], column_names[j][0])()
                    else:
                        value = getattr(export_data[i], column_names[j][0])
                except:
                    value = ''

                sheet.write(i + 1, j, force_unicode(value))
        workbook.save(path)

    def export_select_data(self, request, queryset, **kwargs):

        tmp_save_path = self._save_path()
        #para_get = request.GET
        #filters = {}
        # for key in para_get:
        #    tmp = para_get.get(key)
        #    if tmp:
        #        filters[key] = tmp[0] if isinstance(tmp, list) else tmp
        #self._export_data_to_excel([i for i in self.model.objects.filter(**filters)], tmp_save_path)
        self._export_data_to_excel([i for i in queryset], tmp_save_path)
        export_data = open(tmp_save_path, 'rb').read()
        response = HttpResponse(
            export_data, mimetype='application/vnd.ms-excel')
        response[
            'Content-Disposition'] = 'attachment; filename=%s' % self.model._meta.verbose_name
        return response
    export_select_data.verbose_name = _('export select data')

    def manual_response(self, request, obj, method, *args, **kwargs):
        if hasattr(self, 'manual_error'):
            return HttpResponseRedirect(request.path)
        else:
            return getattr(super(AllplatformsAdminT, self), method)(request, obj, *args, **kwargs)

    def render_change_form(self, request, context, *args, **kwargs):
        if hasattr(self, 'form_name'):
            dif_init_choices = LAYOUT_CHOICES.get(self.form_name)
            fields = context['adminform'].form.fields

            print dif_init_choices
            if hasattr(self, 'filters'):
                for key in self.filters:
                    if fields.has_key(key):
                        fields[key].initial = self.filters[key]

            if hasattr(self, 'foreign_filter'):
                tmp_filter = self.foreign_filter
                for key in tmp_filter:
                    if fields.has_key(key):
                        try:
                            queryset = fields[key]._get_queryset().filter(
                                **tmp_filter[key])
                            fields[key]._set_queryset(queryset)
                        except Exception, e:
                            logger.info(e)

            if dif_init_choices:
                keys = dif_init_choices.keys()
                for key in keys:
                    print fields, self.filters.get('platform')
                    if fields.has_key(key):
                        old_choices = fields[key]
                        fields[key] = forms.ChoiceField(widget=forms.Select(),
                                                        choices=dif_init_choices.get(key).get(self.filters.get('platform'), old_choices), label="Category layout")

        return super(AllplatformsAdminT, self).render_change_form(request, context, *args, **kwargs)

    def queryset(self, request):

        if hasattr(self, 'filters'):
            return super(AllplatformsAdminT, self).queryset(request).filter(**self.filters)
        else:
            return super(AllplatformsAdminT, self).queryset(request)

    def save_model(self, request, obj, form, change):
        super(AllplatformsAdminT, self).save_model(request, obj, form, change)
        if not obj.pk:
            if hasattr(obj, 'order') and not obj.order and hasattr(self, 'order_init'):
                obj.order = self._init_order(request)
        else:
            if hasattr(obj, 'order') and hasattr(self, 'auto_sort') and change:
                if not obj.order:
                    return "OrderIsNone"
                self._set_order(request, obj)

        obj.save()


def orginize_inline(tmp_inlines):
    ship_common = "{'order':models.IntegerField()}"
    ship_unicode = "'%s(%s)'"
    inline_raw_id = "{}"
    inlines = []
    for a, b, c in tmp_inlines:
        if isinstance(c, (tuple, list)) and len(c) == 2:
            inlines.append((
                (a, b),
                ("{'order':models.IntegerField(),%s}" % c[1], inline_raw_id),
                ("%s%s" %
                 (ship_unicode, '%' + c[0] % (a.__name__.lower(), b.__name__.lower())),),
            ))
        else:
            inlines.append((
                (a, b),
                (ship_common, inline_raw_id),
                ("%s%s" % (ship_unicode, '%' + c %
                 (a.__name__.lower(), b.__name__.lower())),),
            ))
    return inlines


def allplatformsInline_factory(class_prefix, model_prefix, master_slaver, (ship_attr, inline_attr), (ship_unicode,), filters={}, model=EnhancedAdminInline):
    (ship_model, is_register) = ship_factory(
        master_slaver, ship_unicode, ship_attr)
    slaver_name = master_slaver[1].__name__
    class_attrs = {
        'extra':  1,
        'model': ship_model,
        'inline_slaver_model': '%s%s' % (model_prefix, slaver_name),
        'slaver': slaver_name,
        'ordering': ['order'],
        'auto_sort': True
    }
    if '%s%s' % (model_prefix.lower(), slaver_name) in globals():
        logger.info('exitst!%s' % slaver_name)
    class_attrs.update(filters)
    class_attrs.update(eval(inline_attr))
    class_name = '%s%sinline' % (model_prefix, ship_model.__name__)
    return forms.MediaDefiningClass(class_name, (model,), class_attrs)


def allplatformsAdmin_factory(class_prefix, model_prefix, model, filters, inline=None, foreign_filter={}):

    class_attrs = {
        'form_name': model.__name__,
        'filters': filters,
        '__module__': __name__,
        'foreign_filter': foreign_filter,
    }
    if inline:
        class_attrs.update({'inlines': inline})
    class_name = '%s%s' % (model_prefix, model.__name__)
    return forms.MediaDefiningClass(class_name, (model,), class_attrs)


def custom_register(base_model_admin, filters, class_name, model_name, label_title, inlines=(), foreign_filter=(), foreign_filters=None):
    try:
        inline_dict = {}
        foreign_filter_dict = {}
        inlines = orginize_inline(inlines)
        if foreign_filters is None:
            foreign_filters = filters
        for bind_target, filter_target in foreign_filter:
            tmp_dict = {}
            for key in filter_target:
                tmp_dict.update({key: foreign_filters})
            foreign_filter_dict[bind_target] = tmp_dict

        for (master, slaver), attrs, unicodes in inlines:
            (bind_target, filter_target) = (
                master.__name__, slaver.__name__.lower())
            inline_filter = {'filter_include': {}}
            inline_filter['filter_include'][filter_target] = filters
            admin_inline = allplatformsInline_factory(
                class_name, model_name, (master, slaver), attrs, unicodes, inline_filter)
            if inline_dict.has_key(bind_target):
                inline_dict[bind_target].append(admin_inline)
            else:
                inline_dict[bind_target] = [admin_inline]
        for base_model, base_form in base_model_admin:
            model_class = model_factory(
                class_name, model_name, base_model, string_with_title(*label_title), filters)
            name = base_model.__name__
            para_list = {}
            if name in inline_dict:
                para_list.update({'inline': inline_dict[name]})
            if name in foreign_filter_dict:
                para_list.update({'foreign_filter': foreign_filter_dict[name]})
            model_form = allplatformsAdmin_factory(
                class_name, model_name, base_form, filters, **para_list)
            custom_site.register(model_class, model_form)

    except Exception, e:
        print sys.exc_info()
        logger.error(e)

RESPON_FUN = ('response_change', 'response_add')

for key in DB_SERVERS.keys():
    proxy_func = eval(
        'lambda self,request,queryset: self._sync_mongodb(request,queryset,"%s","upload")' % key)
    setattr(EntityModelAdmin, 'upload_to_%s' % key, proxy_func)
    setattr(EntityModelAdmin.__dict__['upload_to_%s' %
            key], 'short_description', _('publish to %s') % key)

    proxy_func = eval(
        'lambda self,request,queryset: self._sync_mongodb(request,queryset,"%s","delete")' % key)
    setattr(EntityModelAdmin, 'delete_from_%s' % key, proxy_func)
    setattr(EntityModelAdmin.__dict__['delete_from_%s' %
            key], 'short_description', _('delete from %s') % key)

for key in RESPON_FUN:
    proxy_func = eval(
        'lambda self, request, obj, *args, **kwargs: self.manual_response(request, obj, "%s", *args, **kwargs)' % key)
    setattr(AllplatformsAdminT, key, proxy_func)

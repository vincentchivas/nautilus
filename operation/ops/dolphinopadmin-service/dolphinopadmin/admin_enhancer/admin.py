from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils.translation import ugettext_lazy as _

from .widgets import FilteredSelectMultipleWrapper, RelatedFieldWidgetWrapper, CusForeignKeyRawIdWidget


class EnhancedAdminMixin(object):
    enhance_exclude = ()
    filtered_multiple_wrapper = FilteredSelectMultipleWrapper
    related_widget_wrapper = RelatedFieldWidgetWrapper

    def get_dymamic_model_admin(self, base_model, target_model=None, app_label=None):
        cur_model = self.model
        if cur_model:
            if not app_label:
                app_label = cur_model._meta.app_label

            if not target_model:
                target_model = '%s%s' % (
                    self.filters.get('platform'), base_model.capitalize())
            all_models = self.admin_site._registry.keys()
            for model in all_models:
                if model.__name__ == target_model and model._meta.app_label == app_label:
                    return (model, self.admin_site._registry.get(model))

        return None

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """
        Get a form Field for a ForeignKey.
        """
        if hasattr(self, 'foreign_filter') and db_field.name in self.foreign_filter and db_field.name in self.raw_id_fields:
            result = self.get_dymamic_model_admin(db_field.name)
            if result:
                cus_rel = result[0]
                db = kwargs.get('using')
                setattr(db_field.rel, 'cus_rel', cus_rel)
                kwargs['widget'] = CusForeignKeyRawIdWidget(db_field.rel,
                                                            self.admin_site, using=db)
                kwargs['empty_label'] = db_field.blank and _('None') or None

                return db_field.formfield(**kwargs)

        return super(EnhancedAdminMixin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(EnhancedAdminMixin,
                          self).formfield_for_dbfield(db_field, **kwargs)
        if (formfield and db_field.name not in self.enhance_exclude and
                isinstance(formfield.widget, admin.widgets.RelatedFieldWidgetWrapper)):

            request = kwargs.pop('request', None)
            related_modeladmin = None
            cus_rel = None
            if hasattr(self, 'slaver') and db_field.rel.to.__name__ == self.slaver:
                result = self.get_dymamic_model_admin(
                    db_field.name, self.inline_slaver_model, db_field.rel.to._meta.app_label)
                if result:
                    formfield.widget.can_add_related = True
                    cus_rel = result[0]
                    related_modeladmin = result[1]
                #model_key =  self.admin_site._registry.keys()
                #target_label = db_field.rel.to._meta.app_label
                # for i in model_key:
                #    if i.__name__ == target_model and i._meta.app_label == target_label:
                #        formfield.widget.can_add_related = True
                #        cus_rel = i
                         #db_field.rel.to = i
                         # setattr(self.related_widget_wrapper,'cus_rel',i)
                #        related_modeladmin = self.admin_site._registry.get(i)
            if not related_modeladmin:
                related_modeladmin = self.admin_site._registry.get(
                    db_field.rel.to)

            if related_modeladmin:
                can_change_related = related_modeladmin.has_change_permission(
                    request)
                can_delete_related = related_modeladmin.has_delete_permission(
                    request)

                if isinstance(formfield.widget.widget, admin.widgets.FilteredSelectMultiple):
                    formfield.widget.widget = self.filtered_multiple_wrapper.wrap(
                        formfield.widget.widget)
                widget = self.related_widget_wrapper.wrap(formfield.widget,
                                                          can_change_related,
                                                          can_delete_related,
                                                          cus_rel)
                formfield.widget = widget
        return formfield


class EnhancedModelAdminMixin(EnhancedAdminMixin):

    def response_change(self, request, obj):
        if '_popup' in request.REQUEST:
            return render_to_response(
                'admin_enhancer/dismiss-change-related-popup.html',
                {'obj': obj})
        else:
            return super(EnhancedModelAdminMixin, self).response_change(request, obj)

    def delete_view(self, request, object_id, extra_context=None):
        delete_view_response = super(EnhancedModelAdminMixin, self).delete_view(
            request, object_id, extra_context)
        if (request.POST and '_popup' in request.REQUEST and
                isinstance(delete_view_response, HttpResponseRedirect)):
            return render_to_response(
                'admin_enhancer/dismiss-delete-related-popup.html',
                {'object_id': object_id})
        else:
            return delete_view_response

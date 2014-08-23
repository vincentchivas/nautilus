from django.contrib.admin.widgets import (FilteredSelectMultiple,
                                          RelatedFieldWidgetWrapper, ForeignKeyRawIdWidget)
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.contrib.admin.templatetags.admin_static import static
from django.utils.translation import ugettext_lazy as _


class CusForeignKeyRawIdWidget(ForeignKeyRawIdWidget):

    """
    A Widget for displaying ForeignKeys in the "raw_id" interface rather than
    in a <select> box.
    """

    def render(self, name, value, attrs=None):
        if hasattr(self.rel, 'cus_rel'):
            rel_to = self.rel.cus_rel
        else:
            rel_to = self.rel.to
        if attrs is None:
            attrs = {}
        extra = []
        if rel_to in self.admin_site._registry:
            # The related object is registered with the same AdminSite
            related_url = reverse('admin:%s_%s_changelist' %
                                  (rel_to._meta.app_label,
                                   rel_to._meta.module_name),
                                  current_app=self.admin_site.name)

            params = self.url_parameters()
            if params:
                url = u'?' + u'&amp;'.join([u'%s=%s' % (k, v)
                                           for k, v in params.items()])
            else:
                url = u''
            if "class" not in attrs:
                # The JavaScript code looks for this hook.
                attrs['class'] = 'vForeignKeyRawIdAdminField'
            # TODO: "lookup_id_" is hard-coded here. This should instead use
            # the correct API to determine the ID dynamically.
            extra.append(u'<a href="%s%s" class="related-lookup" id="lookup_id_%s" onclick="return showRelatedObjectLookupPopup(this);"> '
                         % (related_url, url, name))
            extra.append(u'<img src="%s" width="16" height="16" alt="%s" /></a>'
                         % (static('admin/img/selector-search.gif'), _('Lookup')))
        output = [super(CusForeignKeyRawIdWidget, self)
                  .render(name, value, attrs)] + extra
        # if value:
            # output.append(self.label_for_value(value))
        return mark_safe(u''.join(output))


class RelatedFieldWidgetWrapper(RelatedFieldWidgetWrapper):

    class Media:
        css = {
            'screen': ('admin_enhancer/css/related-widget-wrapper.css',)
        }
        js = ('admin_enhancer/js/related-widget-wrapper.js',)

    def __init__(self, *args, **kwargs):
        self.can_change_related = kwargs.pop('can_change_related', None)
        self.can_delete_related = kwargs.pop('can_delete_related', None)
        tmp_rel = kwargs.pop('cus_rel', None)
        if tmp_rel:
            setattr(self, 'cus_rel', tmp_rel)
        super(RelatedFieldWidgetWrapper, self).__init__(*args, **kwargs)

    @classmethod
    def wrap(cls, wrapper, can_change_related, can_delete_related, cus_rel):
        return cls(wrapper.widget, wrapper.rel, wrapper.admin_site,
                   can_add_related=wrapper.can_add_related,
                   can_change_related=can_change_related,
                   can_delete_related=can_delete_related,
                   cus_rel=cus_rel)

    def get_related_url(self, rel_to, info, action, args=[]):
        return reverse("admin:%s_%s_%s" % (info + (action,)),
                       current_app=self.admin_site.name, args=args)

    def render(self, name, value, attrs=None, *args, **kwargs):
        if attrs is None:
            attrs = {}
        if hasattr(self, 'cus_rel'):
            rel_to = self.cus_rel
        else:
            rel_to = self.rel.to
        info = (rel_to._meta.app_label, rel_to._meta.object_name.lower())
        self.widget.choices = self.choices
        attrs['class'] = ' '.join(
            (attrs.get('class', ''), 'related-widget-wrapper'))
        context = {
            'widget': self.widget.render(name, value, attrs, *args, **kwargs),
            'name': name,
            'can_change_related': self.can_change_related,
            'can_add_related': self.can_add_related,
            'can_delete_related': self.can_delete_related, }
        if self.can_change_related:
            if value:
                context['change_url'] = self.get_related_url(
                    rel_to, info, 'change', [value])
            template = self.get_related_url(rel_to, info, 'change', ['%s'])
            context.update({'change_url_template': template,
                            'change_help_text': _(u'Change related model'), })
        if self.can_add_related:
            context.update(
                {'add_url': self.get_related_url(rel_to, info, 'add'),
                 'add_help_text': _(u'Add another'), })
        if self.can_delete_related:
            if value:
                context['delete_url'] = self.get_related_url(
                    rel_to, info, 'delete', [value])
            template = self.get_related_url(rel_to, info, 'delete', ['%s'])
            context.update({'delete_url_template': template,
                            'delete_help_text': _(u'Delete related model'), })

        return mark_safe(render_to_string('admin_enhancer/related-widget-wrapper.html', context))


class FilteredSelectMultipleWrapper(FilteredSelectMultiple):

    @classmethod
    def wrap(cls, widget):
        return cls(widget.verbose_name, widget.is_stacked,
                   widget.attrs, widget.choices)

    def render(self, *args, **kwargs):
        output = super(FilteredSelectMultipleWrapper,
                       self).render(*args, **kwargs)
        return mark_safe("<div class=\"related-widget-wrapper\">%s</div>" % output)

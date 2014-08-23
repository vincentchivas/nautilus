from django.contrib import admin
from django.contrib.admin.models import ADDITION, CHANGE, DELETION
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.utils.translation import ugettext_lazy as _
from dolphinopadmin.usermanagement.models import GroupManagement, UserManagement, CustomLogEntry
from dolphinopadmin.base.base_admin import AllplatformsAdminT
from dolphinopadmin.utils.sites import custom_site

_LOG_ACTIONS = {
    ADDITION: _('addition action(1)'),
    CHANGE: _('change action(2)'),
    DELETION: _('deletion action(3)'),
    3: _('online(3)'),
    4: _('offline(4)'),
    5: _('login(5)')
}


class CustomAuthAdmin(admin.ModelAdmin):

    def __init__(self, model, admin_site):
        self.has_change = False
        super(CustomAuthAdmin, self).__init__(model, admin_site)

    def get_model_perms(self, request):
        perms = super(CustomAuthAdmin, self).get_model_perms(request)
        perms.update({'view': self.has_view_permission(request)})
        return perms

    def changelist_view(self, request, extra_context=None):
        if self.has_view_permission(request, None):
            self.has_change = True
        if not extra_context:
            extra_context = {}
        extra_context.update({'has_change_permission': request.user.has_perm(self.opts.app_label +
                                                                             '.' + self.opts.get_change_permission())})
        result = super(CustomAuthAdmin, self).changelist_view(
            request, extra_context=extra_context)
        self.has_change = False
        return result

    def has_view_permission(self, request, obj=None):
        opts = self.opts
        view_permission = 'view_%s' % self.model._meta.module_name
        return request.user.has_perm(opts.app_label + '.' + view_permission)

    def has_change_permission(self, request, obj=None):
        if getattr(self, 'has_change', False):
            return True
        return super(CustomAuthAdmin, self).has_change_permission(request, obj)

    def change_view(self, request, object_id, extra_context=None):
        if self.has_view_permission(request, None):
            self.has_change = True
        result = super(CustomAuthAdmin, self).change_view(
            request, object_id, extra_context=extra_context)
        self.has_change = False
        return result

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        old_has_change = self.has_change
        self.has_change = False
        context.update({'has_sync_to_permission': False})
        result = super(
            CustomAuthAdmin, self).render_change_form(request, context, add=add,
                                                      change=change, form_url=form_url, obj=obj)
        if old_has_change:
            self.has_change = True
        return result


class LogEntryAdmin(AllplatformsAdminT):

    list_display = ('user', 'object_belong', 'object_repr',
                    'object_id', 'action_time', 'display_action_flag', 'change_message')
    list_filter = ('user', 'action_flag', 'action_time')
    readonly_fields = ('user', 'content_type', 'object_id',
                       'object_repr', 'action_time', 'action_flag', 'change_message')
    list_per_page = 50
    search_fields = ['user__username',
                     'content_type__name', 'object_id', 'object_repr']

    def has_add_permission(self, request, obj=None):
        return False

    def display_action_flag(self, obj):
        return _LOG_ACTIONS[obj.action_flag]
    display_action_flag.short_description = _('action flag')

    actions = ['export_select_data']
    # def get_actions(self, request):
    #    actions = super(LogEntryAdmin, self).get_actions(request)
    #    actions['export_select_data'] = (self.export_select_data, 'export_select_data', unicode(_('export select data')))
        # actions.append('export_select_data')
    #    return actions


class CustomUserAdmin(UserAdmin, CustomAuthAdmin):
    pass


class CustomGroupAdmin(GroupAdmin, CustomAuthAdmin):
    pass

custom_site.register(CustomLogEntry, LogEntryAdmin)
custom_site.register(GroupManagement, CustomGroupAdmin)
custom_site.register(UserManagement, CustomUserAdmin)

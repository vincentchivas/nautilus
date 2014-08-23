from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext as _

from dolphinopadmin.utils import string_with_title


class CustomLogEntry(LogEntry):

    def object_belong(self):
        if self.content_type:
            return '%s-%s' % (self.content_type.app_label, self.content_type.name)
    object_belong.verbose_name = _('object belong')

    class Meta:
        proxy = True
        app_label = string_with_title("usermanagement", _("User Management"))
        verbose_name = _('operator log')
        verbose_name_plural = _('operator log')


class GroupManagement(Group):

    class Meta:
        proxy = True
        app_label = string_with_title("usermanagement", _("User Management"))
        verbose_name = _("Group")
        verbose_name_plural = _("Groups")


class UserManagement(User):

    class Meta:
        proxy = True
        app_label = string_with_title("usermanagement", _("User Management"))
        verbose_name = _("User")
        verbose_name_plural = _("Users")

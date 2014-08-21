from django.conf.urls.defaults import patterns  # , include

from provisionadmin.service.views import views_list
from provisionadmin.service.views import views_add
from provisionadmin.service.views import views_edit
from provisionadmin.service.views import views_export, views_module
from provisionadmin.service.views import views_revision
from provisionadmin.service.views import stat_report
from provisionadmin.service.views import views_export_v2

urlpatterns = patterns(
    'provisionadmin.service.views',

    (r'^upload', 'apk.upload'),
    (r'^download', 'apk.download'),
    (r'^build', 'apk.build'),
    (r'^i18n/translation/add', views_add.task_add),
    (r'^i18n/translation/edit/marked', views_edit.mark_cope),
    (r'^i18n/translation/edit', views_edit.edit),
    (r'^i18n/translation/export/xml', views_list.export_task_xml),
    (r'^i18n/translation/export/rawxml2', views_export_v2.export_raw_xml),
    (r'^i18n/translation/export/list', views_export_v2.export_list),
    (r'^i18n/translation/export/rawxml', views_export.export_raw_xml),
    (r'^i18n/translation/export', views_export.export),
    (r'^i18n/translation/modules', views_module.get_modules),
    (r'^i18n/translation/list', views_list.show_list),
    (r'^i18n/revision/download', views_revision.export_revision_xml),
    (r'^i18n/revision', views_revision.show_snap),
    (r'^login', 'user.login'),
    (r'^logout', 'user.logout'),
    (r'^auth/user/add', 'user.add_user'),
    (r'^auth/user/(?P<user_id>[1-9]\d*)', 'user.user_detail_modify'),
    (r'^auth/user/delete', 'user.del_user'),
    (r'^auth/user/list', 'user.user_list'),
    (r'^auth/group/add', 'user.add_group'),
    (r'^auth/group/(?P<group_id>[1-9]\d*)', 'user.group_detail_modify'),
    (r'^auth/group/delete', 'user.del_group'),
    (r'^auth/group/list', 'user.group_list'),
    (r'^auth/perm/add', 'user.add_perm'),
    (r'^auth/perm/(?P<perm_id>[1-9]\d*)', 'user.perm_detail_modify'),
    (r'^auth/perm/delete', 'user.del_perm'),
    (r'^auth/perm/list', 'user.perm_lsit'),
    (r'^changepwd', 'user.change_password'),
    (r'^report/provision_analysis', stat_report.report_locale)
)

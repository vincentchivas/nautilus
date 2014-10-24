from django.conf.urls.defaults import patterns  # , include
from django.views import static

from provisionadmin.service.views import views_list
from provisionadmin.service.views import views_add
from provisionadmin.service.views import views_edit
from provisionadmin.service.views import views_module
from provisionadmin.service.views import views_history
from provisionadmin.service.views import stat_report
from provisionadmin.service.views import views_export
from provisionadmin.service.views import views_build
from provisionadmin.service.views import build_list
from provisionadmin.service.views import handle_task
from provisionadmin.service.views import submit_strings
from provisionadmin.service.views import init_xml

urlpatterns = patterns(
    'provisionadmin.service.views',
    (r'^media/(?P<path>.*)$', static.serve,
        {'document_root': '/var/app/data/provisionadmin-service/images'}),
    (r'^upload/build/(?P<path>.*)', static.serve,
        {'document_root': '/var/app/data/provisionadmin-service/'}),
    (r'^xls/upload', 'upload_xls.upload_xls_file'),
    (r'^upload', 'apk.upload'),
    (r'^download', 'apk.download'),
    (r'^build', 'apk.build'),
    (r'^translation-tool/translations/list', views_list.show_list),
    (r'^translation-tool/translations/add', views_add.task_add),
    (r'^translation-tool/translations/send-email',
        views_list.submit_translation_content),
    (r'^translation-tool/translations/assign/task', views_list.assign_task),
    (r'^translation-tool/translations/check/task', handle_task.check_task),
    (r'^translation-tool/translations/lock/task', handle_task.lock_task),
    (r'^translation-tool/strings/list', views_edit.get_strings),
    (r'^translation-tool/strings/save', views_edit.save_strings),
    (r'^translation-tool/strings/submit', submit_strings.submit_strings),
    (r'^translation-tool/strings/marked', views_edit.mark_cope),
    (r'^translation-tool/strings/list', views_edit.get_strings),
    (r'^translation-tool/strings/save', views_edit.save_strings),
    (r'^translation-tool/string/update', submit_strings.update_strings),
    (r'^modules', views_module.get_modules),
    (r'^translation-tool/last-build/list', build_list.get_project_info),
    (r'^translation-tool/last-build/kill', build_list.cancel_project),
    (r'^translation-tool/last-build/delete', build_list.delete_project),
    (r'^translation-tool/last-build/retry', views_build.create_project),
    (r'^translation-tool/last-build/warning', build_list.lint_message),
    (r'^translation-tool/update/status', build_list.update_project_status),
    (r'^translation-tool/activity', views_history.history_list),
    (r'^data-manage/exportxml/list', views_export.export_list),
    (r'^data-manage/exportxml/rawxml', views_export.export_raw_xml),
    (r'^get/latest-data', init_xml.init_xml_file),
    (r'^user/feedback', 'feedback.trans_comment'),
    (r'^project/list', views_build.project_list),
    (r'^project/create', views_build.create_project),
    (r'^init/app/tag', views_build.init_tag),
    (r'^login', 'user.login'),
    (r'^logout', 'user.logout'),
    (r'^auth/user/add', 'user.create_user'),
    (r'^auth/user/(?P<user_id>[1-9]\d*)', 'user.detail_modify_user'),
    (r'^auth/user/delete', 'user.delete_user'),
    (r'^auth/user/list', 'user.list_user'),
    (r'^auth/group/add', 'user.create_group'),
    (r'^auth/group/(?P<group_id>[1-9]\d*)', 'user.detail_modify_group'),
    (r'^auth/group/delete', 'user.delete_group'),
    (r'^auth/group/list', 'user.list_group'),
    (r'^auth/perm/add', 'user.create_perm'),
    (r'^auth/perm/(?P<perm_id>[1-9]\d*)', 'user.detail_modify_perm'),
    (r'^auth/perm/delete', 'user.delete_perm'),
    (r'^auth/perm/list', 'user.list_perm'),
    (r'^auth/user/active', 'user.user_active'),
    (r'^auth/user/permissions', 'user.user_perm_list'),
    (r'^auth/group/permissions', 'user.group_perm_list'),
    (r'^auth/actionlog/list', 'user.action_log_list'),
    (r'^changepwd', 'user.change_password'),
    (r'^provision-service/provision_analysis', stat_report.report_locale),
    (r'^provision-service/detail_analysis', stat_report.get_detail_data),
    (r'^bookmark/add', 'preset.bookmark_add')
)

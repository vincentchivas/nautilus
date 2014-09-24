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
from provisionadmin.service.views import views_errorlog
from provisionadmin.utils import init_xml

urlpatterns = patterns(
    'provisionadmin.service.views',

    (r'^upload/build/(?P<path>.*)', static.serve,
        {'document_root': '/var/app/data/provisionadmin-service/'}),
    (r'^upload', 'apk.upload'),
    (r'^download', 'apk.download'),
    (r'^build', 'apk.build'),
    (r'^translation-tool/translations/add', views_add.task_add),
    (r'^translation-tool/string/marked', views_edit.mark_cope),
    (r'^translation-tool/string/list', views_edit.edit),
    (r'^translation-tool/translations/send-email', views_list.submit_xml_info),
    (r'^specification/exportxml/rawxml', views_export.export_raw_xml),
    (r'^specification/exportxml/list', views_export.export_list),
    (r'^modules', views_module.get_modules),
    (r'^translation-tool/translations/list', views_list.show_list),
    (r'^translation-tool/activity', views_history.history_list),
    (r'^translation-tool/last-build/list', build_list.get_project_info),
    (r'^translation-tool/last-build/kill', build_list.cancel_project),
    (r'^translation-tool/last-build/delete', build_list.delete_project),
    (r'^translation-tool/last-build/retry', views_build.create_project),
    (r'^translation-tool/update/status', build_list.update_project_status),
    (r'^get/latest-data', init_xml.init_xml_file),
    (r'^specification/errorlog/list', views_errorlog.errorlog),
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
    (r'^changepwd', 'user.change_password'),
    (r'^report/provision_analysis', stat_report.report_locale),
    (r'^report/detail_analysis', stat_report.get_detail_data)
)

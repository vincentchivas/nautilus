def enum(**enums):
    return type('Enum', (), enums)

Method = enum(GET="GET", POST="POST")


class Perm_Sys(object):
    # views/user.py api
    user_list_group = {Method.GET: ["auth-groups-list"]}
    user_create_group = {Method.POST: ["auth-groups-add"]}
    user_detail_modify_group = {
        Method.GET: ["auth-groups-list"],
        Method.POST: ["auth-groups-edit"]}
    user_delete_group = {Method.POST: ["auth-groups-delete"]}

    user_list_user = {Method.GET: ["auth-user-list"]}
    user_create_user = {Method.POST: ["auth-user-add"]}
    user_detail_modify_user = {
        Method.GET: ["auth-user-list"],
        Method.POST: ["auth-user-edit"]}
    user_delete_user = {Method.POST: ["auth-user-delete"]}

    user_list_perm = {Method.GET: ["auth-permission-list"]}

    # i18n
    views_add_task_add = {
        Method.GET: ["translation-tool-translations-add"],
        Method.POST: ["translation-tool-translations-add"]}
    submit_strings_submit_strings = {Method.POST: ["string-submit"]}
    views_edit_mark_cope = {Method.POST: ["mark-cope"]}
    views_edit_get_strings = {
        Method.GET: ["translation-tool-strings-list"]}
    views_edit_save_strings = {
        Method.POST: ["translation-tool-strings-edit"]}
    views_list_submit_translation_content = {
        Method.POST: ["send-mail-xmlinfo"]}

    views_list_assign_task = {
        Method.GET: ["assign-to-translator"],
        Method.POST: ["assign-to-translator"]}

    handle_task_check_task = {
        Method.POST: ["country-manager-check"]}

    handle_task_lock_task = {
        Method.POST: ["admin-lock-unlock"]}

    views_export_export_raw_xml = {Method.GET: ["export-xml"]}
    views_export_export_list = {
        Method.GET: ["data-manage-exportxml-list"]}
    views_list_show_list = {Method.GET: ["translation-tool-translations-list"]}
    views_history_history_list = {
        Method.GET: ["translation-tool-activity-list"]}
    build_list_get_project_info = {
        Method.GET: ["translation-tool-last-build-list"]}
    build_list_cancel_project = {
        Method.GET: ["translation-tool-last-build-delete"]}
    build_list_delete_project = {
        Method.GET: ["translation-tool-last-build-delete"]}
    init_xml_init_xml_file = {Method.GET: ["get-latest-data"]}
    views_errorlog_errorlog = {Method.GET: ["data-manage-errorlog-list"]}
    views_build_project_list = {Method.GET: ["project-list"]}
    views_build_create_project = {Method.GET: ["build-project"]}
    views_module_get_modules = {Method.GET: ["get-modules"]}
    # stability

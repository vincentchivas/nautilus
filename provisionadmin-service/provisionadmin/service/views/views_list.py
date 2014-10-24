# -*-coding: utf-8 -*-

import os
import simplejson as json

from django.conf import settings

from provisionadmin.utils.json import json_response_error, json_response_ok
from provisionadmin.utils.respcode import PARAM_REQUIRED, METHOD_ERROR, \
    DATA_ERROR, DB_ERROR
from provisionadmin.model.i18n import LocalizationTask, LocalizationConfig, \
    LocalizationInfo, LocalizationStrings
from provisionadmin.model.user import User
from provisionadmin.utils.util_mail import send_message
from provisionadmin.decorator import check_session, exception_handler
from provisionadmin.service.views.all_json import list_filters


TEMPLATE_ROOT = settings.CUS_TEMPLATE_DIR


@exception_handler()
@check_session
def show_list(request, user):
    """
    Get translation task list by user id
    Parameters:
        -appname: package name,
        -appversion: package version,
        -status: the status of task,
    Return:
        -1. The lists of the translation task
        {
            "status": 0,
            "data":{
                ...
            }
         }
        -2. error http method
        {
            "status": 11,
            "data":{
                ...
            }
         }
    """
    if request.method == 'GET':
        uid = user.get("_id")
        role = user.get("group_id")[0]
        platform = request.GET.get("platform")
        appname = request.GET.get("appname")
        category = request.GET.get("category")
        appversion = request.GET.get("appversion")
        status = request.GET.get("status", "")

        data = {}
        data["filters"] = _get_list_filter()
        if platform is None:
            platform_value = data["filters"]["items"][0]
            platform = platform_value.get("value")
            appname_value = platform_value["children"]["items"][0]
            appname = appname_value.get("value")
            category_value = appname_value["children"]["items"][0]
            category = category_value.get("value")
            version_value = category_value["children"]["items"][0]
            appversion = version_value.get("value")
        temp_data = LocalizationTask.get_all_task(
            platform, category, appname, appversion, uid, role,
            status, sort=[("created_at", -1)])
        data["items"] = get_task(temp_data)
        data["role"] = role
        return json_response_ok(data)
    else:
        return json_response_error(METHOD_ERROR, msg="http method wrong")


@exception_handler()
@check_session
def assign_task(request, user):
    """
    Assign translation task to translator
    Parameters:
        -appname: package name,
        -appversion: package version,
        -status: the status of task,
    Return:
        -1. The lists of the translation task
        {
            "status": 0,
            "data":{
                ...
            }
         }
        -2. error http method
        {
            "status": 11,
            "data":{
                ...
            }
         }
    """
    if request.method == 'GET':
        uid = user.get("_id")
        department = user.get("department")
        required_list = (
            'platform', 'appname', 'category', 'appversion', 'locale')
        for required_para in required_list:
            para_data = request.GET.get(required_para)
            if not para_data:
                return json_response_error(
                    PARAM_REQUIRED,
                    msg="parameter '%s' invalid" % required_para)
        translator_info = User.get_charge_info(department)[1]
        data = {"translator_info": []}
        data["translator_info"] = translator_info
        return json_response_ok(data)
    elif request.method == 'POST':
        uid = user.get("_id")
        department = user.get("department")
        role = user.get("group_id")[0]
        data = {}
        assign_info = request.raw_post_data
        assign_info = json.loads(assign_info)
        data["platform"] = assign_info.get("platform")
        appname = data["appname"] = assign_info.get("appname")
        data["category"] = assign_info.get("category")
        appversion = data["appversion"] = assign_info.get("appversion")
        locale = data["locale"] = assign_info.get("locale")
        translator_info = assign_info.get("translator_info")

        status = LocalizationTask.assign_task(data, uid, role, translator_info)
        if not status:
            return json_response_error(DATA_ERROR, msg="The task is locked")
        # send email
        _send_email_to_translator(appname, appversion, locale, department)
        data["assign"] = True
        return json_response_ok(data)
    else:
        return json_response_error(METHOD_ERROR, msg="http method wrong")


def get_task(ret_task):
    """
    Formatting task information
    Parameters:
        -ret_task: array of task information,
    Return:
        -items: processed task  information
    """
    items = []
    for i in ret_task:
        temp = {}
        temp['platform'] = i["target"]["platform"]
        temp['appname'] = i["target"]["appname"]
        temp['category'] = i["target"]["category"]
        temp['appversion'] = i["target"]["appversion"]
        locale = i["target"]["locale"]
        temp['locale'] = locale
        if temp['locale'] == "":
            continue
        locale_language = LocalizationConfig.get_locale_info(
            temp["appname"], temp["appversion"], locale).get("language")
        temp['display_locale'] = "%s(%s)" % (locale_language, locale)
        if i["task_status"] == "Created":
            temp['task_status'] = "Translating"
        else:
            temp['task_status'] = i["task_status"]

        if temp['task_status'] == "Translating":
            temp["left_count"] = i["strings"]["untranslated"]
        elif temp["task_status"] == "To be check":
            temp["left_count"] = i["strings"]["uncheck"]
        else:
            temp["left_count"] = 0

        temp['is_send_email'] = False if i.get("is_send_email") \
            is None else i.get("is_send_email")
        temp['is_assign'] = False if i.get("translator_id") \
            is None else True if i.get("translator_id") else False
        temp['is_checked'] = True if i.get("task_status") == "Finished" \
            else False
        temp['is_locked'] = i.get("is_locked")
        temp['autofill'] = True if i.get("autofill") is None \
            else i.get("autofill")
        if i["reference"]:
            r_locale = i["reference"]["locale"]
            refer_language = LocalizationConfig.get_locale_info(
                temp["appname"], temp["appversion"], r_locale).get("language")
            temp['display_refer'] = "%s(%s)" % (
                refer_language, r_locale if r_locale else 'us')
        else:
            temp['display_refer'] = None
        items.append(temp)
    return items


@exception_handler(as_json=False)
@check_session
def submit_translation_content(request, user):
    """
    Send email to response management after completet translation task
    Parameters:
        -appname: package name,
        -appversion: package version,
        -locale: Country code,
        -display_locale: The name of the locale displayed on the page
    Return:
        -1.successful send email
        {
            "status": 0,
            "data":{
                ...
            }
         }
        -2. error http method
        {
            "status": 11,
            "data":{
                ...
            }
         }
    """
    if request.method == 'POST':
        data = {"is_send_email": False}
        submit_info = request.raw_post_data
        submit_info = json.loads(submit_info)
        required_list = (
            'platform', 'appname', 'category', 'appversion',
            'display_locale', 'locale')
        for required_para in required_list:
            para_data = submit_info.get(required_para)
            if not para_data:
                return json_response_error(
                    PARAM_REQUIRED,
                    msg="parameter '%s' invalid" % required_para)
        department = user.get("department")
        appname = submit_info.get('appname')
        appversion = submit_info.get('appversion')
        locale = submit_info.get('locale')
        display_locale = submit_info.get('display_locale')

        target_cond = submit_info
        target_cond.pop("display_locale")

        info_id = LocalizationInfo.find_id_by_unique(target_cond)

        fields = {"strings": 1, "_id": 0, "task_status": 1, "is_send_email": 1}
        task_info = LocalizationTask.find(
            {"target": info_id}, fields, one=True)
        if not task_info:
            return json_response_error(DB_ERROR, msg="this task not in db")
        task_status = task_info.get("task_status")
        untrans_count = task_info["strings"]["untranslated"]
        if task_status == "Translating" and untrans_count != 0:
            return json_response_error(
                DATA_ERROR, msg="The task is not finished")
        if task_info["is_send_email"]:
            return json_response_error(
                DATA_ERROR, msg="The email is alreay sended")
        LocalizationTask.update(
            {"target": info_id},
            {"is_send_email": True, "task_status": "To be check"})

        LocalizationStrings.update(
            {"localization_info": info_id, "status": "Translated"},
            {"status": "To be check"}, multi=True)
        LocalizationTask.update_finish_count(info_id)

        _send_email_to_countrypm(
            appname, appversion, locale, display_locale, department)

        data["is_send_email"] = True
        return json_response_ok(data)
    else:
        return json_response_error(METHOD_ERROR, msg="http method wrong")


def _send_email_to_countrypm(
        appname, appversion, locale, display_locale, department):
    """
    When translator completed task, send an email to country pm to check
    Parameters:
        -appname: package name,
        -appversion: package version,
        -locale: Country code,
        -display_locale: The name of the locale displayed on the page
    Return:
        -None
    """
    subject = u"Completed task 【%s】" % display_locale
    mail_to = User.get_charge_info(department)[2]
    mail_to = ["yqyu@bainainfo.com"]
    mail_cc = ['bhuang@bainainfo.com']
    mail_cc.append('nqi@bainainfo.com')
    template = os.path.join(TEMPLATE_ROOT, "finish_task.html")
    name_version = appname + " V" + appversion
    send_message(
        subject, template, mail_to, mail_cc, False, None,
        name_version, display_locale)


def _send_email_to_translator(
        platform, appname, category, appversion, locale, department):
    """
    Sene e-mail to translator
    Parameters:
        -appname: package name,
        -appversion: package version,
        -locale: Country code,
        -display_locale: The name of the locale displayed on the page
    Return:
        -None
    """
    app_info = LocalizationConfig.get_locale_info(
        appname, appversion, locale)
    locale_language = app_info.get("language")
    display_locale = "%s(%s)" % (locale_language, locale)
    subject = u"Translation task 【%s %s】" % (appname, appversion)
    mail_to = User.get_charge_info(department)[1]
    mail_to = ["yqyu@bainainfo.com"]
    mail_cc = ['bhuang@bainainfo.com']
    mail_cc.append('nqi@bainainfo.com')
    template = os.path.join(TEMPLATE_ROOT, "create_task.html")
    name_version = appname + " V" + appversion
    info_cond = {
        'platform': platform, 'category': category,
        'appname': appname, 'appversion': appversion,
        'locale': locale}
    info_id = LocalizationInfo.find_id_by_unique(info_cond)
    strings = LocalizationTask.find({"target": info_id}, one=True)
    left_count = strings["strings"]["draft"]
    send_message(
        subject, template, mail_to, mail_cc, False, None, name_version,
        display_locale, left_count)


def _get_list_filter():
    """
    Filter of the translation list page
    Parameters:
        -None
    Return:
        -The lists of translation list filter
        {
            "name": "appname",
            "items":[
                ...
            ]
         }
    """
    filters = {"name": "platform", "items": []}
    platform_list = LocalizationInfo.find(
        {"locale": ""}, {"platform": 1, "_id": 0}, toarray=True)
    if not platform_list:
        return json_response_error(DATA_ERROR, msg="no app in db")
    platform_list = _delete_duplicate_ele(platform_list)

    for plat_item in platform_list:
        plat_children = {"name": "appname", "items": []}
        plat_dict = {"display_value": "", "value": "", "children": {}}
        plat_name = plat_item.get("platform")
        appname_list = LocalizationInfo.find(
            {"platform": plat_name, "locale": ""},
            {"appname": 1, "_id": 0}, toarray=True)
        appname_list = _delete_duplicate_ele(appname_list)
        for app_item in appname_list:
            appname_children = {"name": "category", "items": []}
            name_dict = {"display_value": "", "value": "", "children": {}}
            app_name = app_item.get("appname")
            category_list = LocalizationInfo.find(
                {"platform": plat_name, "locale": "", "appname": app_name},
                {"category": 1, "_id": 0}, toarray=True)
            category_list = _delete_duplicate_ele(category_list)
            for cate_item in category_list:
                category_children = {"name": "appversion", "items": []}
                cate_dict = {"display_value": "", "value": "", "children": {}}
                cate_name = cate_item.get("category")
                app_version = LocalizationInfo.get_by_app_version(
                    app_name, plat_name, cate_name).get("appversion")
                for version in app_version:
                    version_items = {
                        "display_value": "", "value": "", "children": {}}
                    version_items["display_value"] = version
                    version_items["children"] = list_filters
                    version_items["value"] = version
                    category_children["items"].append(version_items)
                cate_dict["display_value"] = cate_name
                cate_dict["value"] = cate_name
                cate_dict["children"] = category_children
                appname_children["items"].append(cate_dict)
            name_dict["display_value"] = app_name
            name_dict["value"] = app_name
            name_dict["children"] = appname_children
            plat_children["items"].append(name_dict)
        plat_dict["display_value"] = plat_name
        plat_dict["value"] = plat_name
        plat_dict["children"] = plat_children
        filters["items"].append(plat_dict)
    return filters


def _delete_duplicate_ele(temp_list):
    func = lambda x, y: x if y in x else x + [y]
    temp_list = reduce(func, [[], ] + temp_list)
    return temp_list

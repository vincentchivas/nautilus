# -*-coding: utf-8 -*-

import os

from django.conf import settings

from provisionadmin.utils.json import json_response_error, json_response_ok
from provisionadmin.utils.respcode import PARAM_REQUIRED, METHOD_ERROR, \
    DATA_ERROR
from provisionadmin.model.i18n import LocalizationTask, LocalizationConfig, \
    LocalizationInfo, MailConfig
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
        appname = request.GET.get("appname")
        appversion = request.GET.get("appversion")
        status = request.GET.get("status")
        data = {}
        data["filters"] = _get_list_filter()
        if appname is None:
            appname_value = data["filters"]["items"][0]
            appname = appname_value.get("value")
            version_value = appname_value["children"]["items"][0]
            appversion = version_value.get("value")
        temp_data = LocalizationTask.get_all_task(
            appname, appversion, status, sort=[("created_at", -1)])
        data["items"] = get_task(temp_data)
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
    for item_task in ret_task:
        temp = {}
        temp['appname'] = item_task["target"]["appname"]
        temp['appversion'] = item_task["target"]["appversion"]
        locale = item_task["target"]["locale"]
        temp['locale'] = locale
        temp['autofill'] = True if item_task.get("autofill") is None \
            else item_task.get("autofill")
        temp['is_send_email'] = False if item_task.get("is_send_email") \
            is None else item_task.get("is_send_email")
        if temp['locale'] == "":
            continue
        locale_language = LocalizationConfig.get_locale_info(
            temp["appname"], temp["appversion"], locale).get("language")
        temp['display_locale'] = "%s(%s)" % (locale_language, locale)
        if item_task["reference"]:
            r_locale = item_task["reference"]["locale"]
            refer_language = LocalizationConfig.get_locale_info(
                temp["appname"], temp["appversion"], r_locale).get("language")
            temp['display_refer'] = "%s(%s)" % (
                refer_language, r_locale if r_locale else 'us')
        else:
            temp['display_refer'] = None
        left_count = item_task["strings"]["total"] - \
            item_task["strings"]["finished"]
        if left_count > 0:
            status = "draft"
        else:
            status = "finished"
        temp['status'] = status
        temp['left_count'] = left_count
        items.append(temp)
    return items


@exception_handler(as_json=False)
@check_session
def submit_xml_info(request, user):
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
    if request.method == 'GET':
        data = {"is_send_email": False}
        if request.method == 'GET':
            required_list = (
                'appname', 'appversion', 'display_locale', 'locale')
            for required_para in required_list:
                para_data = request.GET.get(required_para)
                if not para_data:
                    return json_response_error(
                        PARAM_REQUIRED,
                        msg="parameter '%s' invalid" % required_para)
        appname = request.GET.get('appname')
        appversion = request.GET.get('appversion')
        locale = request.GET.get('locale')
        display_locale = request.GET.get('display_locale')

        info_id = LocalizationInfo.get_by_app_locale(
            appname, appversion, locale, id_only=True)
        LocalizationTask.update(
            {"target": info_id}, {"is_send_email": True})

        _send_translate_email(appname, appversion, locale, display_locale)

        data["is_send_email"] = True
        return json_response_ok(data)
    else:
        return json_response_error(METHOD_ERROR, msg="http method wrong")


def _send_translate_email(appname, appversion, locale, display_locale):
    """
    Get e-mail list by appname & appversion & locale
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
    country = app_info.get("language")
    subject = u"Completion task 【%s】" % display_locale
    mail_to, mail_cc = MailConfig.get_mailto_by_country(country)
    mail_to = ["yqyu@bainainfo.com", 'lhhuang@bainainfo.com']
    mail_cc = ['bhuang@bainainfo.com', 'jyqiu@bainainfo.com']
    template = os.path.join(TEMPLATE_ROOT, "finish_task.html")
    name_version = appname + " V" + appversion
    send_message(
        subject, template, mail_to, mail_cc, False, None,
        name_version, display_locale)


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
    filters = {"name": "appname", "items": []}
    appname_list = LocalizationInfo.find(
        {"locale": ""}, {"appname": 1, "_id": 0}, toarray=True)
    func = lambda x, y: x if y in x else x + [y]
    appname_list = reduce(func, [[], ] + appname_list)
    if not appname_list:
        return json_response_error(DATA_ERROR, msg="no app in db")
    for app_item in appname_list:
        items_dict = {"display_value": "", "value": "", "children": {}}
        app_name = app_item.get("appname")
        app_version = LocalizationInfo.get_by_app_version(
            app_name).get("appversion")
        appname_children = {"name": "appversion", "items": []}
        for version in app_version:
            version_items = {"display_value": "", "value": "", "children": {}}
            version_items["display_value"] = version
            version_items["children"] = list_filters
            version_items["value"] = version
            appname_children["items"].append(version_items)
        items_dict["display_value"] = app_name
        items_dict["value"] = app_name
        items_dict["children"] = appname_children
        filters["items"].append(items_dict)
    return filters

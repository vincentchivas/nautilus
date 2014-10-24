# -*- coding: utf-8 -*-
"""
@author: yqyu
@date: 2014-07-15
@description: Create translation task
"""

import os

from django.conf import settings

from provisionadmin.model.user import User
from provisionadmin.utils.respcode import DB_ERROR, \
    METHOD_ERROR, DATA_ERROR
from provisionadmin.utils.json import json_response_error, json_response_ok
from provisionadmin.decorator import check_session, exception_handler
from provisionadmin.model.i18n import LocalizationInfo, LocalizationTask, \
    LocalizationConfig, MailConfig
from provisionadmin.utils.util_mail import send_message
from provisionadmin.service.views.views_list import _delete_duplicate_ele
import simplejson as json


TEMPLATE_ROOT = settings.CUS_TEMPLATE_DIR
_ADMIN = 2


@exception_handler()
@check_session
def task_add(request, user):
    """
    GET: Get candidate tasks need to be translated
    Parameters:
        -appname: package name,
        -appversion: package version,
        -locale: Country code,

    POST: Save the translation document
    Parameters:
        -json: the information of translated string,
    Return:
        -1. The lists of text need to translated
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
        data = {}
        uid = user.get("_id")
        data = _get_task_list(uid)
        return json_response_ok(data)
    elif request.method == 'POST':
        uid = user.get("_id")
        role = user.get("group_id")[0]
        department = user.get("department")

        dict_str = request.raw_post_data
        insert_data = {}
        temp_dict = json.loads(dict_str)
        platform = insert_data["platform"] = temp_dict["platform"]
        appname = insert_data["appname"] = temp_dict["appname"]
        category = insert_data["category"] = temp_dict["category"]
        appversion = insert_data["appversion"] = temp_dict["appversion"]
        locale = insert_data["locale"] = temp_dict["locale"]

        if role == _ADMIN:
            app_info = LocalizationConfig.get_locale_info(
                appname, appversion, locale)
            department = app_info.get("country")

        insert_info = dict(insert_data)
        insert_data["autofill"] = temp_dict.get("autofill")
        if temp_dict.get("reference") == 'us':
            insert_data["reference"] = ""
        else:
            insert_data["reference"] = temp_dict.get("reference")
        uid = user.get("_id")
        department = user.get("department")
        insert_data['creator_id'] = uid
        assign_info = User.get_charge_info(department)[0]
        insert_data['assign_id'] = assign_info.get("_id")
        info_id = LocalizationInfo.insert(insert_info, get=True)
        if not info_id:
            return json_response_error(
                DB_ERROR, msg='create localizationinfo failed!')
        LocalizationTask.insert_task(insert_data)

        # send email
        _send_email_to_charge(platform, appname, category, appversion, locale)

        return json_response_ok()
    else:
        return json_response_error(METHOD_ERROR, msg="http method wrong")


def _process_locales(locales):
    """
    process country code like this:Arabic(ar)
    Parameters:
        -None
    Return:
        -The lists of processed locales
        [
           {
            "value": "ar",
            "display_value": "Arabic(ar)"
           },
        ]
    """
    ret_locales = []
    for locale_item in locales:
        new_l = {
            'value': locale_item['locale'] if locale_item['locale'] else "us",
            'display_value': "%s(%s)" % (
                locale_item['language'],
                locale_item['locale'] if locale_item['locale'] else "us")}
        ret_locales.append(new_l)
    return ret_locales


def _send_email_to_charge(platform, appname, category, appversion, locale):
    """
    Get e-mail list by appname & appversion & locale
    Parameters:
        -appname: package name,
        -appversion: package version,
        -locale: Country code,
    Return:
        -None
    """
    app_info = LocalizationConfig.get_locale_info(
        appname, appversion, locale)
    locale_language = app_info.get("language")
    display_locale = "%s(%s)" % (locale_language, locale)
    subject = u"Assign task 【%s %s】" % (appname, appversion)
    mail_to, mail_cc = MailConfig.get_mailto_by_country(locale_language)
    mail_cc.append('nqi@bainainfo.com')
    template = os.path.join(TEMPLATE_ROOT, "create_task.html")
    name_version = appname + " V" + appversion
    send_message(
        subject, template, mail_to, mail_cc, False, None, name_version,
        display_locale)


def _get_task_list(uid):
    """
    list of the translation task
    Parameters:
        -None
    Return:
        -The lists of translation task
        {
            "name": "platform",
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
                        "display_value": "", "value": "", "children": []}

                    version_locale = {"name": "locale", "items": []}
                    version_refer = {"name": "reference", "items": []}
                    countrys = User.get_country_info(uid)
                    print "1234 country"
                    print countrys
                    countrys = ["Croatian", "Denmark"]
                    version_locale["items"] = _process_locales(
                        LocalizationTask.get_candidate_locales(
                            plat_name, cate_name, app_name, version, countrys))
                    if version_locale["items"]:
                        for i, locale_i in enumerate(version_locale["items"]):
                            if locale_i.get("value") == 'tl':
                                version_locale.get("items").pop(i)
                    version_refer["items"] = _process_locales(
                        LocalizationTask.get_in_task_locales(
                            plat_name, cate_name,
                            app_name, version, status="finished"))

                    version_items["display_value"] = version
                    version_items["value"] = version
                    version_items["children"].append(version_locale)
                    version_items["children"].append(version_refer)
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

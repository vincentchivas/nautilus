# -*- coding: utf-8 -*-
"""
@author: yqyu
@date: 2014-07-15
@description: Create translation task
"""

import os

from django.conf import settings

from provisionadmin.utils.respcode import DB_ERROR, \
    METHOD_ERROR, DATA_ERROR
from provisionadmin.utils.json import json_response_error, json_response_ok
from provisionadmin.decorator import check_session, exception_handler
from provisionadmin.model.i18n import LocalizationInfo, LocalizationTask, \
    LocalizationConfig, MailConfig, LocalizationStrings
from provisionadmin.utils.util_mail import send_message
import simplejson as json


TEMPLATE_ROOT = settings.CUS_TEMPLATE_DIR


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
        data = _get_task_list()
        return json_response_ok(data)
    elif request.method == 'POST':
        dict_str = request.raw_post_data
        insert_data = {}
        temp_dict = json.loads(dict_str)
        appname = insert_data["appname"] = temp_dict["appname"]
        appversion = insert_data["appversion"] = temp_dict["appversion"]
        locale = insert_data["locale"] = temp_dict["locale"]
        insert_info = dict(insert_data)
        insert_data["autofill"] = temp_dict.get("autofill")
        if temp_dict.get("reference") == 'us':
            insert_data["reference"] = ""
        else:
            insert_data["reference"] = temp_dict.get("reference")
        uid = user._id
        insert_data['creator_id'] = uid
        info_id = LocalizationInfo.insert(insert_info, get=True)
        if not info_id:
            return json_response_error(
                DB_ERROR, msg='create localizationinfo failed!')
        LocalizationTask.insert_task(insert_data)

        # send email
        _send_task_email(appname, appversion, locale)

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


def _send_task_email(appname, appversion, locale):
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
    subject = u"Translation task 【%s】" % display_locale
    mail_to, mail_cc = MailConfig.get_mailto_by_country(locale_language)
    mail_to = ["yqyu@bainainfo.com", 'lhhuang@bainainfo.com']
    mail_cc = ['bhuang@bainainfo.com', 'jyqiu@bainainfo.com']
    mail_cc.append('nqi@bainainfo.com')
    template = os.path.join(TEMPLATE_ROOT, "create_task.html")
    name_version = appname + " V" + appversion
    strings_total = LocalizationStrings.get_app_locale_count(
        appname, appversion, '')
    strings_finished = LocalizationStrings.get_app_locale_count(
        appname, appversion, locale, {'finished': True})
    left_count = strings_total - strings_finished
    send_message(
        subject, template, mail_to, mail_cc, False, None, name_version,
        display_locale, left_count)


def _get_task_list():
    """
    list of the translation task
    Parameters:
        -None
    Return:
        -The lists of translation task
        {
            "name": "appname",
            "items":[
                ...
            ]
         }
    """
    data = {"name": "appname", "items": []}
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
            version_items = {"display_value": "", "value": "", "children": []}

            version_locale = {"name": "locale", "items": []}
            version_refer = {"name": "reference", "items": []}
            version_locale["items"] = _process_locales(
                LocalizationTask.get_candidate_locales(app_name, version))
            if version_locale["items"]:
                for i, locale_i in enumerate(version_locale["items"]):
                    if locale_i.get("value") == 'tl':
                        version_locale.get("items").pop(i)
            version_refer["items"] = _process_locales(
                LocalizationTask.get_in_task_locales(
                    app_name, version, status="finished"))

            version_items["display_value"] = version
            version_items["value"] = version
            version_items["children"].append(version_locale)
            version_items["children"].append(version_refer)
            appname_children["items"].append(version_items)
        items_dict["display_value"] = app_name
        items_dict["value"] = app_name
        items_dict["children"] = appname_children
        data["items"].append(items_dict)
    return data

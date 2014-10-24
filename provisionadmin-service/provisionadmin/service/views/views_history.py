# -*-coding: utf-8 -*-
"""
@author: yqyu
@date: 2014-07-15
@description: Check the user build history information
"""

import time
from provisionadmin.utils.json import json_response_error, json_response_ok
from provisionadmin.utils.respcode import PARAM_REQUIRED, METHOD_ERROR, \
    DATA_ERROR
from provisionadmin.decorator import check_session, exception_handler
from provisionadmin.model.i18n import LocalizationTask, LocalizationConfig, \
    LocalizationHistory, LocalizationInfo
from provisionadmin.service.views.views_add import _process_locales
from provisionadmin.service.views.views_list import _delete_duplicate_ele


@exception_handler()
@check_session
def history_list(request, user):
    """
    Get history records of users operating by userid
    Parameters:
        -start: start time,
        -end:  deadline,
    Return:
        -1. the history records of users operating by userid
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
        required_list = ('start', 'end')
        for required_para in required_list:
            para_data = request.GET.get(required_para)
            if not para_data:
                return json_response_error(
                    PARAM_REQUIRED,
                    msg="parameter '%s' invalid" % required_para)
        temp_start = request.GET.get("start")
        start = time.mktime(time.strptime(temp_start, '%Y-%m-%d'))
        temp_end = request.GET.get("end")
        end = time.mktime(time.strptime(temp_end, '%Y-%m-%d')) + 86400.0
        platform = request.GET.get("platform")
        appname = request.GET.get("appname")
        category = request.GET.get("category")
        appversion = request.GET.get("appversion")
        locale = request.GET.get("locale")
        uid = user.get("_id")
        cond = {"modifier_id": uid,
                "modified_at": {"$gte": start, "$lte": end}}
        data = {}
        data["filters"] = _get_filter()
        if platform is None:
            platform_value = data["filters"]["items"][0]
            platform = platform_value.get("value")
            appname_value = platform_value["children"]["items"][0]
            appname = appname_value.get("value")
            category_value = appname_value["children"]["items"][0]
            category = category_value.get("value")
            version_value = category_value["children"]["items"][0]
            appversion = version_value.get("value")
            locale_info = version_value["children"]["items"][0]
            locale = locale_info.get("value")
        if locale == "us":
            locale = ""
        temp_data = LocalizationHistory.get_history_by_userid(
            cond, platform, category, appname, appversion,
            locale, sort=[("modified_at", -1)])
        data["items"] = temp_data
        locale_language = LocalizationConfig.get_locale_info(
            appname, appversion, locale).get("language")
        data['display_locale'] = "%s(%s)" % (locale_language, locale)
        return json_response_ok(data)
    else:
        return json_response_error(METHOD_ERROR, msg="http method wrong")


def _get_filter():
    """
    Filter of the activity list page
    Parameters:
        -None
    Return:
        -The lists of activity list filter
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
                    version_children = {"name": "locale", "items": []}

                    version_children["items"] = _process_locales(
                        LocalizationTask.get_in_task_locales(
                            plat_name, cate_name, app_name, version))
                    version_items["display_value"] = version
                    version_items["value"] = version
                    version_items["children"] = version_children
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

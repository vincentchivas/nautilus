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
        appname = request.GET.get("appname")
        appversion = request.GET.get("appversion")
        locale = request.GET.get("locale")
        uid = user._id
        cond = {"modifier_id": uid,
                "modified_at": {"$gte": start, "$lte": end}}
        data = {}
        data["filters"] = _get_history_filter()
        if appname is None:
            appname_value = data["filters"]["items"][0]
            appname = appname_value.get("value")
            version_value = appname_value["children"]["items"][0]
            appversion = version_value.get("value")
            locale_info = version_value["children"]["items"][0]
            locale = locale_info.get("value")
        temp_data = LocalizationHistory.get_history_by_userid(
            cond, appname, appversion, locale, sort=[("modified_at", -1)])
        data["items"] = temp_data
        locale_language = LocalizationConfig.get_locale_info(
            appname, appversion, locale).get("language")
        data['display_locale'] = "%s(%s)" % (locale_language, locale)
        return json_response_ok(data)
    else:
        return json_response_error(METHOD_ERROR, msg="http method wrong")


def _get_history_filter():
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
            appversion_children = {"name": "locale", "items": []}

            appversion_children["items"] = _process_locales(
                LocalizationTask.get_in_task_locales(app_name, version))
            temp_item = appversion_children["items"]
            if temp_item:
                for i, locale_i in enumerate(temp_item):
                    if locale_i.get("value") == 'us':
                        appversion_children.get("items").pop(i)
            version_items["display_value"] = version
            version_items["children"] = appversion_children
            version_items["value"] = version
            appname_children["items"].append(version_items)
        items_dict["display_value"] = app_name
        items_dict["value"] = app_name
        items_dict["children"] = appname_children
        filters["items"].append(items_dict)
    return filters

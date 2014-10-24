# -*- coding: utf-8 -*-
"""
@author: yqyu
@date: 2014-07-15
@description: submit build task
"""

from provisionadmin.utils.respcode import PARAM_REQUIRED, DATA_ERROR, \
    METHOD_ERROR
from provisionadmin.utils.json import json_response_error, json_response_ok
from provisionadmin.decorator import check_session, exception_handler
from provisionadmin.model.i18n import LocalizationSnap, LocalizationApps


@exception_handler()
@check_session
def project_list(request, user):
    """
    Get project information list for can be built,
    include:
        -package name,
        -package version
        -tag of package
    Parameters:
        -None
    Return:
        -1. list of project information
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
        data = _get_project_list()
        return json_response_ok(data)
    else:
        return json_response_error(METHOD_ERROR, msg="http method wrong")


@exception_handler()
@check_session
def create_project(request, user):
    """
    Create build task
    Parameters:
        -appname: package name,
        -appversion: package version,
        -tag: the tag of apk,
    Return:
        -1. create success
        {
            "status": 0,
            "data":{
                ...
            }
         }
        -2. create failed
        {
            "status": 4,
            "data":{
                ...
            }
         }
        -3. error http method
        {
            "status": 11,
            "data":{
                ...
            }
         }
    """
    if request.method == 'GET':
        uid = user.get("_id")
        required_list = ('appname', 'appversion', 'tag')
        for required_para in required_list:
            para_data = request.GET.get(required_para)
            if not para_data:
                return json_response_error(
                    PARAM_REQUIRED,
                    msg="parameter '%s' invalid" % required_para)
        appname = request.GET.get('appname')
        appversion = request.GET.get('appversion')
        tag = request.GET.get("tag")

        if tag == 'new':
            tag_array = LocalizationApps.get_tag_by_app(
                appname, appversion).get("tag")
            tag = tag_array[-1]

        miss_only = False

        temp_data = LocalizationSnap.submit_project(
            appname, appversion, tag, locale=None, creator_id=uid,
            missing_only=miss_only)
        if temp_data:
            return json_response_ok(msg="upload successful")
        else:
            return json_response_error(DATA_ERROR, msg="upload failure")
    else:
        return json_response_error(METHOD_ERROR, msg="http method wrong")


def _get_project_list():
    """
    list of the project information
    Parameters:
        -None
    Return:
        -The lists of project information
        {
            "name": "appname",
            "items":[
                ...
            ]
         }
    """
    data = {"name": "appname", "items": []}
    appname_list = LocalizationApps.find(
        {}, {"appname": 1, "_id": 0}, toarray=True)
    if not appname_list:
        return json_response_error(DATA_ERROR, msg="no app in db")
    func = lambda x, y: x if y in x else x + [y]
    appname_list = reduce(func, [[], ] + appname_list)
    for app_item in appname_list:
        items_dict = {"display_value": "", "value": "", "children": {}}
        app_name = app_item.get("appname")
        app_version = LocalizationApps.get_by_app_version(
            app_name).get("appversion")
        appname_children = {"name": "appversion", "items": []}
        for version in app_version:
            version_items = {"display_value": "", "value": "", "children": {}}
            appversion_children = {"name": "tag", "items": []}

            tag_array = LocalizationApps.get_tag_by_app(
                app_name, version).get("tag")
            for tag in tag_array:
                tag_items = {"display_value": "", "value": ""}
                tag_items["display_value"] = tag
                tag_items["value"] = tag
                appversion_children["items"].append(tag_items)

            version_items["display_value"] = version
            version_items["children"] = appversion_children
            version_items["value"] = version
            appname_children["items"].append(version_items)
        items_dict["display_value"] = app_name
        items_dict["value"] = app_name
        items_dict["children"] = appname_children
        data["items"].append(items_dict)
    return data


@exception_handler()
def init_tag(request):
    """
    init all app tag
    Parameters:
        -None
    Return:
        -1. found tag data
        {
            "status": 0,
            "data":{
                ...
            }
         }
        -1. not found tag data
        {
            "status": 4,
            "data":{
                ...
            }
         }
        -3. error http method
        {
            "status": 11,
            "data":{
                ...
            }
         }
    """
    if request.method == 'GET':
        tag = LocalizationApps.update_apptag()
        if tag:
            return json_response_ok()
        else:
            return json_response_error(DATA_ERROR, msg="no tag in service")
    else:
        return json_response_error(METHOD_ERROR, msg="http method wrong")

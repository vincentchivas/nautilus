# -*- coding: utf-8 -*-

from django.http import HttpResponse
from provisionadmin.utils.respcode import PARAM_REQUIRED, DATA_ERROR, \
    METHOD_ERROR
from provisionadmin.utils.json import json_response_error, json_response_ok
from provisionadmin.decorator import check_session, exception_handler
from provisionadmin.model.i18n import LocalizationInfo, LocalizationApps


@exception_handler()
@check_session
def export_list(request, user):
    """
    Get apk information can export XML file
    Parameters:
        -None
    Return:
        -1. The list of apk information
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
        appname_list = LocalizationInfo.find(
            {"locale": ""}, {"appname": 1, "_id": 0}, toarray=True)
        if not appname_list:
            return json_response_error(DATA_ERROR, msg="no app in db")
        data = {}
        data = _get_export_list()
        return json_response_ok(data)
    else:
        return json_response_error(METHOD_ERROR, msg="http method wrong")


@exception_handler(as_json=False)
@check_session
def export_raw_xml(request, user):
    """
    export XML file by appname & appversion & locale & allxml
    Parameters:
        -appname: package name,
        -appversion: package version,
        -locale: Country code,
        -allxml: full xml file or miss xml
    Return:
        -1. The xml file
        -2. error http method
        {
            "status": 11,
            "data":{
                ...
            }
        }
    """
    if request.method == 'GET':
        required_list = ('appname', 'appversion')
        for required_para in required_list:
            para_data = request.GET.get(required_para)
            if not para_data:
                return json_response_error(
                    PARAM_REQUIRED,
                    msg="parameter '%s' invalid" % required_para)

        appname = request.GET.get("appname")
        appversion = request.GET.get("appversion")
        locale = request.GET.get("locale", 'all')
        print "123:%s" % locale
        allxml = request.GET.get("allxml")
        if allxml == 'true':
            miss_only = False
        else:
            miss_only = True

        if miss_only:
            ret_filename = "raw_xml_%s_%s.zip" % (appname, appversion)
        else:
            ret_filename = "global_xml_%s_%s.zip" % (appname, appversion)

        xmlfile = LocalizationApps.generate_xml_file(
            appname, appversion, locale, md5=None, missing_only=miss_only)

        response = HttpResponse(xmlfile, mimetype="application/zip")
        response['Content-Disposition'] = "attachment; "\
            "filename=%s" % ret_filename
        return response
    else:
        return json_response_error(METHOD_ERROR, msg="http method wrong")


def _get_export_list():
    """
    list of the export list
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
            version_items = {"display_value": "", "value": ""}
            version_items["display_value"] = version
            version_items["value"] = version
            appname_children["items"].append(version_items)
        items_dict["display_value"] = app_name
        items_dict["value"] = app_name
        items_dict["children"] = appname_children
        data["items"].append(items_dict)
    return data

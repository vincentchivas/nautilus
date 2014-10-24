# -*- coding: utf-8 -*-

from django.http import HttpResponse
from provisionadmin.utils.respcode import PARAM_REQUIRED, DATA_ERROR, \
    METHOD_ERROR
from provisionadmin.utils.json import json_response_error, json_response_ok
from provisionadmin.decorator import check_session, exception_handler
from provisionadmin.model.i18n import LocalizationInfo, LocalizationApps
from provisionadmin.service.views.views_history import _get_filter


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
        data = _get_filter()
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
        -allxml: full xml file or miss xml or diff xml
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
        required_list = ('platform', 'appname', 'category', 'appversion')
        for required_para in required_list:
            para_data = request.GET.get(required_para)
            if not para_data:
                return json_response_error(
                    PARAM_REQUIRED,
                    msg="parameter '%s' invalid" % required_para)

        platform = request.GET.get("platform")
        appname = request.GET.get("appname")
        category = request.GET.get("category")
        appversion = request.GET.get("appversion")
        locale = request.GET.get("locale", 'all')
        if locale == "us":
            locale = ""
        xml_type = request.GET.get("type", "miss")

        if xml_type == 'diff':
            ret_filename = "diff_%s_%s_%s.zip" % (
                platform, appname, appversion)
            xmlfile = LocalizationApps.generate_diff_xml(
                platform, appname, category, appversion, locale,
                md5=None)
        elif xml_type == 'xls':
            ret_filename = "xml_%s_%s.xls" % (appname, appversion)
            xmlfile = LocalizationApps.generate_xls_file(
                platform, appname, category, appversion, locale)
            response = HttpResponse(
                open(xmlfile, 'r').read(), mimetype="application/ms-excel")
            response['Content-Disposition'] = "attachment; "\
                "filename=%s" % ret_filename
            return response
        else:
            if xml_type == 'all':
                miss_only = False
                ret_filename = "global_xml_%s_%s.zip" % (appname, appversion)
            else:
                miss_only = True
                ret_filename = "raw_xml_%s_%s.zip" % (appname, appversion)

            xmlfile = LocalizationApps.generate_xml_file(
                platform, appname, category, appversion, locale,
                md5=None, missing_only=miss_only)

        response = HttpResponse(xmlfile, mimetype="application/zip")
        response['Content-Disposition'] = "attachment; "\
            "filename=%s" % ret_filename
        return response
    else:
        return json_response_error(METHOD_ERROR, msg="http method wrong")

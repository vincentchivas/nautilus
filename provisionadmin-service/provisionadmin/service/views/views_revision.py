# -*-coding: utf-8 -*-
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
import zipfile
import os
import time
from django.http import HttpResponse
from provisionadmin.utils.json import json_response_error, json_response_ok
from provisionadmin.utils.respcode import PARAM_REQUIRED, METHOD_ERROR
from provisionadmin.decorator import check_session, exception_handler
from provisionadmin.model.i18n import LocalizationTask, LocalizationSnap, \
    LocalizationApps, LocalizationHistory
from bson import ObjectId
import all_json
# from xml.etree import ElementTree as ET


@exception_handler(as_json=False)
@check_session
def export_revision_xml(request, user):
    data = request.GET

    snap_id = data.get('snap_id')
    if not snap_id:
        return json_response_error(
            PARAM_REQUIRED, msg="parameter 'snap_id' invalid")
    s_id = ObjectId(snap_id)
    cond = {}
    cond["_id"] = s_id
    ret_filename = "%s_xml.zip" % (s_id)
    ret_sio = StringIO()
    ret_zip = zipfile.ZipFile(ret_sio, 'w')
    snaps = LocalizationSnap.find(cond, one=True)
    appname = snaps["appname"]
    appversion = snaps["appversion"]
    md5 = LocalizationApps.get_xml_info(appname, appversion)['md5']
    items = snaps["items"]
    for i in items:
        sios = {}
        locale = i["locale"]
        strings = i["strings"]["items"]
        locale_strings = LocalizationTask.organize_strings(
            appname, appversion, locale, md5, missing_only=False,
            strings=strings, inc_only=False)
        for k, v in locale_strings.items():
            sio = StringIO()
            v.write(sio, encoding="utf-8", xml_declaration=True)
            sios[k] = sio
        for k, v in sios.items():
            ret_zip.writestr(
                os.path.join(
                    "values-%s" % locale if locale else "values",
                    "%s.xml" % k),
                v.getvalue())
    ret_zip.close()
    response = HttpResponse(ret_sio.getvalue(), mimetype="application/zip")
    response['Content-Disposition'] = "attachment; filename=%s" % ret_filename
    return response


@exception_handler()
# @check_session
# def task_list(request, user):
def history_list(request):
    if request.method == 'GET':
        # uid = user._id
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
        appversion = request.GET.get("appname")
        display_locale = request.GET.get("display_locale")
        locale = display_locale
        uid = 3
        cond = {"modifier_id": uid,
                "modified_at": {"$gte": start, "$lte": end}}
        data = {}
        data["filters"] = all_json.filters
        temp_data = LocalizationHistory.get_history_by_userid(
            cond, appname, appversion, locale, sort=[("modified_at", -1)])
        data["items"] = temp_data
        return json_response_ok(data)
    else:
        return json_response_error(METHOD_ERROR, msg="http method wrong")

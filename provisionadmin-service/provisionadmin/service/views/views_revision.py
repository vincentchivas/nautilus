# -*-coding: utf-8 -*-
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
import zipfile
import os
import datetime
import pymongo
from django.http import HttpResponse
from provisionadmin.utils.json import json_response_error, json_response_ok
from provisionadmin.utils.respcode import PARAM_REQUIRED
from provisionadmin.decorator import check_session, exception_handler
from provisionadmin.model import i18n
from provisionadmin.utils import exception
from bson import ObjectId
# from xml.etree import ElementTree as ET
# import time


@exception_handler()
@check_session
def show_snap(request):
    uid = request.session.get('uid')
    if not uid:
        raise exception.AuthFailureError("can not get uid")
    if request.method == 'GET':
        cond = {"creator_id": uid, 'status': 'finished'}
        data = [{
            'snap_id': str(s['_id']),
            'export_revision_time': str(
                datetime.datetime.fromtimestamp(s['created_at']))}
            for s in i18n.LocalizationSnap.find(cond, {'created_at': 1}).sort(
                'created_at', pymongo.DESCENDING)]
        return json_response_ok(data)


@exception_handler(as_json=False)
@check_session
def export_revision_xml(request):
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
    snaps = i18n.LocalizationSnap.find(cond, one=True)
    appname = snaps["appname"]
    appversion = snaps["appversion"]
    items = snaps["items"]
    for i in items:
        sios = {}
        locale = i["locale"]
        strings = i["strings"]["items"]
        locale_strings = i18n.LocalizationTask.organize_strings(
            appname, appversion, locale, strings, inc_only=False)
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

#-*- coding: utf-8 -*-

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
import zipfile
import os
from django.http import HttpResponse
from django.conf import settings
from provisionadmin.utils.respcode import PARAM_REQUIRED
from provisionadmin.utils.json import json_response_error, json_response_ok
from provisionadmin.decorator import check_session, exception_handler
from provisionadmin.model.i18n import LocalizationSnap, LocalizationInfo, \
    LocalizationConfig, LocalizationTask
from provisionadmin.utils import respcode, exception


STATIC_ROOT = settings.STATIC_ROOT


@exception_handler()
@check_session
def export(request):
    uid = request.session.get('uid')
    if not uid:
        raise exception.AuthFailureError("can not get uid")
    if request.method == 'GET':
        required_list = ('appname', 'appversion')
        for required_para in required_list:
            para_data = request.GET.get(required_para)
            if not para_data:
                return json_response_error(
                    PARAM_REQUIRED,
                    msg="parameter '%s' invalid" % required_para)
        appname = request.GET['appname']
        appversion = request.GET['appversion']
        locale = request.GET.get('locale')
        # locale = request.GET['locale']
        apk_downlink, qrcode_pic_downlink = LocalizationSnap.init_rebuild(
            appname, appversion, locale, creator_id=uid)
        data = {}
        data["download_link"] = apk_downlink
        data["qrcode_pic"] = qrcode_pic_downlink
        return json_response_ok(data, msg="export success")


@exception_handler(as_json=False)
@check_session
def export_raw_xml(request):
    info = LocalizationInfo.get_lastest_info()
    if not info:
        return json_response_error(
            respcode.CONTENT_NOT_FOUND, msg="parameter 'snap_id' invalid")
    appname = info['appname']
    appversion = info['appversion']
    locales = LocalizationConfig.get_app_locales(
        appname, appversion, locale_only=True)
    ret_sio = StringIO()
    ret_zip = zipfile.ZipFile(ret_sio, 'w')

    for l in locales:
        missing_xml_dirpath = os.path.join(
            STATIC_ROOT, appname, appversion, 'miss_xml_data',
            'values' if l == '' else "values-%s" % l)
        l_strings = LocalizationTask.organize_strings(
            appname, appversion, l, as_raw=True)

        if os.path.exists(missing_xml_dirpath):
            files = os.listdir(missing_xml_dirpath)
            for f in files:
                if f not in l_strings:
                    sio = StringIO()
                    sio.write(
                        file(os.path.join(missing_xml_dirpath, f)).read())
                    sio.flush()
                    missing_filename = "%s_missing%s" % tuple(
                        os.path.splitext(f))
                    ret_zip.writestr(
                        os.path.join(
                            "values-%s" % l if l else 'values',
                            missing_filename),
                        sio.getvalue())

        for k, v in l_strings.iteritems():
            missing_filename = "%s_missing%s" % tuple(os.path.splitext(k))
            # to adapt to standard of client side
            filepath = os.path.join(
                "values-%s" % l if l else 'values', missing_filename)
            sio = StringIO()
            v.write(sio, encoding='utf-8', xml_declaration=True)
            ret_zip.writestr(filepath, sio.getvalue())

    ret_zip.close()
    response = HttpResponse(ret_sio.getvalue(), mimetype="application/zip")
    response['Content-Disposition'] = "attachment; filename=raw_xml_data_" \
        "%s_%s.zip" % (appname, appversion)
    return response

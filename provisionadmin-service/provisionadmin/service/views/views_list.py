# -*-coding: utf-8 -*-

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
import zipfile
from django.http import HttpResponse
# from xml.etree import ElementTree as ET
from provisionadmin.utils.json import json_response_error, json_response_ok
from provisionadmin.utils.respcode import PARAM_REQUIRED, METHOD_ERROR
from provisionadmin.model.i18n import LocalizationTask, LocalizationConfig
from provisionadmin.utils import exception
from provisionadmin.decorator import check_session, exception_handler
import all_json
from provisionadmin.model import i18n


@exception_handler()
@check_session
def show_list(request):
    uid = request.session.get('uid')
    if not uid:
        raise exception.AuthFailureError("can not get uid")
    if request.method == 'GET':
        status = request.GET.get("status")
        # cond = {"creator_id": uid}
        cond = {}
        if status:
            cond["string.status"] = status
        data = {}
        data["filters"] = all_json.filters
        temp_data = LocalizationTask.get_all_task(
            cond, sort=[("created_at", -1)])
        data["items"] = get_task(temp_data)
        return json_response_ok(data)
    else:
        return json_response_error(METHOD_ERROR, msg="http method wrong")


def get_task(ret_task):
    items = []
    for t in ret_task:
        temp = {}
        temp['appname'] = t["target"]["appname"]
        temp['appversion'] = t["target"]["appversion"]
        temp['locale'] = t["target"]["locale"]
        temp['autoFill'] = t["target"].get("autoFill")
        if temp['locale'] == "":
            continue
        #r_locale = t["reference"]["locale"]
        #temp['display_locale'] = "%s - %s" % (
        #    r_locale if r_locale else 'en', t['target']['locale'])
        language = LocalizationConfig.get_locale_info(
            temp["appname"], temp["appversion"], temp["locale"]).get("language")
        temp['display_locale'] = "%s(%s)" % (language, t['target']['locale'])
        left_count = t["strings"]["total"] - t["strings"]["finished"]
        if left_count > 0:
            status = "draft"
        else:
            status = "finished"
        temp['status'] = status
        temp['left_count'] = left_count
        # temp.append(["view deltails", "xxx/xxx"])
        items.append(temp)
    return items


@exception_handler(as_json=False)
@check_session
def export_task_xml(request):
    data = request.GET

    appname = data.get('appname')
    if not appname:
        return json_response_error(
            PARAM_REQUIRED, msg="parameter 'appname' invalid")
    appversion = data.get('appversion')
    if not appversion:
        return json_response_error(
            PARAM_REQUIRED, msg="parameter 'appversion' invalid")
    locale = data.get('locale')
    if not locale:
        return json_response_error(
            PARAM_REQUIRED, msg="parameter 'locale' invalid")
    ret_filename = "%s_%s_%s_xml.zip" % (
        appname, appversion, locale)
    ret_sio = StringIO()
    ret_zip = zipfile.ZipFile(ret_sio, 'w')
    strings = i18n.LocalizationTask.organize_strings(
        appname, appversion, locale, inc_only=True)
    if not strings:
        raise exception.DataError(
            "The list is empty, nothing to do. Try to translate!")
    sios = {}
    for k, v in strings.items():
        sio = StringIO()
        v.write(
            sio, encoding="utf-8", xml_declaration=True)
        sios[k] = sio
    for k, v in sios.items():
        ret_zip.writestr("%s.xml" % k, v.getvalue())
    ret_zip.close()
    response = HttpResponse(ret_sio.getvalue(), mimetype="application/zip")
    response['Content-Disposition'] = "attachment; filename=%s" % ret_filename
    return response

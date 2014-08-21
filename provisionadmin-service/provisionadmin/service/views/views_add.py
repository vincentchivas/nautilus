# -*- coding: utf-8 -*-

from provisionadmin.utils.respcode import DB_ERROR, \
    METHOD_ERROR, DATA_ERROR, PARAM_REQUIRED
from provisionadmin.utils.json import json_response_error, json_response_ok
from provisionadmin.decorator import check_session, exception_handler
from provisionadmin.model.i18n import LocalizationInfo, LocalizationTask
from provisionadmin.service.views.views_list import get_task
from provisionadmin.utils import exception
import all_json
import simplejson as json


@exception_handler()
@check_session
def task_add(request):

    def process_locales(locales):
        ret_locales = []
        for l in locales:
            new_l = {
                'value': l['locale'],
                'display_value': "%s(%s)" % (l['language'], l['locale'] if l['locale'] else "en")}
            ret_locales.append(new_l)
        return ret_locales

    uid = request.session.get('uid')
    if not uid:
        raise exception.AuthFailureError("can not get uid")
    if request.method == 'GET':
        '''
        if not uid:
            return json_response_error(PERMISSION_DENY, msg='not login')
        '''
        data = {}
        temp_dict = LocalizationInfo.get_lastest_info()
        if not temp_dict:
            return json_response_error(DATA_ERROR, msg="no apk in local")
        data["appname"] = temp_dict["appname"]
        data["appversion"] = temp_dict["appversion"]
        data["locale"] = process_locales(
            LocalizationTask.get_candidate_locales(
                data["appname"], data["appversion"]))
        # notice the locale item may have default_value which is to be ...
        data["reference"] = process_locales(
            LocalizationTask.get_in_task_locales(
                data["appname"], data["appversion"],
                {"strings.status": "finished"}))
        return json_response_ok(data)
    elif request.method == 'POST':
        dict_str = request.raw_post_data
        insert_data = {}
        temp_dict = json.loads(dict_str)
        insert_data["appname"] = temp_dict["appname"]
        insert_data["appversion"] = temp_dict["appversion"]
        insert_data["locale"] = temp_dict["locale"]
        insert_info = dict(insert_data)
        insert_data["autoFill"] = temp_dict.get("autoFill")
        insert_data["reference"] = temp_dict.get("reference")
        # orig_status = temp_dict["status"] if "status" in temp_dict \
        #   else None
        #insert_data["uid"] = request.session.get('uid')
        if not uid:
            raise exception.AuthFailureError("can not get uid")
        insert_data['creator_id'] = uid
        info_id = LocalizationInfo.insert(insert_info, get=True)
        print "info_id is:%s" % info_id
        if not info_id:
            json_response_error(
                DB_ERROR, msg='create localizationinfo failed!')
        LocalizationTask.insert_task(insert_data)
        print "after insert task"
        data = {}
        data["filters"] = all_json.filters
        cond = {"creator_id": uid}
        #if orig_status:
            #cond["strings.status"] = status
        temp_data = LocalizationTask.get_all_task(cond)
        data["items"] = get_task(temp_data)
        return json_response_ok(data)
    else:
        return json_response_error(METHOD_ERROR, msg="http method wrong")

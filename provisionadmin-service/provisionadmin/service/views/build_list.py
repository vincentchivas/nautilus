# -*- coding: utf-8 -*-
"""
@author: yqyu
@date: 2014-07-15
@description: Check the user build history information
"""

import simplejson as json
from bson import ObjectId
from provisionadmin.utils.respcode import PARAM_REQUIRED, METHOD_ERROR
from provisionadmin.utils.json import json_response_error, json_response_ok
from provisionadmin.decorator import check_session, exception_handler
from provisionadmin.model.i18n import LocalizationSnap, LocalizationErrorlog


@exception_handler()
@check_session
def get_project_info(request, user):
    """
    get build project history list by user_id
    param: None
    return_value: Json
    """
    if request.method == 'GET':
        # uid = user.get("_id")
        uid = 3
        data = {
            "id": "", "time": "", "appname": "", "appversion": "", "tag": "",
            "status": "", "download_link": "", "qrcode_pic": ""}
        data = LocalizationSnap.get_snap_info(uid=uid)
        return json_response_ok(data)
    else:
        return json_response_error(METHOD_ERROR, msg="http method wrong")


@exception_handler()
@check_session
def cancel_project(request, user):
    """
    cancle build project task
    param: task id
    return_value: Json
    """
    if request.method == 'GET':
        # uid = user._id
        uid = user.get("_id")
        task_id = request.GET.get("id")
        if not task_id:
            return json_response_error(
                PARAM_REQUIRED, msg="parameter '%s' invalid" % task_id)
        if not isinstance(task_id, ObjectId):
            task_id = ObjectId(task_id)
        cond = {"_id": task_id, "creator_id": uid}
        data = {"status": ""}
        snap_id = LocalizationSnap.find(cond, id_only=True)
        if not snap_id:
            data["status"] = "failed"
            return json_response_ok(data, msg="cancle failure")
        LocalizationSnap.update(cond, {"status": "cancel"})
        data["status"] = "success"
        return json_response_ok(data, msg="cancle success")
    else:
        return json_response_error(METHOD_ERROR, msg="http method wrong")


@exception_handler()
@check_session
def delete_project(request, user):
    """
    delete build project task info
    param: task id
    return_value: Json
    """
    if request.method == 'GET':
        uid = user.get("_id")
        task_id = request.GET.get("id")
        if not task_id:
            return json_response_error(
                PARAM_REQUIRED, msg="parameter id invalid")
        if not isinstance(task_id, ObjectId):
            task_id = ObjectId(task_id)
        data = {"status": ""}
        cond = {"_id": task_id, "creator_id": uid}
        snap_id = LocalizationSnap.find(cond, id_only=True)
        if not snap_id:
            data["status"] = "failed"
            return json_response_ok(data, msg="delete failure")
        LocalizationSnap.remove(cond)
        data["status"] = "success"
        return json_response_ok(data, msg="delete success")
    else:
        return json_response_error(METHOD_ERROR, msg="http method wrong")


@exception_handler()
@check_session
def lint_message(request, user):
    """
    Check the lint results
    Parameters:
        -task id: the id of build task,
    Return:
        -1. The lists of the lint message
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
        task_id = request.GET.get("id")
        if not task_id:
            return json_response_error(
                PARAM_REQUIRED, msg="parameter id invalid")
        data = {}
        data["items"] = LocalizationErrorlog.get_errorlog_by_target(task_id)
        return json_response_ok(data)
    else:
        return json_response_error(METHOD_ERROR, msg="http method wrong")


@exception_handler()
def update_project_status(request):
    """
    update build project task info
    param: taskid, status, apk_url, reason, log_url
    return_value: Json
    """
    if request.method == 'POST':
        dict_str = request.raw_post_data
        temp_dict = json.loads(dict_str)
        required_list = ('taskid', 'status')
        for required_para in required_list:
            para_data = temp_dict.get(required_para)
            if not para_data:
                return json_response_error(
                    PARAM_REQUIRED,
                    msg="parameter '%s' invalid" % required_para)
        task_id = temp_dict.get("taskid")
        status = temp_dict.get("status")
        apk_url = temp_dict.get("apk_uri", "")
        reason = temp_dict.get("reason", "")
        log_url = temp_dict.get("log_uri", "")
        lint_url = temp_dict.get("lint_url", "")
        lint_result = temp_dict.get("lint_result", [])
        if not isinstance(task_id, ObjectId):
            task_id = ObjectId(task_id)
        status = int(status)
        LocalizationSnap.update_status(
            task_id, status, apk_url, reason, log_url, lint_url, lint_result)
        return json_response_ok()
    else:
        return json_response_error(METHOD_ERROR, msg="http method wrong")

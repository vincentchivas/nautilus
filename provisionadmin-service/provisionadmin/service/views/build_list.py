# -*- coding: utf-8 -*-
"""
@author: yqyu
@date: 2014-07-15
@description: Check the user build history information
"""

from bson import ObjectId
from provisionadmin.utils.respcode import PARAM_REQUIRED, METHOD_ERROR
from provisionadmin.utils.json import json_response_error, json_response_ok
from provisionadmin.decorator import check_session, exception_handler
from provisionadmin.model.i18n import LocalizationSnap


@exception_handler()
@check_session
def get_project_info(request, user):
    """
    get build project history list by user_id
    param: None
    return_value: Json
    """
    if request.method == 'GET':
        uid = user._id
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
    uid = user._id
    if request.method == 'GET':
        uid = user._id
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
        uid = user._id
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
def update_project_status(request):
    """
    update build project task info
    param: taskid, status, apk_url, reason, log_url
    return_value: Json
    """
    if request.method == 'POST':
        required_list = ('taskid', 'status')
        for required_para in required_list:
            para_data = request.POST.get(required_para)
            if not para_data:
                return json_response_error(
                    PARAM_REQUIRED,
                    msg="parameter '%s' invalid" % required_para)
        task_id = request.POST.get("taskid")
        status = request.POST.get("status")
        apk_url = request.POST.get("apk_uri", "")
        reason = request.POST.get("reason", "")
        log_url = request.POST.get("log_uri", "")
        if not isinstance(task_id, ObjectId):
            task_id = ObjectId(task_id)
        status = int(status)
        LocalizationSnap.update_status(
            task_id, status, apk_url, reason, log_url)
        return json_response_ok()
    else:
        return json_response_error(METHOD_ERROR, msg="http method wrong")

# -*- coding: utf-8 -*-
"""
@author: yqyu
@date: 2014-07-15
@description: Get Check the information of user failed to build
"""

import time
from provisionadmin.utils.json import json_response_ok, json_response_error
from provisionadmin.utils.respcode import PARAM_REQUIRED, METHOD_ERROR
from provisionadmin.decorator import check_session, exception_handler
from provisionadmin.model.i18n import LocalizationSnap


@exception_handler()
@check_session
def errorlog(request, user):
    """
    Get history records of users build failed
    Parameters:
        -start: start time,
        -end:  deadline,
    Return:
        -1. the history records of users build failed by userid
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
        cond = {"reason": {"$ne": ""},
                "created_at": {"$gte": start, "$lte": end}}
        fields = {
            "appversion": 1, "reason": 1, "created_at": 1,
            "_id": 0, "log_url": 1}
        data = [{
            'appversion': s.get('appversion'),
            'time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
                s.get('created_at'))),
            "reason": s.get("reason"),
            "log_url": s.get("log_url")}
            for s in LocalizationSnap.find(cond, fields).sort(
                'created_at', -1)]
        return json_response_ok(data)
    else:
        return json_response_error(METHOD_ERROR, msg="http method wrong")

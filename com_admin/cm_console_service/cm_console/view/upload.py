# -*- coding: utf-8 -*-
import logging

from cm_console.model.common import classing_model
from cm_console.view.upload_base import offline_data, online_data

from cm_console.utils.common import common_filter

from armory.marine.respcode import PARAM_ERROR
from armory.marine.json_rsp import json_response_ok, json_response_error

_LOGGER = logging.getLogger(__name__)
_ADMIN = "admin"


def online(appname, modelname, item_ids, server):
    Model_Class = classing_model(modelname)
    items = Model_Class.find(
        appname, {'id': {'$in': item_ids}}, fields={'_id': 0}, toarray=True)
    if not items:
        return json_response_error(PARAM_ERROR, msg="no item find")
    results = online_data(appname, modelname, server, items)
    status = results[0]
    out_msg = results[1]
    data = {}
    data["success"] = results[2]
    data["failed"] = results[3]
    data['userlog'] = [common_filter(i) for i in data.get('success')]
    data['memo'] = 'online to %s' % server
    if status == -1:
        return json_response_error(PARAM_ERROR, msg="UNKNOWN UPLOAD SERVER")
    elif status == 0:
        return json_response_ok(data, msg="upload successfully")
    else:
        return json_response_error(status, data, msg=out_msg)


def offline(appname, modelname, item_ids, server):
    Model_Class = classing_model(modelname)
    items = Model_Class.find(
        appname, {'id': {'$in': item_ids}}, fields={'_id': 0}, toarray=True)
    if not items:
        return json_response_error(PARAM_ERROR, msg="no item find")
    results = offline_data(appname, modelname, server, items)
    status = results[0]
    data = {}
    data["success"] = results[1]
    data["failed"] = results[2]
    data['userlog'] = [common_filter(i) for i in data.get('success')]
    data['memo'] = 'offline from %s' % server
    if status == -1:
        return json_response_error(PARAM_ERROR, msg="UNKNOWN UPLOAD SERVER")
    elif status == 0:
        if server == _ADMIN:
            data['success_list'] = data.get('success')
            data['failed_list'] = data.get('failed')
            suc_ids = fail_ids = []
            if data["failed"]:
                fail_ids = [i.get('id') for i in data.get('failed')]
            if data["success"]:
                suc_ids = [i.get('id') for i in data.get('success')]
            data["success"] = suc_ids
            data["failed"] = fail_ids
            data['memo'] = 'delete it from admin'
        return json_response_ok(data, msg="delete successfully")
    else:
        return json_response_error(status, data, msg="del error")

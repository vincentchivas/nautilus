# -*- coding:utf-8 -*-
import logging

from armory.marine.json import ArmoryJson
from armory.marine.respcode import PARAM_ERROR
from armory.marine.json_rsp import json_response_error
from armory.marine.access_control import access_control, exception_handler

from cm_console.api import request, app
from cm_console.view.upload import online, offline

from cm_console.decorator import savelog, check_url_params

_LOGGER = logging.getLogger(__name__)


@app.route('/<appname>/<modelname>/online', methods=['POST', 'OPTIONS'])
@savelog
@exception_handler
@access_control
@check_url_params
def upload_model(appname, modelname):
    '''
    upload api to upload
    Request URL:  /predata/upload
    Http Method:  POST
    Parameters:{
        "items":["123", "124"],
        "server":"local"}
    Return :{
     "status":0
     "data":{}}
    '''
    try:
        req_dict = ArmoryJson.decode(request.data)
    except:
        return json_response_error(PARAM_ERROR, msg="json format error")
    id_list = []
    item_ids = req_dict.get("items")
    server = req_dict.get("server")
    try:
        id_list.extend(map(int, item_ids))
    except:
        return json_response_error(PARAM_ERROR, msg="item ids format error")
    # view logic
    return online(appname, modelname, id_list, server)


@app.route('/<appname>/<modelname>/offline', methods=['POST', 'OPTIONS'])
@savelog
@exception_handler
@access_control
@check_url_params
def drop_model(appname, modelname):
    """
    offline api to offline data
    Request URL:  /predata/offline
    Http Method:  POST
    Parameters:{
        "items":["123", "124"],
        "server":"local"}
    Return :{
     "status":0
     "data":{}}
    """
    try:
        req_dict = ArmoryJson.decode(request.data)
    except:
        return json_response_error(PARAM_ERROR, msg="json format error")
    id_list = []
    item_ids = req_dict.get("items")
    server = req_dict.get("server")
    try:
        id_list.extend(map(int, item_ids))
    except:
        return json_response_error(PARAM_ERROR, msg="item ids format error")
    # view logic
    return offline(appname, modelname, id_list, server)

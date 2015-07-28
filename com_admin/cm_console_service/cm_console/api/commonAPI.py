# -*- coding:utf-8 -*-
import logging
import simplejson

from cm_console.api import request, app
from cm_console.view.common import (
    common_create, common_update, common_detail, common_list, common_delete,
    common_check_unique)

from armory.marine.json import ArmoryJson
from armory.marine.respcode import PARAM_ERROR
from armory.marine.json_rsp import json_response_error
from armory.marine.access_control import access_control, exception_handler

from cm_console.decorator import savelog, check_url_params

_LOGGER = logging.getLogger(__name__)


@app.route(
    '/<appname>/<modelname>/check_unique', methods=['POST', 'OPTIONS'])
@exception_handler
@access_control
@check_url_params
def common_model_unique(appname, modelname):
    '''
    check api to make sure unique field
    Request URL:  /modelname/add/check_unique
    Http Method:  POST
    Parameters:{
        "method":"add",
        "key_name":"key_value"}
        or
        {
         "method": "update",
         "id": xx,
         "key_name":"key_value"}
    Return :{
     "data":{'unique': true}}
    '''
    try:
        req_dict = ArmoryJson.decode(request.data)
    except:
        return json_response_error(PARAM_ERROR, msg="json format error")
    # view logic
    return common_check_unique(appname, modelname, req_dict)


@app.route('/<appname>/<modelname>/add', methods=['POST', 'OPTIONS'])
@savelog
@exception_handler
@access_control
@check_url_params
def common_model_add(appname, modelname):
    '''
    create api to add
    Request URL:  appname/v2/modelname/add
    Http Method:  POST
    Parameters:{
        "name":"xxx",
        "title":"zack"}
    Return :{
     "status":0
     "data":{}}
    '''
    try:
        req_dict = ArmoryJson.decode(request.data)
    except:
        return json_response_error(PARAM_ERROR, msg="json format error")
    # view logic
    return common_create(appname, modelname, req_dict)


@app.route('/<appname>/<modelname>/delete', methods=['POST', 'OPTIONS'])
@savelog
@exception_handler
@access_control
@check_url_params
def common_model_delete(appname, modelname):
    '''
    delete api to delete
    Request URL:  /modelname/delete
    Http Method:  POST
    Parameters:{
        "items":["123", "124"]}
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
    try:
        id_list.extend(map(int, item_ids))
    except:
        return json_response_error(PARAM_ERROR, msg="item ids format error")
    comfirm = req_dict.get("comfirm")
    comfirm = True if comfirm is not None else False
    # view logic
    return common_delete(appname, modelname, comfirm, id_list)


@app.route(
    '/<appname>/<modelname>/update/<item_id>', methods=['POST', 'OPTIONS'])
@savelog
@exception_handler
@access_control
@check_url_params
def common_model_modify(appname, modelname, item_id):
    '''
    notice: update api
    Request URL:  /modelname/update
    Http Method:  POST
    Parameters:{
        "name":"xxx",
        "title":"zack"}
    Return :{
     "status":0
     "data":{}}
    '''
    try:
        req_dict = ArmoryJson.decode(request.data)
    except:
        return json_response_error(PARAM_ERROR, msg="json format error")
    # view logic
    return common_update(appname, modelname, req_dict, int(item_id))


@app.route('/<appname>/<modelname>/edit/<item_id>', methods=['GET', ])
@exception_handler
@access_control
@check_url_params
def common_model_detail(appname, modelname, item_id):
    '''
    notice: get one item detail
    url: /appname/modelname/edit?id=xxxx
    http method: GET
    return:{}
    '''
    return common_detail(appname, modelname, int(item_id))


@app.route('/<appname>/<modelname>/list', methods=['GET', ])
@exception_handler
@access_control
@check_url_params
def common_model_list(appname, modelname):
    '''
    notice: get item list
    url: /appname/modelname/list?
    http method: GET
    return:{
            "status":0,
            "data":{
                "items":[
                {"field1":value1},
                {"field2":value2}],
                "total":123}}
    '''
    query_dict = {}
    query_args = request.args
    for arg in query_args:
        query_dict[arg] = query_args.get(arg)
    sort_strs = query_dict.get('sort')
    sort_dict = {}
    if sort_strs:
        try:
            sort_dict = simplejson.loads(sort_strs)
        except ValueError as e:
            _LOGGER.error(e)
            raise ValueError("sort string error")
    query = {
        'pageindex': int(query_dict.get('index', 1)) - 1,
        'pagesize': int(query_dict.get('limit', 20)),
        'sort_field': sort_dict.get('sortBy', 'last_modified'),
        'sort_way': 1 if sort_dict.get('sortWay') == 'asc' else -1,
        'searchKeyword': query_dict.get('searchKeyword'),
        'start': query_dict.get('start'),
        'end': query_dict.get('end')}
    return common_list(appname, modelname, query)

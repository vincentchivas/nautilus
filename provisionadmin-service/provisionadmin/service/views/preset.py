# -*- coding: utf-8 -*-
import simplejson
import time
import logging
from provisionadmin.utils.json import json_response_error, json_response_ok
from provisionadmin.decorator import exception_handler
from provisionadmin.utils.validate import MetaValidate
from provisionadmin.model.preset import classing_model
from provisionadmin.utils.respcode import PARAM_ERROR, METHOD_ERROR, \
    PARAM_REQUIRED
from bson import ObjectId

_LOGGER = logging.getLogger("view")
_ONE_DAY = 86400.0


def _get_children_model(child_name, parent_model, api_type="add", item_ids=[]):
    '''
     notice: when call add model api, if the model has children models,it
     will return children model data list
    '''
    model_list = []
    Model_Child = classing_model(str(child_name))
    if Model_Child:
        relation = Model_Child.relation
        parents = relation["parent"]
        parent_dict = parents.get(parent_model)
        fields = parent_dict.get("fields")
        display_field = parent_dict.get("display_value")
        results = Model_Child.find({}, fields, toarray=True)
        for result in results:
            model_dict = {}
            model_id = str(result.get("_id"))
            model_dict["value"] = model_id
            model_dict["display_value"] = result.get(display_field)
            if api_type == "edit" and model_id in item_ids:
                model_dict["selected"] = True
            else:
                model_dict["selected"] = False
            model_list.append(model_dict)
    return model_list


@exception_handler()
def preset_model_add(req, model_name):
    '''
    notice: when get request, if the model had children model, it will return
    a child model data list
    when post request, it will return add successfully or failed
    Request URL: /admin/P<model_name>/add
    HTTP Method: GET/POST
    when get:
    Parameters: None
    Return:{
        "child_model":[
        {"value":child_id,
          "display_value":child_field
        }
        ]
        }
    when post:
    Parameters: {"field1":value1, "field2":value2,...}
    Return:{
         "status":0,
         "msg":"add successfully"
        }
    '''
    Model_Name = classing_model(str(model_name))
    if Model_Name:
        if req.method == "POST":
            temp_strs = req.raw_post_data
            try:
                temp_dict = simplejson.loads(temp_strs)
            except ValueError as expt:
                _LOGGER.info("model add api para except:%s", expt)
                return json_response_error(
                    PARAM_ERROR,
                    msg="json loads error,check parameters format")
            required_list = Model_Name.required
            for required_para in required_list:
                if temp_dict.get(required_para) is None:
                    return json_response_error(
                        PARAM_REQUIRED,
                        msg="parameter %s request" % required_para)
            check_dict = Model_Name.type_check
            for key in check_dict:
                value = temp_dict.get(key)
                check_type = check_dict[key].get("type")
                if not MetaValidate.check_validate(check_type, value):
                    return json_response_error(
                        PARAM_REQUIRED,
                        msg="parameter %s invalid" % required_para)
            result = Model_Name.insert(temp_dict)
            if result == "unique_failed":
                return json_response_error(
                    PARAM_ERROR,
                    msg="unque check failed")
            return json_response_ok(
                {}, msg="add %s success" % model_name)
        elif req.method == "GET":
            data = {}
            print Model_Name
            if Model_Name.resources:
                for key in Model_Name.resources:
                    res = Model_Name.resources[key]
                    _LOGGER.info(res)
                    func_name = res.get("func_name")
                    _LOGGER.info(func_name)
                    if hasattr(Model_Name, func_name):
                        val = getattr(Model_Name, func_name)
                        data[func_name] = val
            if Model_Name.relation:
                children = Model_Name.relation.get("children")
                if children:
                    for key in children:
                        model_list = _get_children_model(key, model_name)
                        data[key] = model_list
                    return json_response_ok(data, msg="get %s list" % key)
                else:
                    return json_response_ok({}, msg="no child model")
            else:
                return json_response_ok({}, msg="no relation model")
        else:
            return json_response_error(
                METHOD_ERROR, msg="http method error")
    else:
        return json_response_error(
            PARAM_ERROR, msg="model name %s is not exist" % model_name)


def _search_cond(request, search_fields):
    '''
    notice:when a request comes,combination of the search_fields and the
    request parameter values, return a condition query to mongodb
    '''
    cond = {}
    for key in search_fields.keys():
        value = request.GET.get(key)
        if value:
            value_type = search_fields.get(key)["type"]
            if value_type == "int":
                value = int(value)
            if search_fields.get(key)["front"] == "dropdownlist":
                cond[key] = value
            elif search_fields.get(key)["front"] == "textbox":
                cond[key] = {"$regex": value}
        else:
            if search_fields.get(key) == "date":
                start_time = request.GET.get("start")
                if not start_time:
                    continue
                start = time.mktime(
                    time.strptime(start_time, '%Y-%m-%d'))
                end_time = request.GET.get("end")
                end = time.mktime(
                    time.strptime(end_time, '%Y-%m-%d')) + _ONE_DAY
                cond[key] = {"$gte": start, "$lte": end}
    return cond


@exception_handler()
def preset_model_list(req, model_name):
    '''
    Request URL: /admin/preset_{P<model>}_list
    HTTP Method: GET
    Parameters: None
    Return:
        {
            "status":0,
            "data":{
                "items":[
                {"field1":value1},
                {"field2":value2}
                ]
                }
            }

    '''
    Model_Name = classing_model(str(model_name))
    if Model_Name:
        if req.method == "GET":
            model_list = []
            cond = {}
            try:
                list_api = Model_Name.list_api
            except:
                return json_response_error(
                    PARAM_ERROR, msg="list_api is not configed")
            fields = list_api["fields"]
            filters = list_api["filters"]
            if list_api.get("search_fields"):
                search_fields = list_api["search_fields"]
                cond = _search_cond(req, search_fields)
            results = Model_Name.find(cond, fields=fields, toarray=True)
            for result in results:
                result["id"] = str(result.get("_id"))
                result.pop("_id")
                model_list.append(result)
            data = {}
            data["items"] = model_list
            data["filters"] = filters
            return json_response_ok(data, msg="get list")
        else:
            return json_response_error(
                METHOD_ERROR, msg="http method error")
    else:
        return json_response_error(
            PARAM_ERROR, msg="model name %s is not exist" % model_name)


@exception_handler()
def detail_modify_model(req, model_name, item_id):
    '''
    notice:when a get request comes, it will return one model detail data;
    when a post request comes, it will return update success or not
    Request URL:/admin/P<model_name>/P<int>
    HTTP Method: GET/POST
    when get:
    parameter: None
    return:{
         "item":{
            "field1":value1,
            "field2":value2
            }
        }
    when post:
    parameter:{"field1":value1, "field2:value2"}
    return:{
           "status":0,
           "msg":"save successfully"
        }
    '''
    if not isinstance(item_id, ObjectId):
        item_id = ObjectId(item_id)
    Model_Name = classing_model(str(model_name))
    if Model_Name:
        if req.method == "GET":
            list_api = Model_Name.list_api
            cond = {"_id": item_id}
            fields = list_api["fields"]
            detail_item = Model_Name.find(cond, fields, one=True, toarray=True)
            if detail_item:
                data = {}
                detail_item["id"] = str(detail_item.pop("_id", None))
                data["item"] = detail_item
                if Model_Name.relation:
                    children = Model_Name.relation.get("children")
                    if children:
                        for key in children:
                            item_ids = detail_item.get(key)
                            model_list = _get_children_model(
                                key, model_name,
                                api_type="edit", item_ids=item_ids)
                            data[key] = model_list
                        return json_response_ok(
                            data, msg="edit api get %s list" % key)
                    else:
                        return json_response_ok(data, msg="no child model")
                else:
                    return json_response_ok(data, msg="no relation model")
            else:
                return json_response_error(
                    PARAM_ERROR, msg="the id is not exist")
        elif req.method == "POST":
            required_list = Model_Name.required
            temp_strs = req.raw_post_data
            try:
                temp_dict = simplejson.loads(temp_strs)
            except ValueError as expt:
                _LOGGER.info("model edit api para except:%s", expt)
                return json_response_error(
                    PARAM_ERROR,
                    msg="json loads error,check parameters format")
            for required_para in required_list:
                if not temp_dict.get(required_para):
                    return json_response_error(
                        PARAM_REQUIRED,
                        msg="parameter %s invalid" % required_para)
            check_dict = Model_Name.type_check
            for key in check_dict:
                value = temp_dict.get(key)
                check_type = check_dict[key].get("type")
                if not MetaValidate.check_validate(check_type, value):
                    return json_response_error(
                        PARAM_REQUIRED,
                        msg="parameter %s invalid" % required_para)
            cond = {"_id": item_id}
            if Model_Name.find(cond):
                Model_Name.update(cond, temp_dict)
                return json_response_ok(
                    {}, msg="update %s success" % model_name)
            else:
                return json_response_error(
                    PARAM_ERROR, msg="the id is not exist")
        else:
            return json_response_error(
                METHOD_ERROR, msg="http method error")
    else:
        return json_response_error(
            PARAM_ERROR, msg="model name %s is not exist" % model_name)


def _del_model_with_relations(model_name, item_ids):
    Model_Name = classing_model(str(model_name))
    relation = Model_Name.relation
    parent_dict = {}
    if relation.get("parent"):
        parent_dict = relation.get("parent")
    for item_id in item_ids:
        model = Model_Name.find(
            cond={"_id": ObjectId(item_id)}, one=True, toarray=True)
        if model:
            Model_Name.remove({"_id": ObjectId(item_id)})
            if parent_dict:
                for key in parent_dict:
                    Parent_Model = classing_model(str(key))
                    fields_in_parent = model_name
                    model_list = Parent_Model.find(
                        {fields_in_parent: str(item_id)}, toarray=True)
                    for model in model_list:
                        child_list = model.get(fields_in_parent)
                        child_list.remove(str(item_id))
                        Parent_Model.update(
                            {"_id": model["_id"]},
                            {fields_in_parent: child_list})
            else:
                _LOGGER.info("%s has no parent model" % model_name)
            item_ids.remove(str(item_id))
        else:
            _LOGGER.info(
                "model %s itemid %s is not exist" % (model_name, item_id))
    return item_ids


@exception_handler()
def preset_model_delete(req, model_name):
    '''
    Request URL: /admin/P<model_name>/delete
    HTTP Method: POST
    Parameters: {"item_ids": ["123","124"]}
    Return:{
        "status":0,
        "msg":"delete successfully"

        }
    '''
    Model_Name = classing_model(str(model_name))
    if Model_Name:
        if req.method == "POST":
            temp_strs = req.raw_post_data
            try:
                temp_dict = simplejson.loads(temp_strs)
            except ValueError as expt:
                _LOGGER.info("model delete api para except:%s", expt)
                return json_response_error(
                    PARAM_ERROR,
                    msg="json loads error,check parameters format")
            item_ids = temp_dict.get("item_ids")
            if not item_ids:
                return json_response_error(PARAM_ERROR, msg="item_id is empty")
            else:
                ids = _del_model_with_relations(str(model_name), item_ids)
                if not ids:
                    return json_response_ok({}, msg="delete successfully")
                else:
                    return json_response_error(
                        PARAM_ERROR, msg="ids:%s invalid" % ids)
        else:
            return json_response_error(
                METHOD_ERROR, msg="http method error")
    else:
        return json_response_error(
            PARAM_ERROR, msg="model name %s is not exist" % model_name)

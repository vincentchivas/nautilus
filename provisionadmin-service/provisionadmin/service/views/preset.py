# -*- coding: utf-8 -*-
import simplejson
import time
from provisionadmin.utils.json import json_response_error, json_response_ok
from provisionadmin.utils.validate import MetaValidate
from provisionadmin.model.preset import config
from provisionadmin.settings import MODELS
from provisionadmin.utils.respcode import PARAM_ERROR, METHOD_ERROR, \
    PARAM_REQUIRED
from bson import ObjectId


def preset_model_add(req, model_name):
    if req.method == "POST":
        temp_strs = req.raw_post_data
        temp_dict = simplejson.loads(temp_strs)
        if MODELS.get(model_name):
            Model_Name = config(str(model_name))
            required_list = Model_Name.required
            for required_para in required_list:
                if not temp_dict.get(required_para):
                    return json_response_error(
                        PARAM_REQUIRED,
                        msg="parameter %s request" % required_para)
            check_dict = Model_Name.type_check
            for check_para in check_dict.keys():
                value = temp_dict.get(check_para)
                check_type = check_dict[check_para].get("type")
                if not MetaValidate.check_validate(check_type, value):
                # 检查类型的同时还可检查长度之类的
                    return json_response_error(
                        PARAM_REQUIRED,
                        msg="parameter %s invalid" % required_para)
            Model_Name.insert(temp_dict)
            return json_response_ok(
                {}, msg="add %s success" % model_name)
        else:
            return json_response_error(
                PARAM_ERROR, msg="model name %s is not exist" % model_name)
    else:
        return json_response_error(
            METHOD_ERROR, msg="http method error")


def preset_model_list(req, model_name):
    if req.method == "GET":
        if MODELS.get(model_name):
            model_list = []
            Model_Name = config(str(model_name))
            cond = {}
            list_api = Model_Name.list_api
            fields = list_api["fields"]
            filters = list_api["filters"]
            search_fields = list_api["search_fields"]
            for key in search_fields.keys():
                value = req.GET.get(key)
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
                        one_day = 86400.0
                        start_time = req.GET.get("start")
                        if not start_time:
                            continue
                        start = time.mktime(
                            time.strptime(start_time, '%Y-%m-%d'))
                        end_time = req.GET.get("end")
                        end = time.mktime(
                            time.strptime(end_time, '%Y-%m-%d')) + one_day
                        cond[key] = {"$gte": start, "$lte": end}
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
                PARAM_ERROR, msg="model name %s is not exist" % model_name)
    else:
        return json_response_error(
            METHOD_ERROR, msg="http method error")


def detail_modify_model(req, model_name, item_id):
    if not isinstance(item_id, ObjectId):
        item_id = ObjectId(item_id)
    if req.method == "GET":
        if MODELS.get(model_name):
            Model_Name = config(str(model_name))
            list_api = Model_Name.list_api
            cond = {"_id": item_id}
            fields = list_api["fields"]
            detail_item = Model_Name.find(cond, fields, toarray=True)
            if detail_item:
                data = {}
                model_one = detail_item[0]
                model_one["id"] = str(model_one["_id"])
                model_one.pop("_id")
                data["item"] = model_one
                return json_response_ok(
                    data, msg="get one  detail")
            else:
                return json_response_error(
                    PARAM_ERROR, msg="the id is not exist")
        else:
            return json_response_error(
                PARAM_ERROR, msg="model name %s is not exist" % model_name)
    elif req.method == "POST":
        if MODELS.get(model_name):
            Model_Name = config(str(model_name))
            required_list = Model_Name.required
            temp_strs = req.raw_post_data
            temp_dict = simplejson.loads(temp_strs)
            for required_para in required_list:
                if not temp_dict.get(required_para):
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
                PARAM_ERROR, msg="model name %s is not exist" % model_name)
    else:
        return json_response_error(
            METHOD_ERROR, msg="http method error")


def preset_model_delete(req, model_name):
    if req.method == "POST":
        if MODELS.get(model_name):
            Model_Name = config(str(model_name))
            temp_strs = req.raw_post_data
            temp_dict = simplejson.loads(temp_strs)
            item_ids = temp_dict.get("item_ids")
            if not item_ids:
                return json_response_error(PARAM_ERROR, msg="item_id is empty")
            else:
                cond = {}
                for item_id in item_ids:
                    cond["_id"] = ObjectId(item_id)
                    Model_Name.remove(cond)
            return json_response_ok({}, msg="delete successfully")
        else:
            return json_response_error(
                PARAM_ERROR, msg="model name %s is not exist" % model_name)
    else:
        return json_response_error(
            METHOD_ERROR, msg="http method error")

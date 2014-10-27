# -*- coding: utf-8 -*-
# import simplejson
from provisionadmin.utils.json import json_response_error, json_response_ok
from provisionadmin.model.preset import config
from provisionadmin.settings import MODELS
from provisionadmin.utils.respcode import PARAM_ERROR, METHOD_ERROR


def preset_model_add(req, model_name):
    if req.method == "POST":
        temp_dict = {}
        temp_dict["name"] = "new123"
        temp_dict["url"] = "www.baidu.com"
        if MODELS.get(model_name):
            Model_Name = config(str(model_name))
            Model_Name.insert(temp_dict)
            return json_response_ok({}, msg="add %s success" % model_name)
        else:
            return json_response_error(
                PARAM_ERROR, msg="model name %s is not exist" % model_name)
    else:
        return json_response_error(
            METHOD_ERROR, msg="http method error")

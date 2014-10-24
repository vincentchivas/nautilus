# -*- coding: utf-8 -*-
# import simplejson
from provisionadmin.utils.json import json_response_error, json_response_ok
from provisionadmin.model.preset import CLASS_NAME


def bookmark_add(req):
    data = {}
    data["name"] = CLASS_NAME.name
    return json_response_ok(data, msg="add book mark success")

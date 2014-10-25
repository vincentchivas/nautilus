# -*- coding: utf-8 -*-
# import simplejson
from provisionadmin.utils.json import json_response_error, json_response_ok
from provisionadmin.model.preset import config


def bookmark_add(req):
    Bookmark = config("bookmark")
    temp_dict = {}
    temp_dict["name"] = "new123"
    temp_dict["url"] = "www.baidu.com"
    item = Bookmark.insert(temp_dict)
    data = {}
    data["item"] = item
    return json_response_ok(data, msg="add book mark success")

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: qtgan
# Date: 2013/12/18

import os
import sys
import time
from django.http import HttpResponse as http
from dolphinop.db.base import MongodbStorage
from dolphinop.service.utils.common_op import get_logger, get_params, json_response, now, \
    parse_rule
from dolphinop.service.errors import internal_server_error, resource_not_modified
from dolphinop.service.utils.content import ALL_FLAG, BASE_PARAS, RULE_ORIGINIZE

NAV_FUNCTION = ("navigation", "shortcut", "hotsearch")
NAV_DB = MongodbStorage()
setattr(NAV_DB, 'table', 'websitesnav')


def _filter_fields(sections, fields):
    result = {}
    for section in sections:
        for key, value in section.items():
            if key in fields:
                result[key] = value
        return result


def sort_by_id(list_dict):
    return list_dict['_sync_key']['id']


@json_response
def fetch(request):
    try:
        self_fields = ('_data',)
        request_paras = get_params(request, "get", BASE_PARAS)
        if isinstance(request_paras, http):
            return request_paras
        cond = {}
        print request_paras
        for key, value in request_paras.items():
            if value is not None:
                match = RULE_ORIGINIZE[key]
                if match[1] == 1:
                    cond.update(eval(match[0] % value))
                else:
                    cond.update(eval(match[0] % (value, value)))
        result_dict = {
            "mt": request.GET.get("mt"),
            "navigation": {},
            "shortcut": [],
            "hotsearch": []
        }

        # cond.update({"function": func})
        results = NAV_DB.get_item(cond, {'_id': 0})
        # results = parse_rule(results, ['src', 'lc'])
        if len(results) == 0:  # no result found
            return resource_not_modified(request, "websitesnav")

        mt_dict = {
            "navigation": result_dict["mt"],
            "hotsearch": result_dict["mt"],
            "shortcut": result_dict["mt"]
        }
        print request.GET.get("mt")
        for result in results:
            result["function"].encode("ascii")
            if result['mt'] > mt_dict[result["function"]]:
                mt_dict[result["function"]] = result['mt']
                result_dict[result["function"]] = result["_data"]
            if result["mt"] > result_dict["mt"]:
                result_dict["mt"] = result["mt"]

        return result_dict
    except Exception, e:
        # LOGGER.exception(e)
        return internal_server_error(request, e, sys.exc_info())

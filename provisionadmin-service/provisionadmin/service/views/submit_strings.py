# -*- coding: utf-8 -*-
"""
@author: yqyu
@date: 2014-07-15
@description: the page of strings list
"""

import simplejson as json

from provisionadmin.utils.respcode import PARAM_REQUIRED, METHOD_ERROR
from provisionadmin.utils.json import json_response_error, json_response_ok
from provisionadmin.decorator import check_session, exception_handler
from provisionadmin.model.i18n import LocalizationStrings, LocalizationInfo, \
    LocalizationTask


_XMLNS_XLIFF = 'urn:oasis:names:tc:xliff:document:1.2'
_UNTRANSLATED = 'Untranslated'
_TRANSLATED = 'Translated'
_FINISHED = 'Finishd'
_HISTORICAL_DOCUMENT = 'Historical document'


@exception_handler()
@check_session
def submit_strings(request, user):
    """
    POST: Submit string need to be check

    Parameters:
        -json: the information of translated string,
    Return:
        -1. The lists of text need to translated
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
    if request.method == 'POST':
        uid = user.get("_id")
        dict_str = request.raw_post_data
        temp_dict = json.loads(dict_str)
        platform = temp_dict["platform"]
        appname = temp_dict["appname"]
        appversion = temp_dict["appversion"]
        category = temp_dict["category"]
        locale = temp_dict["locale"]
        string_items = temp_dict['items']
        data = {}
        item_list = []
        for item in string_items:
            name = item.get('name')
            cond = {
                "appname": appname, "appversion": appversion,
                'platform': platform, 'category': category,
                "locale": locale}
            str_pass = item["str_pass"]
            items = LocalizationStrings.update_string_status(
                cond, name, modifier_id=uid, str_pass=str_pass)
            item_list.append(items)

        data["items"] = item_list
        return json_response_ok(data)
    else:
        return json_response_error(METHOD_ERROR, msg="http method wrong")


@exception_handler()
def update_strings(request):
    """
    Refresh the history data

    Parameters:
        -None
    Return:
        -1. The lists of text need to translated
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
        required_list = ('platform', 'appname', 'category', 'appversion')
        for required_para in required_list:
            para_data = request.GET.get(required_para)
            if not para_data:
                return json_response_error(
                    PARAM_REQUIRED,
                    msg="parameter '%s' invalid" % required_para)

        temp_dict = request.GET
        platform = temp_dict["platform"]
        appname = temp_dict["appname"]
        appversion = temp_dict["appversion"]
        category = temp_dict["category"]

        info_ids = LocalizationInfo.get_id_by_app(
            platform, appname, category, appversion)
        """
        history_cond = {}
        history_cond['localization_info'] = {'$in': info_ids}
        history_cond['finished'] = True
        history_doc = {"status": _HISTORICAL_DOCUMENT}
        LocalizationStrings.update(history_cond, history_doc, multi=True)

        draft_cond = {}
        draft_cond['target'] = {'$in': info_ids}
        draft_cond['finished'] = False
        draft_doc = {"status": _UNTRANSLATED}
        LocalizationStrings.update(draft_cond, draft_doc, multi=True)
        """
        finished_cond = {}
        finished_cond['localization_info'] = {'$in': info_ids}
        finished_cond["status"] = "Translated"
        finished_doc = {"status": _FINISHED}
        LocalizationStrings.update(finished_cond, finished_doc, multi=True)

        to_be_check_cond = {}
        to_be_check_cond['localization_info'] = {'$in': info_ids}
        to_be_check_cond["status"] = "Not Validated"
        draft_doc = {"status": _TRANSLATED}
        LocalizationStrings.update(to_be_check_cond, draft_doc, multi=True)
        for info_id in info_ids:
            LocalizationTask.update_old_data_count(info_id)

        return json_response_ok({}, msg="data is update")
    else:
        return json_response_error(METHOD_ERROR, msg="http method wrong")

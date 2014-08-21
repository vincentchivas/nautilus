# -*- coding: utf-8 -*-

from provisionadmin.utils.respcode import PARAM_REQUIRED, \
    METHOD_ERROR  # , UNKNOWN_ERROR
from provisionadmin.utils.json import json_response_error, json_response_ok
from provisionadmin.decorator import check_session, exception_handler
from provisionadmin.model.i18n import LocalizationStrings
from provisionadmin.utils import exception
import all_json
import simplejson as json


@exception_handler()
@check_session
def edit(request):
    uid = request.session.get('uid')
    if not uid:
        raise exception.AuthFailureError("can not get uid")
    if request.method == 'GET':
        # need to convert the format of module path to list
        data = {}
        required_list = ('appname', 'appversion', 'locale')
        for required_para in required_list:
            para_data = request.GET.get(required_para)
            if not para_data:
                return json_response_error(
                    PARAM_REQUIRED,
                    msg="parameter '%s' invalid" % required_para)
        appname = request.GET.get('appname')
        appversion = request.GET.get('appversion')
        locale = request.GET.get("locale")
        modulepath = request.GET.get('module')
        name = request.GET.get("name")
        import time
        print "before function: %s" % time.time()
        data = LocalizationStrings.generate_edit_data(
            appname, appversion, locale, modulepath, name)
        data["filters"] = all_json.edit_filters
        print "befor response: %s" % time.time()
        return json_response_ok(data)
    elif request.method == 'POST':
        dict_str = request.raw_post_data
        temp_dict = json.loads(dict_str)
        appname = temp_dict["appname"]
        appversion = temp_dict["appversion"]
        locale = temp_dict["locale"]
        string_items = temp_dict['items']
        data = {}
        item_list = []
        for item in string_items:
            module_path = item.get('module_path')
            name = item.get('name')
            alias = item.get('alias')
            items = LocalizationStrings.update_alias(
                appname, appversion, locale, module_path, name, alias,
                modifier_id=uid)
            if items["finished"]:
                items["status"] = "finished"
            else:
                items["status"] = "draft"
            items.pop("finished")
            item_list.append(items)
        data["items"] = item_list
        return json_response_ok(data)
    else:
        return json_response_error(METHOD_ERROR, msg="http method wrong")


@exception_handler()
@check_session
def mark_cope(request):
    if request.method == 'POST':
        dict_mark = request.raw_post_data
        temp_dict = json.loads(dict_mark)
        cond = {}
        appname = temp_dict["appname"]
        appversion = temp_dict["appversion"]
        locale = temp_dict["locale"]
        module_path = temp_dict["module_path"]
        name = temp_dict["name"]
        cond, string_item = LocalizationStrings.set_default(
            appname, appversion, locale, module_path, name)
        #cond["module_path"] = temp_dict["module_path"]
        #cond["localization_info"] = LocalizationInfo.get_by_app_locale(
        #    appname, appversion, locale, id_only=True)
        #cond["name"] = temp_dict["name"]
        string_item["marked"] = temp_dict["marked"]
        LocalizationStrings.update(cond, string_item)
        return json_response_ok()
    else:
        return json_response_error(METHOD_ERROR, msg="http method wrong")

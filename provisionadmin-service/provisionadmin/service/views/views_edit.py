# -*- coding: utf-8 -*-
"""
@author: yqyu
@date: 2014-07-15
@description: the page of strings list
"""

from provisionadmin.utils.respcode import PARAM_REQUIRED, \
    METHOD_ERROR
from provisionadmin.utils.json import json_response_error, json_response_ok
from provisionadmin.decorator import check_session, exception_handler
from provisionadmin.model.i18n import LocalizationStrings, LocalizationHistory
from provisionadmin.utils import exception
from provisionadmin.service.views.all_json import edit_filters
import simplejson as json
from xml.etree import ElementTree as ET


_XMLNS_XLIFF = 'urn:oasis:names:tc:xliff:document:1.2'


@exception_handler()
@check_session
def edit(request, user):
    """
    GET: Get string need to be translated
    Parameters:
        -appname: package name,
        -appversion: package version,
        -locale: Country code,

    POST: Save the translation document
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
    if request.method == 'GET':
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
        data = LocalizationStrings.generate_edit_data(
            appname, appversion, locale, modulepath, name)
        data["filters"] = edit_filters
        return json_response_ok(data)
    elif request.method == 'POST':
        uid = user._id
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
            tag_name = item.get('tag_name')
            xml_file = item.get('xml_file')
            alias = item.get('alias')
            alias = update_alias(alias)
            for alias_item in alias:
                content = alias_item.get("content")
                check_content(content)
            items = LocalizationStrings.update_alias(
                appname, appversion, locale, module_path, name, alias,
                modifier_id=uid)
            if items["finished"]:
                items["status"] = "finished"
            else:
                items["status"] = "draft"
            items.pop("finished")
            item_list.append(items)

            LocalizationHistory.insert_history(
                appname, appversion, locale, module_path, name, alias,
                tag_name, xml_file, modifier_id=uid)
        data["items"] = item_list
        return json_response_ok(data)
    else:
        return json_response_error(METHOD_ERROR, msg="http method wrong")


def adjust_alias(alias):
    """
    change alias's type from unicode to utf-8 & update alias with namespace
    Parameters:
        -alias: the value of string,
    Return:
        -alias: the value of string,
    """
    if type(alias) is unicode:
        alias = alias.encode('utf-8')
    return alias.replace(
        "<xliff:g", "<xliff:g xmlns:xliff=\"%s\"" % _XMLNS_XLIFF)


def check_content(content):
    """
    Check whether there are illegal XML tags in the translated text
    or
    Check whether the translated text is None
    Parameters:
        -content: the content of translated text,
    Return:
        -excetion
    """
    if type(content) is dict:
        content = content['content']
    if content is None:
        raise exception.DataError("content is empty")
    if content:
        try:
            ET.fromstring('<test>%s</test>' % adjust_alias(content))
        except Exception:
            raise exception.DataError("the alias is not valid")


def update_alias(alias):
    """
    Check whether the content of translated text is None
    if the content is None, the assignment to an empty string
    Parameters:
        -alias: the content of translated text,
    Return:
        -alias: empty string or content of translated text,
    """
    if len(alias) > 1:
        for alias_item in alias:
            content = alias_item.get("content")
            if content is None:
                alias_item["content"] = ""
    else:
        content = alias[0].get("content")
        if content is None:
            alias[0]["content"] = ""
    return alias


@exception_handler()
@check_session
def mark_cope(request, user):
    """
    Mark the translator cannot confirm copy
    Parameters:
        -json: the information of needed to mark,
    Return:
        -1. The lists of the translation task
        {
            "status": 0,
            "data":{
            }
         }
        -2. error http method
        {
            "status": 11,
            "data":{
            }
         }
    """
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
        string_item["marked"] = temp_dict["marked"]
        LocalizationStrings.update(cond, string_item)
        return json_response_ok()
    else:
        return json_response_error(METHOD_ERROR, msg="http method wrong")

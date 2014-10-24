# -*- coding: utf-8 -*-
"""
@author: zhhfang
@date: 2014-07-15
@description: define the i18n relevant models
"""

import logging
import os
import re
import glob
import time
import zipfile
from bson import ObjectId
from xml.etree import ElementTree as ET
import subprocess
import xlwt

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

from django.conf import settings

from provisionadmin.model.base import ModelBase
from provisionadmin.utils.common import now_timestamp
from provisionadmin.utils import exception, get_api
from provisionadmin.utils.qrcode_generator import make_qr
# from provisionadmin.service.views.views_add import _process_locales

_LOGGER = logging.getLogger("model")
STATIC_ROOT = settings.STATIC_ROOT
HOST = settings.HOST
_XMLNS_XLIFF = 'urn:oasis:names:tc:xliff:document:1.2'
_XMLNS_TOOLS = 'http://schemas.android.com/tools'

_UNTRANSLATED = 'Untranslated'
_TRANSLATED = 'Translated'
_TO_BE_CHECK = 'To be check'
_FINISHED = 'Finished'
_HISTORICAL_DOCUMENT = 'Historical document'

_ADMIN = 2
_COUNTRY_PM = 3
_CHARGE = 5
_TRANSLATOR = 4

STRING_TAG_RE = r'^<string .*?name="(.*?)".*?>(.*?)</string>'
string_tag_compile = re.compile(STRING_TAG_RE, re.S)
ARRAY_TAG_RE = r'^<item.*?>(.*?)</item>'
ARRAY_TAG_RE_BLANK = r'^<item.*?/>'
array_tag_compile = re.compile(ARRAY_TAG_RE, re.S)
array_tag_blank_compile = re.compile(ARRAY_TAG_RE_BLANK, re.S)

ET.register_namespace('xliff', _XMLNS_XLIFF)
ET.register_namespace('tools', _XMLNS_TOOLS)


class LocalizationStrings(ModelBase):

    """
    examples:
        {
            "module_path": ["a", "b", "c"],
            "localization_info": 1231231,
            "name": "home_add",
            "tag_name": "string",
            "alias": "home add",
            "status": "Untranslated/Historical->Translated->
            To be check->Finished/Untranslated"
        },
        the alias can also be:
            [
                null,
                'test'
            ]
    """

    db = 'i18n'
    collection = "localization_strings"

    required = (
        'module_path', 'localization_info', 'name', 'tag_name', 'alias',
        'xml_file')
    optional = (
        ("status", "Untranslated"),
        ("update", False),
        ('marked', '')
    )

    unique = (('module_path', 'localization_info', 'name'),)

    alias_pattern = re.compile(
        r"^[^<>]*(<xliff:g[^<>]*>[^<>]*</xliff:g>[^<>]*)*[^<>]*$", re.M)

    @classmethod
    def get_app_locale_count(
            cls, platform, appname, category, appversion, locale, cond={}):
        """
        Calculate the total number of the string
        in the collection localization_strings
        params: appname, appversion, locale
        return: the total number of the string
        """
        info_id = LocalizationInfo.get_by_app_locale(
            platform, appname, category, appversion, locale, id_only=True)
        if not info_id:
            return 0
        cond['localization_info'] = info_id
        return cls.find(cond).count()

        # left to design detailedly

    @classmethod
    def check_alias(cls, alias, origin_alias):
        """
        Check the current locale with the original English text
        translation content type, and length of the string
        params: alias, origin_alias
        return: True or False
        """
        temp_flag = []
        if type(alias) in (list, tuple):
            alias_len = len(origin_alias)
            for alias_x in xrange(alias_len):
                if(type(alias[alias_x]) is dict):
                    if origin_alias[alias_x].get("content") == "":
                        alias[alias_x]["content"] = ""
                        flag = True
                    else:
                        flag = True if alias[alias_x].get("content") else False
                else:
                    if origin_alias[alias_x] == "":
                        alias[alias_x] = ""
                        flag = True
                    else:
                        flag = True if alias[alias_x] else False
                temp_flag.append(flag)
        return all(temp_flag)

    @classmethod
    def update_alias_to_string(cls, alias, string):
        """
        update the value of alias into string["alias"]
        Parameters:
            -alias: the value of translated text with mark,
            -string: the corresponding details of translated text
        Return:
            -None
        """
        s_alias = string['alias']
        s_alias_len = len(s_alias)
        for i, alias_i in enumerate(alias):
            alias_i_content = alias_i['content']
            if type(s_alias) is list:
                if i >= s_alias_len:
                    break
                s_alias_i = s_alias[i]
                if type(s_alias_i) is dict:
                    s_alias_i['content'] = alias_i_content
                else:
                    s_alias[i] = alias_i_content
            else:
                string['alias'] = alias_i_content

    @classmethod
    def clear_alias(cls, string_item):
        """
        Clear the original English translation content
        params: string_item
        return: True or False
        """
        alias = string_item["alias"]
        if type(alias) in (list, tuple):
            temp = []
            for alias_item in string_item['alias']:
                alias_item = ''
                temp.append(alias_item)
            string_item['alias'] = temp
            return string_item
        if type(alias) is dict:
            string_item['alias']['content'] = ''
        if alias:
            string_item['alias'] = ''
        return string_item

    @classmethod
    def set_default(
            cls, platform, appname, category, appversion, locale,
            module_path, name, save=True):
        """
        If the translation content is not in string collection
        insert a new data in the table
        Parameters::
            -appname: package name,
            -appversion: package version,
            -locale: Country code,
            -module_path: the module path of string or string-array,
            -name: the name of the need to be translated text .
            -save: Whether needed to save
        Return: a Tuple(cond, string_item)
            -cond: query conditions,
            -string_item: the query result set of name

        """
        origin_cond = {
            "appname": appname, "appversion": appversion, "locale": locale,
            "platform": platform, "category": category}
        info_id = LocalizationInfo.find_id_by_unique(origin_cond)
        if not info_id:
            _LOGGER.warn(
                "localization_info not found for appname: %s; appversion: "
                "%s; locale: %s", appname, appversion, locale)
            raise exception.DataError(
                "can not find relevant localization_info")
            # left to implement --- use specified exception class
        cond = {
            'localization_info': info_id, 'module_path': module_path,
            'name': name}
        string_item = cls.find(cond, one=True)
        fields = {"autofill": 1, "reference": 1, "_id": 0}
        task_info = LocalizationTask.find(
            {"target": info_id}, fields, one=True)
        autofill = True if task_info.get("autofill") is None \
            else task_info.get("autofill")
        refer_id = task_info.get("reference")
        if not string_item:
            if not autofill:
                orig_cond = dict(cond)
                orig_cond['localization_info'] = \
                    LocalizationInfo.get_by_app_locale(
                        platform, appname, category,
                        appversion, '', id_only=True)
                string_item = cls.find(orig_cond, one=True)
                string_item = cls.clear_alias(string_item)
            else:
                ref_cond = dict(cond)
                ref_cond['localization_info'] = refer_id
                string_item = cls.find(ref_cond, one=True)

            if not string_item:
                _LOGGER.error(
                    "can not find orig_string_item for cond %s", cond)
                raise exception.UnknownError(
                    "can not find relevant orig_string_item")
            string_item['localization_info'] = info_id
            string_item['status'] = _UNTRANSLATED
            if save:
                cls.insert(string_item)
        return cond, string_item

    @classmethod
    def delete_all_tag(cls, alias):
        """
        Delete the tags added to content of alias
        Parameters::
            -alias: the value of translated text with mark,
        Return:
            -alias: the value of translated text,
        """
        left_str = '[***'
        right_str = '***]'
        alias = alias.replace(left_str, '')
        alias = alias.replace(right_str, '')
        return alias

    @classmethod
    def update_alias(
            cls, platform, category, appname, appversion, locale, module_path,
            name, alias, modifier_id=1):
            # lack of type check and value check
        """
        Update the value of the corresponding alias of
        name in the string collection
        Parameters::
            -appname: package name,
            -appversion: package version,
            -locale: Country code,
            -module_path: the module path of string or string-array,
            -name: the name of the need to be translated text .
            -alias: the value of translated text,
        Return:
            -alias: the value of translated text,
        """
        cond, string_item = cls.set_default(
            platform, appname, category, appversion, locale,
            module_path, name, save=True)
        info_id = LocalizationInfo.get_by_app_locale(
            platform, appname, category, appversion, locale, id_only=True)
        cls.update_alias_to_string(alias, string_item)
        info_cond = {
            "appname": appname, "appversion": appversion, "locale": "",
            "platform": platform, "category": category}
        origin_id = LocalizationInfo.find_id_by_unique(info_cond)
        origin_cond = {
            'localization_info': origin_id, 'name': name,
            'module_path': module_path}
        origin_item = cls.find(origin_cond, one=True)
        if type(string_item['alias']) in (list, tuple):
            check_alias_res = cls.check_alias(
                string_item['alias'], origin_item['alias'])
            temp_alias = []
            for item in string_item['alias']:
                item = cls.delete_all_tag(item)
                temp_alias.append(item)
            string_item['alias'] = temp_alias
        else:
            if origin_item["alias"] == "":
                string_item["alias"] = ""
                check_alias_res = True
            else:
                check_alias_res = True if string_item["alias"] else False
            string_item['alias'] = cls.delete_all_tag(string_item['alias'])
        if check_alias_res:
            string_item['status'] = _TRANSLATED
        else:
            string_item['status'] = _UNTRANSLATED
        if string_item['status'] != _UNTRANSLATED:
            string_item['marked'] = ""
        # the status check of array is left to improving
        _LOGGER.info("update the string: %s", string_item)
        cls.update(cond, string_item)
        fields = {"name": 1, "status": 1, "marked": 1, "_id": 0}
        ret = cls.find(cond, fields, one=True)
        LocalizationTask.update_finish_count(
            info_id, modifier_id=modifier_id)
        return ret

    @classmethod
    def get_refer_id(cls, appname, appversion, platform, category):
        """
        get reference id to compare
        """
        origin_cond = {
            "appname": appname, "appversion": appversion, "locale": "",
            "platform": platform, "category": category}
        origin_id = LocalizationInfo.find_id_by_unique(origin_cond)
        origin_string_count = cls.find(
            {"localization_info": origin_id}).count()
        if origin_string_count < 1:
            appinfo = LocalizationInfo.get_by_app_version(
                appname, platform, category)
            appversion_list = appinfo.get("appversion")
            if len(appversion_list) < 2:
                return None
            else:
                appversion = appversion_list[1]
                origin_cond = {
                    "appname": appname, "appversion": appversion, "locale": "",
                    "platform": platform, "category": category}
                origin_id = LocalizationInfo.find_id_by_unique(origin_cond)
            return origin_id
        else:
            return origin_id

    @classmethod
    def check_origin_alias(cls, origin_id, string_item):
        """
        Check if the value of the corresponding alias of
        name in the string collection is modified
        Parameters::
            -origin_id: package name,
            -string_item: the value of translated text,
        Return:
            -True: the value of translated text,
        """
        name = string_item['name']
        strings_origin_cond = {
            'localization_info': origin_id, 'name': name}
        origin_item = cls.find(strings_origin_cond, one=True)
        if origin_item:
            origin_alias = origin_item["alias"]
            string_alias = string_item["alias"]
            if type(origin_alias) is list:
                origin_alias = \
                    [i.encode('utf-8') for i in origin_alias]
            else:
                if type(origin_alias) is unicode:
                    origin_alias = origin_alias.encode("utf-8")
            if string_alias != origin_alias:
                return True
            else:
                return False
        else:
            return False

    @classmethod
    def update_other_alias(
            cls, appname, appversion, platform, category):
        origin_cond = {
            "appname": appname, "appversion": appversion, "locale": "",
            "platform": platform, "category": category}
        origin_id = LocalizationInfo.find_id_by_unique(origin_cond)

        # name = string_item['name']
        string_origin_cond = {
            'localization_info': origin_id, 'update': True}
        string_update = cls.find(
            string_origin_cond,
            {"name": 1, "_id": 0}, toarray=True)
        string_update = [i["name"] for i in string_update]

        other_info_cond = {
            "appname": appname, "appversion": appversion,
            "locale": {"$ne": ""}, "platform": platform, "category": category}
        other_ids = LocalizationInfo.find(other_info_cond, id_only=True)
        cond = {}
        cond['localization_info'] = {'$in': other_ids}
        cond['name'] = {'$in': string_update}
        cls.update(cond, {"status": _UNTRANSLATED}, multi=True)

    @classmethod
    def update_string_status(cls, cond, name, modifier_id=1, str_pass=True):
            # lack of type check and value check
        """
        Update the status of strings
        Parameters::
            -cond: package name,
        Return:
            -alias: the value of translated text,
        """
        info_id = LocalizationInfo.find(cond, {"_id": 1}, one=True).get("_id")
        task_info = LocalizationTask.find({"target": info_id}, one=True)
        if task_info.get("task_status") != "To be check":
            return
        update_cond = {'localization_info': info_id, 'name': name}
        string_item = {}
        if str_pass:
            string_item['status'] = _FINISHED
        else:
            string_item['status'] = _UNTRANSLATED
        _LOGGER.info("update the string: %s", string_item)
        cls.update(update_cond, string_item)
        fields = {"name": 1, "status": 1, "marked": 1, "_id": 0}
        ret = cls.find(update_cond, fields, one=True)
        LocalizationTask.update_finish_count(
            info_id, modifier_id=modifier_id)
        return ret

    @classmethod
    def get_by_app_locale(
            cls, platform, appname, category, appversion, locale,
            cond={}, toarray=True, **kwargs):
        """
        return locale information
        Parameters::
            -appname: package name,
            -appversion: package version,
            -locale: Country code,
            -cond: query conditions,
            -toarray: whether return array of locale
        Return:
            -return array of locale information
        """
        cond['localization_info'] = LocalizationInfo.get_by_app_locale(
            platform, appname, category, appversion, locale, id_only=True)
        return cls.find(cond=cond, toarray=toarray, **kwargs)
        # ensure return array by default

    @classmethod
    def get_by_module(
            cls, appname, appversion, locale, module_path, name=None):
        """
        return module information
        Parameters::
            -appname: package name,
            -appversion: package version,
            -locale: Country code,
            -cond: query conditions,
            -toarray: whether return array of locale
        Return:
            -return array of locale information
        """
        cond = {'module_path': module_path}
        if name:
            cond['name'] = name
        return cls.get_by_app_locale(appname, appversion, locale, cond)

    @classmethod
    def strings_to_dict(cls, data):
        """
        Converte the data to dict type
        Parameters::
            -data: needed to converte data,
        Return:
            -ret: converted data
        """
        ret = {}
        if data:
            for string in data:
                ret[string['name']] = string
        return ret

    @classmethod
    def handler_special_character(cls, strings):
        """
        Add tags to the special string
        Parameters::
            -strings: Contain special characters of data,
        Return:
            -strings: the data which added tag
        """
        alias_pattern = r'<xliff:g.*?</xliff:g>|%s|%d|<u>|</u>|<b>|</b>|'
        alias_pattern = alias_pattern + r'<a.*>|</a>|<g>|</g>|<br/>\n|\\n|'
        alias_pattern = alias_pattern + r'&amp;|&lt;.*?&gt;|&lt;.*?/.*&gt;|'
        alias_pattern = alias_pattern + r'%\d\$d|%\d\$s|<html><body>|'
        alias_pattern = alias_pattern + r'</body></html>|@string/.+'
        alias_re = re.compile(alias_pattern)
        alias_match = alias_re.findall(strings.get('alias'))
        alias_match = list(set(alias_match))
        if alias_match is not None:
            for i in alias_match:
                repl = '[***' + i + '***]'
                strings['alias'] = strings['alias'].replace(i, repl)
        return strings

    @classmethod
    def generate_edit_data(
            cls, appname, appversion, locale, platform, category,
            module_path=None, name=None, store=True):
        """
        Get text need to be translated
        Parameters::
            -appname: package name,
            -appversion: package version,
            -locale: Country code,
            -module_path: the module path of string or string-array,
            -name: the name of the need to be translated text .
        Return:
            -ret_content: All corresponding information of need
            to be translated text
        """

        cond = {}
        ret_content = []
        if module_path is not None:
            # ret_content.append({'module_path': module_path})
            cond['module_path'] = module_path
        if name is not None:
            cond['name'] = name

        # get info, reference(locale)
        info_id = LocalizationInfo.get_by_app_locale(
            platform, appname, category, appversion, locale, id_only=True)
        task = LocalizationTask.find({'target': info_id}, one=True)
        if not task:
            raise exception.DataError(
                "can not find relevant task for target %s" % info_id)

        is_locked = task["is_locked"]

        if task.get('reference') is not None:
            reference_info = LocalizationInfo.find({
                '_id': task['reference']}, one=True)
            reference_locale = reference_info['locale']
        else:
            reference_locale = None

        # get data of cur, rCN, origin and reference
        data = cls.strings_to_dict(cls.get_by_app_locale(
            platform, appname, category, appversion, locale, cond))
        if reference_locale is not None:
            reference_data = cls.strings_to_dict(cls.get_by_app_locale(
                platform, appname, category, appversion,
                reference_locale, cond))
        else:
            reference_data = {}
        china_data = cls.strings_to_dict(cls.get_by_app_locale(
            platform, appname, category, appversion, 'zh-rCN', cond))
        origin_data = cls.strings_to_dict(cls.get_by_app_locale(
            platform, appname, category, appversion, '', cond))
        for name, orig_string in origin_data.iteritems():
            s_alias = orig_string['alias']
            ret_alias = []
            orig_string.setdefault('tips', None)
            orig_string.pop('_id')
            orig_string.pop('finished', None)
            orig_string.pop('localization_info')
            reference_string = reference_data.get(name)
            if reference_string is not None:
                if reference_string.get('alias'):
                    if type(reference_string['alias']) is not list:
                        cls.handler_special_character(reference_string)

            china_string = china_data.get(name)
            string = data.get(name)
            if string:
                if string.get('alias'):
                    if type(string['alias']) is not list:
                        cls.handler_special_character(string)
            if type(s_alias) is list:
                is_list = True
                alias_count = len(s_alias)
                # orig_string['type'] = 'array'
            else:
                is_list = False
                alias_count = 1
                # orig_string['type'] = 'item'
            for i in xrange(alias_count):
                new_alias_item = {
                    'content': None, 'zh-rCN': None, 'en-US': None,
                    'reference': None, 'tips': None}
                if type(s_alias[i]) is list:
                    is_dict = True
                else:
                    is_dict = False
                if is_list and is_dict:
                    new_alias_item['tips'] = s_alias[i].get('tips')
                ret_alias.append(new_alias_item)
                for alias_name, the_string in (
                        ('content', string), ('zh-rCN', china_string),
                        ('reference', reference_string),
                        ('en-US', orig_string)):
                    if not the_string or (
                        not the_string.get('alias') and
                        the_string.get('alias') != '') or (
                            i > 0 and len(the_string['alias']) < (i + 1)):
                        continue
                    if is_list:
                        cur_alias_item = the_string['alias'][i]
                        if type(s_alias[i]) is dict:
                            new_alias_item[alias_name] = cur_alias_item[
                                'content'] if cur_alias_item and 'content' \
                                in cur_alias_item else None
                        else:
                            new_alias_item[alias_name] = cur_alias_item
                    else:
                        new_alias_item[alias_name] = the_string['alias']
            orig_string['alias'] = ret_alias
            orig_string['status'] = string.get("status") if string and \
                string.get('status') else _UNTRANSLATED
            orig_string['marked'] = string.get('marked') if string and \
                string.get('marked') else ''
            if store:
                picture_info = LocalizationPicture.get_picture_by_appname(
                    appname, orig_string["name"])
                orig_string['picture_url'] = picture_info.get("pic_url")
                orig_string['description'] = picture_info.get("description")
            ret_content.append(orig_string)

        return is_locked, ret_content

    @classmethod
    def to_xml_element(cls, data, level=1, at_end=False):
        """
        from
            string_item
        to
            <string name="test">haha</string>
                      or
            <string name="test">
                <item>haha1</item>
                <item>haha2</item>
            </string>
            or
            <plurlas name="test">
                <item quantity="xxx">haha1</item>
                <item quantity="yyy">haha2</item>
            </plurlas>

        alias may like      hour<xliff:g id="xxx">%d</xliff:g>now
        """
        ele = ET.Element(data['tag_name'], {'name': data['name']})
        alias = data['alias']
        if isinstance(alias, list):
            ele.text = "\n%s" % (" " * 4 * (level + 1))
            max_alias_index = len(alias) + 1
            for alias_i, alias_a in enumerate(alias):
                child = ET.Element('item')
                child.text = alias_a
                if alias_i == max_alias_index:
                    child.tail = "\n%s" % (" " * 4 * level)
                else:
                    child.tail = "\n%s" % (" " * 4 * (level + 1))
                ele.append(child)
        else:
            ele.text = alias
        ele.tail = "\n%s" % (" " * 4 * level if not at_end else (level + 1))
        return ele
    # unused as re-factor, leave to improve

    @classmethod
    def adjust_alias(cls, alias):
        """
        change alias's type from unicode to utf-8 & update alias with namespace
        Parameters::
            -alias: the value of string,
        Return:
            -alias: the value of string,
        """
        if type(alias) is unicode:
            alias = alias.encode('utf-8')
        return alias.replace(
            "<xliff:g", "<xliff:g xmlns:xliff=\"%s\"" % _XMLNS_XLIFF)

    @classmethod
    def refresh_app_strings(
            cls, platform, appname, category, appversion, locale):
        """
        Refresh the corresponding content when initializing the database
        Parameters::
            -appname: package name,
            -appversion: package version,
            -locale: Country code,
        Return:
            -result: {'add': 0, 'delete': 0, 'update': 0}
        """
        result = {'add': 0, 'delete': 0, 'update': 0}
        strings = cls.get_by_app_locale(
            platform, appname, category, appversion, locale)
        orig_strings = cls.get_by_app_locale(
            platform, appname, category, appversion, '')
        if not strings or not orig_strings:
            return result
        strings = cls.strings_to_dict(strings)
        orig_strings = cls.strings_to_dict(orig_strings)
        ids_to_delete = []
        for name, string in strings.iteritems():
            orig_string = orig_strings.get(name)
            if orig_string is None:
                ids_to_delete.append(string['_id'])
                continue
            if string['xml_file'] != orig_string['xml_file']:
                cls.update(
                    {'_id': string['_id']},
                    {'xml_file': orig_string['xml_file']})
                result['update'] += 1
        # maybe use set minus operation is a more efficient way
        if ids_to_delete:
            result['delete'] += len(ids_to_delete)
            cls.remove({'_id': {'$in': ids_to_delete}})
        return result


class LocalizationInfo(ModelBase):

    """
    examples:
        {
            "appname": "dolphinopbrowser",
            "appversion": "11.1.1",
            "locale": "ar",
            "created_at": 1232,
            "creator_id": 1,
        },
    """

    db = 'i18n'
    collection = "localization_info"

    required = ('appname', 'appversion', 'locale', "platform", "category")
    optional = (
        ('creator_id', 1),
        ('creator_id', 1),
    )

    unique = (('appname', 'appversion', 'locale'),)

    @classmethod
    def get_lastest_info(cls, appname=None):
        """
        Get the latest data from the database
        Parameters::
            -appname: package name,
        Return:
            -ret[0]: the list of latest data
            or None
        """
        if appname:
            find_list = cls.find({'appname': appname, 'locale': ''})
        else:
            find_list = cls.find({'locale': ''})
        ret = find_list.sort('created_at', -1).limit(1)
        if ret:
            return ret[0]
        else:
            return None

    @classmethod
    def get_id_by_app(
            cls, platform, appname, category, appversion):
        """
        Get app id information
        Parameters:
            -appname: package name,
            -appname: package name,
            -appversion: package version,
            -locale: Country code,
            -id_only: Only return the value of id
        Return:
            -array: the list of id information
        """
        info_cond = {
            'platform': platform, 'category': category,
            'appname': appname, 'appversion': appversion}
        info_ids = cls.find(info_cond, id_only=True)
        return info_ids

    @classmethod
    def get_by_app_locale(
            cls, platform, appname, category, appversion,
            locale, id_only=False):
        """
        Get information by app locale from the database
        Parameters:
            -appname: package name,
            -appversion: package version,
            -locale: Country code,
            -id_only: Only return the value of id
        Return:
            -array: the list of information
            or id
        """
        cond = {
            'platform': platform, 'appname': appname, 'category': category,
            'appversion': appversion, 'locale': locale}
        if id_only:
            return cls.find_id_by_unique(cond)
        else:
            return cls.find(cond, one=True)
        # ensure return one info item or one info id

    @classmethod
    def get_by_app_version(cls, appname, platform=None, category=None):
        """
        Get appversion information by appname from the database
        Parameters:
            -appname: package name,
        Return:
            -ret: the information of appversion and appname
        """
        cond = {'appname': appname, 'locale': ''}
        if platform:
            cond['platform'] = platform
        if category:
            cond["category"] = category

        find_list = cls.find(cond).sort('appversion', -1)
        ret = {}
        appversion = []
        for i in find_list:
            if appname == "mobi.mgeek.TunnyBrowser":
                if i["appversion"] < "11.2.4":
                    continue
            appversion.append(i["appversion"])
        ret["appname"] = appname
        ret["appversion"] = appversion
        return ret

    @classmethod
    def check_info(
            cls, platform, appname, category, appversion=None,
            locale=None, raise_exception=True):
        """
        Check the database for this appname information
        Parameters:
            -appname: package name,
            -appversion: package version,
            -locale: Country code,
            -raise_exception: If an exception is thrown
        Return:
            -true: the appname in database
            or false: the appname not in  database
            or exception info
        """
        cond = {'platform': platform, 'appname': appname, 'category': category}
        if appversion is not None:
            cond['appversion'] = appversion
        if locale is not None:
            cond['locale'] = locale
        info = cls.find(cond, one=True)
        if not info:
            if raise_exception:
                raise exception.DataError("can not find info for cur cond")
            else:
                return False
        if raise_exception:
            return info
        else:
            return True


class LocalizationTask(ModelBase):

    """
    examples:
        {
            "target": 41241,
            "reference": 42343,
            "creator_id": 1,
            "assign_id": 1,
            "translator_id": [1],
            "created_at": 1404460438,
            "last_built_at": 1404460540,
            "autofill": true
            "is_send_email": false
            "is_locked": false
            "task_status": "Created/Translating/To be check/Finished"
            "strings": {
                "modified_at": 1404460538,
                "modified_id": 1,
                "total": 1231,
                "uncheck: 123,
                "untranslated": 123,
            }
        }
    """

    db = 'i18n'
    collection = "localization_task"

    required = ('target',)
    optional = (
        ('creator_id', 1),
        ('assign_id', 1),
        ('translator_id', []),
        ('created_at', now_timestamp),
        ('autofill', False),
        ('task_status', 'Created'),
        ('is_send_email', False),
        ('is_locked', False),
        ('modified_at', now_timestamp),
        ('modifier_id', 1),
        ('last_built_at', 0),
        ('reference', 0),
        ('strings', {})
    )

    unique = ("target",)

    @classmethod
    def get_by_app_locale(
            cls, platform, appname, category, appversion, locale,
            id_only=False, explain_refer=False):
        """
        Get information by app locale from the database
        Parameters:
            -appname: package name,
            -appversion: package version,
            -locale: Country code,
            -id_only: Only return the value of id
            -explain_refer: explain the refer id as specific information
        Return:
            -task: the information of locale
        """
        if id_only:
            explain_refer = False
            # if only fetch id then we need not explain refer and we only need
            # id of target info
        info = LocalizationInfo.get_by_app_locale(
            platform, appname, category, appversion, locale, id_only=id_only)
        if not info:
            return
        if id_only:
            return cls.find({'target': info}, one=True, id_only=id_only)
        else:
            task = cls.find({'target': info['_id']}, one=True)
            if explain_refer and task:
                task['target'] = info
                task['reference'] = LocalizationInfo.find(
                    {'_id': task['reference']}, one=True)
            return task

    @classmethod
    def insert_task(cls, data, get=False):
        """
        insert a task in localization_task collection
        Parameters:
            -data: the information of task,
            -get: Is the data already exists,
        Return:
            -The results of the insert data
        """
        platform = data['platform']
        appname = data['appname']
        category = data['category']
        appversion = data['appversion']
        locale = data['locale']
        target = LocalizationInfo.get_by_app_locale(
            platform, appname, category, appversion, locale, id_only=True)
        if not target:
            _LOGGER.warning("invalid target: %s", data['locale'])
            raise exception.DataError("invalid target")
        creator_id = data.get('creator_id', 1)
        assign_id = data.get('assign_id', 1)
        if data.get("reference") is not None:
            reference = LocalizationInfo.get_by_app_locale(
                platform, appname, category, appversion,
                data['reference'], id_only=True)
            if not reference:
                _LOGGER.warning("invalid reference: %s", data['reference'])
                raise exception.DataError("invalid reference")
        else:
            reference = None
        autofill = data["autofill"] if data.get('autofill') else False
        # fulfill the actual target/reference
        task_data = {
            'target': target, 'reference': reference,
            "assign_id": assign_id, 'creator_id': creator_id,
            "autofill": autofill}

        # fulfill the strings
        finished = LocalizationStrings.find(
            {"localization_info": target, "status": _FINISHED}).count()
        historical = LocalizationStrings.find(
            {"localization_info": target,
                "status": _HISTORICAL_DOCUMENT}).count()

        strings = {'modified_at': now_timestamp(), 'modifier_id': creator_id}
        strings['total'] = LocalizationStrings.get_app_locale_count(
            platform, appname, category, appversion, '')
        strings["uncheck"] = LocalizationStrings.find(
            {"localization_info": target, "status": _TO_BE_CHECK}).count()
        strings['untranslated'] = strings["total"] - finished \
            - historical - strings["uncheck"]
        task_data['strings'] = strings

        task_data['modified_at'] = now_timestamp()
        task_data['modifier_id'] = creator_id

        if cls.find({'target': target}, one=True, id_only=True):
            raise Exception("this task has existed")
            # left to be replaced with detailed exception class
        _LOGGER.info("insert a new task: %s", data)
        _LOGGER.info("insert task info: %s", task_data)
        return ModelBase.insert.im_func(cls, task_data, get=get)

    @classmethod
    def assign_task(cls, target_cond, assign_id, role, translator_info):
        """
        assign task to translator
        Parameters:
            -data: the information of task,
        Return:
            -The results of the insert data
        """
        target = LocalizationInfo.find_id_by_unique(target_cond)
        if not target:
            _LOGGER.warning("invalid target: %s", target_cond['locale'])
            raise exception.DataError("invalid target")
        if role == _ADMIN:
            task_data = cls.find({"target": target}, {"_id": 0}, one=True)
        else:
            task_data = cls.find(
                {"target": target, "assign_id": assign_id},
                {"_id": 0}, one=True)
        if not task_data:
            _LOGGER.warning("invalid target: %s", target)
            raise exception.DataError("invalid target")
        if task_data["is_locked"]:
            return False
        task_data["translator_id"] = translator_info
        task_data["task_status"] = "Translating"
        cls.update({"target": target}, task_data)
        return True

    @classmethod
    def lock_task(cls, data):
        """
        locak task
        Parameters:
            -data: the information of task,
        Return:
        """
        target_cond = data
        operation = data.get("operation")

        target_cond.pop("operation")

        info_id = LocalizationInfo.find_id_by_unique(target_cond)
        if not info_id:
            _LOGGER.warning("invalid info: %s", data['locale'])
            raise exception.DataError("invalid info")
        task_data = cls.find({"target": info_id}, {"_id": 0}, one=True)
        if not task_data:
            _LOGGER.warning("invalid target: %s", info_id)
            raise exception.DataError("invalid target")
        if operation == "lock":
            task_data["is_locked"] = True
        else:
            task_data["is_locked"] = False
        cls.update({"target": info_id}, task_data)

    @classmethod
    def check_task_by_cpm(cls, target_cond, cpm_id, role):
        """
        assign task to translator
        Parameters:
            -data: the information of task,
        Return:
            -The results of the insert data
        """
        target = LocalizationInfo.find_id_by_unique(target_cond)
        if not target:
            _LOGGER.warning("invalid target: %s", target_cond['locale'])
            raise exception.DataError("invalid target")
        if role == _ADMIN:
            task_data = cls.find({"target": target}, {"_id": 0}, one=True)
        elif role == _COUNTRY_PM:
            task_data = cls.find(
                {"target": target, "creator_id": cpm_id},
                {"_id": 0}, one=True)
        else:
            return
        if not task_data:
            _LOGGER.warning("invalid target: %s", target)
            raise exception.DataError("invalid target")
        if task_data["task_status"] == "To be check" and \
                task_data["strings"]["uncheck"] != 0:
            return False
        if task_data["strings"]["untranslated"]:
            task_data["task_status"] = "Translating"
        else:
            task_data["task_status"] = _FINISHED
            task_data["is_locked"] = True
        cls.update({"target": target}, task_data)
        return task_data

    @classmethod
    def update_finish_count(cls, target, modifier_id=1):
        """
        update the number of target's finished count
        in localization_task collection
        Parameters:
            -target: the target task of needed to update,
            -finished: Whether translated: 1 or 0 or -1,
            -inc: whether the number of finished count to add and subtract one,
            -modifier_id: the id of modifier,
        Return:
            -The results of the update data
        """
        cond = {'target': target}
        task = cls.find(cond, one=True)
        if task is None:
            return
        strings = {}
        strings["total"] = task["strings"]["total"]
        strings['untranslated'] = LocalizationStrings.find(
            {"localization_info": target, "status": _UNTRANSLATED}).count()
        strings['uncheck'] = 0
        if task["task_status"] == "To be check":
            strings['uncheck'] = LocalizationStrings.find(
                {"localization_info": target, "status": _TO_BE_CHECK}).count()
        strings["modified_at"] = now_timestamp()
        strings["modifier_id"] = modifier_id
        count = LocalizationStrings.find({"localization_info": target}).count()
        strings['untranslated'] += strings["total"] - count
        task["strings"] = strings
        task['modified_at'] = now_timestamp()
        task['modifier_id'] = modifier_id
        if task["task_status"] == _FINISHED:
            task["task_status"] = "Translating"
            task["is_send_email"] = False
        _LOGGER.info(
            "update finish count of task: %s ", task)
        cls.update(cond, task)

    @classmethod
    def update_old_data_count(cls, target):
        """
        update the number of target's finished count
        in localization_task collection
        Parameters:
            -target: the target task of needed to update,
            -finished: Whether translated: 1 or 0 or -1,
            -inc: whether the number of finished count to add and subtract one,
            -modifier_id: the id of modifier,
        Return:
            -The results of the update data
        """
        cond = {'target': target}
        task = cls.find(cond, one=True)
        if task is None:
            return
        if task["strings"].get("status") is None:
            return
        if task["strings"]["status"] == "finished":
            task["task_status"] = "Finished"
        elif task["strings"]["status"] == "not_validated":
            task["task_status"] = "To be check"
        else:
            task["task_status"] = "Translating"
        strings = {}
        strings['untranslated'] = LocalizationStrings.find(
            {"localization_info": target, "status": _UNTRANSLATED}).count()
        strings['uncheck'] = 0
        if task["task_status"] == "To be check":
            strings['uncheck'] = LocalizationStrings.find(
                {"localization_info": target, "status": _TO_BE_CHECK}).count()
        strings["modified_at"] = task["strings"]["modified_at"]
        if task["strings"].get("modified_id") is None:
            strings["modified_id"] = task["creator_id"]
        else:
            strings["modified_id"] = task["strings"]["modified_id"]
        strings["total"] = task["strings"]["total"]
        count = LocalizationStrings.find({"localization_info": target}).count()
        strings['untranslated'] += strings["total"] - count
        task["strings"] = strings
        task["assign_id"] = task["creator_id"]
        task["translator_id"] = []
        task["translator_id"].append(task["creator_id"])
        task['autofill'] = True if task.get("reference") else False
        if task["task_status"] == "Finished" or \
                task["task_status"] == "To be check":
            task['is_send_email'] = True
        else:
            task['is_send_email'] = False
        task["is_locked"] = True if task["task_status"] == "Finished" \
            else False

        _LOGGER.info(
            "update finish count of task: %s ", task)
        cls.update(cond, task)

    @classmethod
    def get_all_task(
            cls, platform, category, appname, appversion, uid=None, role=2,
            status='', explain_refer=True, sort=None):
        """
        information for all of the            task
        Parameters:
            -platform: the platform of package,
            -appname: package name,
            -category: the category of package,
            -appversion: package version,
            -status: the status of task,
            -explain_refer: explain the refer id as specific information
            -sort: According to the creating time sorting,
        Return:
            -ret_tasks: The array of information for all of the task
        """
        info_ids = LocalizationInfo.get_id_by_app(
            platform, appname, category, appversion)
        cond = {}
        cond['target'] = {'$in': info_ids}

        if role == _TRANSLATOR:
            cond["translator_id"] = uid
        elif role == _CHARGE:
            cond["assign_id"] = uid
        elif role == _COUNTRY_PM:
            cond["creator_id"] = uid

        if status == "Translating":
            cond["task_status"] = {'$in': ["Created", "Translating"]}
        elif status == "To be check" or status == "Finished":
            cond["task_status"] = status

        ret_tasks = []
        tasks = cls.find(cond)
        if sort is not None:
            tasks = tasks.sort(sort)
        for item_t in tasks:
            target_id = item_t.get('target')
            reference_id = item_t.get('reference')
            if explain_refer:
                item_t['target'] = LocalizationInfo.find(
                    {'_id': target_id}, one=True)
                if reference_id is not None:
                    item_t['reference'] = LocalizationInfo.find(
                        {'_id': reference_id}, one=True)
            if not item_t['target']:
                _LOGGER.warning(
                    "found invalid localization_info with target %s",
                    target_id)
                continue
            ret_tasks.append(item_t)
        return ret_tasks

    @classmethod
    def get_app_task(cls, appname, appversion=None, cond={}):
        """
        information for all of the task
        Parameters:
            -appname: package name,
            -appversion: package version,
            -cond: query conditions,
        Return:
            -The array of information for all of the task
        """
        info_cond = {'appname': appname}
        if appversion is not None:
            info_cond['appversion'] = appversion
        info_ids = LocalizationInfo.find(info_cond, id_only=True)
        cond['target'] = {'$in': info_ids}
        return cls.get_all_task(appname, appversion)

    @classmethod
    def get_candidate_locales(
            cls, platform, category, appname, appversion,
            countrys, locale_only=False):
        """
        return the list of locales which have not been added to tasks
        Parameters:
            -appname: package name,
            -appversion: package version,
            -locale_only: Only return the value of locale
        Return:
            -The array of information for candidate of the task:
            [
                {
                    'lcoale': 'br',
                    'language': 'Portuguese',
                    'country': 'Brail'
                }
            ]
        """
        ret = []
        cur_locales = cls.get_in_task_locales(
            platform, category, appname, appversion, locale_only=True)
        locales = LocalizationConfig.get_app_locales(
            appname, appversion, countrys, locale_only=locale_only)
        for item_l in locales:
            temp_l = item_l['locale']
            if item_l if locale_only else temp_l not in cur_locales and temp_l:
                # the default locale "" should be not candidate
                ret.append(item_l)
        return ret
        # recommend locale is to be implemented

    @classmethod
    def get_in_task_locales(
            cls, platform, category, appname, appversion,
            status=None, cond={}, locale_only=False):
        """
        can receive cond such as strings.status to filter locales of specified
        tasks
        Parameters:
            -appname: package name,
            -appversion: package version,
            -status: the status of task,
            -cond: query conditions,
            -locale_only: Only return the value of locale
        Return:
            -The array of locale information of the task:
        """
        info_ids = LocalizationInfo.get_id_by_app(
            platform, appname, category, appversion)
        cond = {}
        cond['target'] = {'$in': info_ids}
        if status is not None:
            cond["strings.status"] = status
        cur_targets = [t['target'] for t in cls.get_all_task(
            platform, category, appname, appversion, status=status)]
        cur_locales = [t['locale'] for t in cur_targets]
        if locale_only:
            return cur_locales
        else:
            return LocalizationConfig.get_locale_info(
                appname, appversion, cur_locales)

    @classmethod
    def export_strings(cls, appname, appversion, locale=None):
        """
        According to the specified locale exported XML file
        Parameters:
            -appname: package name,
            -appversion: package version,
            -locale: Country code
        Return:
            -None
        """
        if locale:
            if type(locale) not in (list, tuple):
                locale = [locale]
        else:
            locale = LocalizationConfig.get_app_locales(
                appname, appversion, locale_only=True)
        path = os.path.join(
            STATIC_ROOT, appname, appversion, 'apk_data', 'res')
        for item_l in locale:
            if item_l == '':
                continue
            l_path = os.path.join(path, "values-%s" % item_l)
            for fpath in glob.glob(os.path.join(l_path, '*')):
                os.remove(fpath)
            # to keep files clean ...
            organized_strings = cls.organize_strings(
                appname, appversion, item_l)
            for k, v in organized_strings:
                ET.ElementTree(v).write(
                    os.path.join(l_path, "%s.xml" % k), encoding='utf-8',
                    xml_declaration=True)

    @classmethod
    def update_string_to_ele(cls, string, ele, locale=None):
        """
        Update the corresponding value of string in the XML file
        Parameters:
            -string: the information of string,
            -ele: element in xml file,
            -locale: Country code
        Return:
            -new_ele: updated element
        """

        def rebuild_ele(ele, content):
            """
            combine content with tag_name like this:
                <tag_name>content</tag_name>
            Parameters:
                -ele: element in xml file,
                -content: the content of tag element
            Return:
                -new_ele: updated element
            """
            tag_name = ele.tag
            content = "<%s>%s</%s>" % (tag_name, content, tag_name)

            content = LocalizationStrings.adjust_alias(content)
            new_ele = ET.fromstring(content)
            new_ele.attrib = ele.attrib
            new_ele.tail = ele.tail
            return new_ele

        tag_name = ele.tag
        alias = string['alias']
        is_list = tag_name.endswith('-array') or tag_name == 'plurals'
        if is_list:
            content = ele.text
        else:
            content = alias
        new_ele = rebuild_ele(ele, content)
        if is_list:
            if type(alias) is not list or len(alias) != len(ele):
                _LOGGER.error(
                    "alias %s is not list or length does not match %s, "
                    "and the ele is %s and locale is %s",
                    alias, len(ele), ET.tostring(ele), locale)
                raise exception.DataError("alias is not list or len not match")
            for i, ele_i in enumerate(ele.getchildren()):
                content = alias[i]
                if type(content) is dict:
                    content = content.get('content', '')
                new_ele.append(rebuild_ele(ele_i, content))
        return new_ele

    @classmethod
    def find_ele_in_root(cls, root, tag_name, name):
        """
        find element in the XML file
        Parameters:
            -root: the root element of the parsed tree,
            -ele: element tag,
            -name: the name of element tag
        Return:
            -i: The position of the element in parsed tree
        """
        for i, ele in enumerate(root.getchildren()):
            if ele.tag == tag_name and ele.attrib.get('name') == name:
                return i, ele
        else:
            return -1, None

    @classmethod
    def organize_strings(
            cls, platform, appname, category, appversion, locale, md5,
            missing_only=True, strings=None, inc_only=False):
        """
        organize strings to element
        Parameters:
            -appname: package name,
            -appversion: package version,
            -locale: Country code
            -md5: The MD5 value of the XML file,
            -missing_only: Full XML file or only MISS XML file,
            -strings: The information of strings
            -inc_only: If there is a new element
        Return:
            -ret:
        """
        ret = {}
        temp_ret = {}

        if strings is None:
            info_id = LocalizationInfo.get_by_app_locale(
                platform, appname, category, appversion, locale, id_only=True)
            if not info_id:
                _LOGGER.warning(
                    "can not find relevant info for appname: %s; appversion: "
                    "%s and locale: %s", appname, appversion, locale)
                return ret
            strings = LocalizationStrings.find(
                {'localization_info': info_id}, toarray=True)

        for string in strings:
            cur_key = string['xml_file']
            # raw strings --- aggregate according to exact xml file
            if cur_key in temp_ret:
                temp_ret[cur_key].append(string)
            else:
                temp_ret[cur_key] = [string]
            # as we will use source xml file for example, we generate xml
            # elements together to avoid frequent xml file load

        for k, v in temp_ret.iteritems():
            cur_names = [s['name'] for s in v]
            if missing_only:
                if md5:
                    the_xml_dir = "miss_xml_%s" % md5
                else:
                    the_xml_dir = "miss_xml_data"
                middle_dir = "res-missing"
            else:
                if md5:
                    the_xml_dir = "xml_%s" % md5
                else:
                    the_xml_dir = "xml_data"
                middle_dir = "res"

            values_dir = 'values' if locale == '' else "values-%s" % locale
            if missing_only:
                k = k.split(".")[0]
                k = "%s_missing.xml" % k
            xml_file_path = os.path.join(
                STATIC_ROOT, appname, appversion, the_xml_dir,
                middle_dir, values_dir, k)
            _LOGGER.info(
                "begin to process: %s, %s, %s, %s. xml_file_path is %s",
                appname, appversion, locale, k, xml_file_path)
            if not os.path.exists(xml_file_path):
                _LOGGER.warning(
                    "cann't find xml file %s for appname %s appversion %s "
                    "locale %s, continue ...", xml_file_path, appname,
                    appversion, locale)
                continue
            tree = ET.parse(xml_file_path, parser=CommentedTreeBuilder())
            root = tree.getroot()
            if inc_only:
                eles_to_delete = []
                _LOGGER.info(
                    "before remove: %s children in orig_root" %
                    len(root.getchildren()))
                for child in root.getchildren():
                    if child.attrib['name'] not in cur_names:
                        eles_to_delete.append(child)
                for ele in eles_to_delete:
                    root.remove(ele)
                _LOGGER.info(
                    "after remove according to cur_names: %s children in "
                    "orig_root" % len(root.getchildren()))
                # like list, you'd better do not remove its element while
                # itering it

            for string in v:
                cur_tagname = string['tag_name']
                cur_name = string['name']
                ele_index, ele = cls.find_ele_in_root(
                    root, cur_tagname, cur_name)
                if ele is None:
                    continue
                else:
                    new_ele = cls.update_string_to_ele(string, ele, locale)
                    if ele is None:
                        root.append(new_ele)
                    else:
                        root[ele_index] = new_ele

            ret[k] = tree
        return ret

    @classmethod
    def check_string_in_ele(cls, string, ele, locale=None):
        """
        Update the corresponding value of string in the XML file
        Parameters:
            -string: the information of string,
            -ele: element in xml file,
            -locale: Country code
        Return:
            -new_ele: updated element
        """

        tag_name = ele.tag
        alias = string['alias']
        if tag_name == 'string-array':
            item_list = []
            for sub_ele in ele:
                match_group = array_tag_compile.match(
                    ET.tostring(sub_ele, encoding='utf-8'))
                if not match_group:
                    match_blank = array_tag_blank_compile.match(
                        ET.tostring(sub_ele, encoding='utf-8'))
                    if not match_blank:
                        _LOGGER.warn(
                            'string-array item not match regex![%s]' %
                            ET.tostring(sub_ele, encoding='utf-8'))
                        continue
                    else:
                        item_list.append('')
                else:
                    item_list.append(match_group.group(1))
            temp_alias = []
            for alias_item in alias:
                if type(alias_item) is unicode:
                    alias_item = alias_item.encode('utf-8')
                    temp_alias.append(alias_item)
            alias = temp_alias

            if item_list == alias:
                return True
            else:
                return False
        else:
            match_group = string_tag_compile.match(
                ET.tostring(ele, encoding='utf-8'))
            if not match_group:
                _LOGGER.warn(
                    'string tag not match regex![%s]' %
                    ET.tostring(ele, encoding='utf-8'))
            content = match_group.group(2)
            if type(alias) is unicode:
                alias = alias.encode('utf-8')
            if content == alias:
                return True
            else:
                return False

    @classmethod
    def update_diff_strings(
            cls, platform, appname, category, appversion, locale, md5):
        """
        update diff strings status
        Parameters:
            -platform: the platform of package,
            -appname: package name,
            -category: the category of package,
            -appversion: package version,
            -locale: Country code
            -md5: The MD5 value of the XML file,
        Return:
            -None
        """
        temp_ret = {}
        info_id = LocalizationInfo.get_by_app_locale(
            platform, appname, category, appversion, locale, id_only=True)
        if not info_id:
            _LOGGER.warning(
                "can not find relevant info for appname: %s; appversion: "
                "%s and locale: %s", appname, appversion, locale)
            return None
        strings = LocalizationStrings.find(
            {'localization_info': info_id}, toarray=True)

        for string in strings:
            cur_key = string['xml_file']
            # raw strings --- aggregate according to exact xml file
            if cur_key in temp_ret:
                temp_ret[cur_key].append(string)
            else:
                temp_ret[cur_key] = [string]
            # as we will use source xml file for example, we generate xml
            # elements together to avoid frequent xml file load

        for k, v in temp_ret.iteritems():
            if md5:
                the_xml_dir = "xml_%s" % md5
            else:
                the_xml_dir = "xml_data"
            middle_dir = "res"

            values_dir = 'values' if locale == '' else "values-%s" % locale
            xml_file_path = os.path.join(
                STATIC_ROOT, appname, appversion, the_xml_dir,
                middle_dir, values_dir, k)
            _LOGGER.info(
                "begin to process: %s, %s, %s, %s. xml_file_path is %s",
                appname, appversion, locale, k, xml_file_path)
            if not os.path.exists(xml_file_path):
                _LOGGER.warning(
                    "cann't find xml file %s for appname %s appversion %s "
                    "locale %s, continue ...", xml_file_path, appname,
                    appversion, locale)
                continue
            tree = ET.parse(xml_file_path, parser=CommentedTreeBuilder())
            root = tree.getroot()

            for string in v:
                cur_tagname = string['tag_name']
                cur_name = string['name']
                ele_index, ele = cls.find_ele_in_root(
                    root, cur_tagname, cur_name)
                if ele is None:
                    continue
                else:
                    string_flag = cls.check_string_in_ele(string, ele, locale)
                    if string_flag:
                        string_status = {"update": False}
                    else:
                        string_status = {"update": True}
                    update_cond = {
                        "localization_info": info_id,
                        "name": cur_name}
                    LocalizationStrings.update(update_cond, string_status)

    @classmethod
    def generate_diff_strings(
            cls, platform, appname, category, appversion, locale, md5):
        ret = {}
        temp_ret = {}
        info_id = LocalizationInfo.get_by_app_locale(
            platform, appname, category, appversion, locale, id_only=True)
        if not info_id:
            _LOGGER.warning(
                "can not find relevant info for appname: %s; appversion: "
                "%s and locale: %s", appname, appversion, locale)
            return None
        strings = LocalizationStrings.find(
            {'localization_info': info_id, "update": True}, toarray=True)
        for string in strings:
            cur_key = string['xml_file']
            # raw strings --- aggregate according to exact xml file
            if cur_key in temp_ret:
                temp_ret[cur_key].append(string)
            else:
                temp_ret[cur_key] = [string]
            # as we will use source xml file for example, we generate xml
            # elements together to avoid frequent xml file load

        for k, v in temp_ret.iteritems():
            cur_names = [s['name'] for s in v]
            if md5:
                the_xml_dir = "xml_%s" % md5
            else:
                the_xml_dir = "xml_data"
            middle_dir = "res"

            values_dir = 'values' if locale == '' else "values-%s" % locale
            xml_file_path = os.path.join(
                STATIC_ROOT, appname, appversion, the_xml_dir,
                middle_dir, values_dir, k)
            _LOGGER.info(
                "begin to process: %s, %s, %s, %s. xml_file_path is %s",
                appname, appversion, locale, k, xml_file_path)
            if not os.path.exists(xml_file_path):
                _LOGGER.warning(
                    "cann't find xml file %s for appname %s appversion %s "
                    "locale %s, continue ...", xml_file_path, appname,
                    appversion, locale)
                continue
            tree = ET.parse(xml_file_path, parser=CommentedTreeBuilder())
            root = tree.getroot()
            eles_to_delete = []
            _LOGGER.info(
                "before remove: %s children in orig_root" %
                len(root.getchildren()))
            for child in root.getchildren():
                name = child.attrib.get("name")
                if name:
                    if child.attrib['name'] not in cur_names:
                        eles_to_delete.append(child)
            for ele in eles_to_delete:
                root.remove(ele)
            _LOGGER.info(
                "after remove according to cur_names: %s children in "
                "orig_root" % len(root.getchildren()))
            # like list, you'd better do not remove its element while
            # itering it

            for string in v:
                cur_tagname = string['tag_name']
                cur_name = string['name']
                ele_index, ele = cls.find_ele_in_root(
                    root, cur_tagname, cur_name)
                if ele is None:
                    continue
                else:
                    new_ele = cls.update_string_to_ele(string, ele, locale)
                    if ele is None:
                        root.append(new_ele)
                    else:
                        root[ele_index] = new_ele

            ret[k] = tree
        return ret

    @classmethod
    def to_snapshot(cls, platform, appname, category, appversion, locale=None):
        ret = []
        if locale is None:
            locale = LocalizationConfig.get_app_locales(
                appname, appversion, locale_only=True)
        elif type(locale) not in (list, tuple):
            locale = [locale]
        for l in locale:
            item = {}
            task = cls.get_by_app_locale(
                platform, appname, category, appversion, l, explain_refer=True)
            item['task'] = task
            info = LocalizationInfo.get_by_app_locale(
                platform, appname, category, appversion, l)
            item['locale'] = l
            item['info'] = info
            strings = {}
            item['strings'] = strings
            if info:
                strings['items'] = LocalizationStrings.find(
                    {'localization_info': info['_id']}, toarray=True)
            else:
                strings['items'] = {}
            ret.append(item)
        return ret

    @classmethod
    def refresh_task(cls, platform, appname, category, appversion, locale):
        finished = LocalizationStrings.get_app_locale_count(
            platform, appname, category, appversion,
            locale, cond={'status': _FINISHED})
        uncheck = LocalizationStrings.get_app_locale_count(
            platform, appname, category, appversion,
            locale, cond={'status': _TO_BE_CHECK})
        historical = LocalizationStrings.get_app_locale_count(
            platform, appname, category, appversion,
            locale, cond={'status': _HISTORICAL_DOCUMENT})
        cur_task_id = cls.get_by_app_locale(
            platform, appname, category, appversion, locale, id_only=True)
        if not cur_task_id:
            _LOGGER.warning(
                "can not find task for appname: %s, appversion: %s and "
                "locale: %s", appname, appversion, locale)
            return
        origin_task = cls.get_by_app_locale(
            platform, appname, category, appversion, '')
        if not origin_task:
            _LOGGER.error(
                "origin task for appname: %s, appversion: %s, locale: %s "
                "not found", appname, appversion, locale)
            raise exception.DataError("origin task not found")

        total = origin_task['strings']['total']
        update_content = {'strings.total': total}
        update_content['strings.untranslated'] = total - \
            finished - uncheck - historical
        update_content['strings.uncheck'] = uncheck
        cls.update({'_id': cur_task_id}, update_content)

    @classmethod
    def clear_task_strings(
            cls, platform, appname, category, appversion, locale):
        """
        Remove strings information from localization_strings
        by appname & appversion& locale
        and update task info
        Parameters:
            -appname: package name,
            -appversion: package version,
            -locale: Country code,
        Return:
            -task: the information of locale
        """
        info_id = LocalizationInfo.get_by_app_locale(
            platform, appname, category, appversion, locale, id_only=True)
        if not info_id:
            return
        """
        else:
            LocalizationStrings.remove({'localization_info': info_id})
        """
        update_content = {'finished': 0}
        if locale == '':
            update_content['total'] = 0
        cls.update({'target': info_id}, update_content)

    @classmethod
    def check_task(
            cls, appname, appversion=None, locale=None, raise_exception=True):
        cond = {'appname': appname}
        if appversion is not None:
            cond['appversion'] = appversion
        if locale is not None:
            cond['locale'] = locale
        info_ids = LocalizationInfo.find(cond, id_only=True)
        task = cls.find({'target': {'$in': info_ids}}, one=True)
        if not task:
            if raise_exception:
                raise exception.DataError("can not find task for cur cond")
            else:
                return False
        if raise_exception:
            return task
        else:
            return True


class LocalizationModules(ModelBase):

    """
    examples:
        {
            "localization_info": 123123,
            "modules": [
                {
                    "name": "xxx",
                    "modules": []
                },
                {
                    "name": "xxx",
                    "modules": [
                        {
                            "name": "xxx",
                            "modules": []
                        }
                     ]
                 },
            ]
        }
    """

    db = 'i18n'
    collection = "localization_modules"

    required = ('localization_info',)
    optional = (('modules', {}),)

    unique = ('localization_info',)

    @classmethod
    def get_by_app(cls, appname, appversion):
        local_info = LocalizationInfo.find_id_by_unique({
            'appname': appname, 'appversion': appversion, 'locale': ''})
        return cls.find(
            {"localization_info": local_info},
            fields={'_id': 0, 'localization_info': 0}, one=True)


class LocalizationSnap(ModelBase):

    """
    examples:
        {
            "created_at": 1404460540,
            "creator_id": 1,
            "appname": "dolphinopbrowser",
            "appversion": "11.1.1",
            "comment": "for test",
            'status': 'finished',
            'tag': 'v11.2.4',
            'task': ObjectId('53d771d9bc3dcaf6979f2890'),
            "items": [
                // 每个item表示一个本地化任务的当前信息，
                // 比如翻译、默认数据等等...
                {
                    "task": {
                        "appname": "dolphinopbrowser",
                        "appversion": "11.1.1",
                        "locale": "ar",
                        "is_origin": false,
                        "referto": "pt",
                        "creator_id": 1,
                        "created_at": 1404460438,
                        "modified_at": 1404460538,
                        "last_built_at": 1404460540,
                    },
                    "info": {},
                     "strings": [
                        {
                            "module_path": ["a", "b", "c"],
                            "localization_info": "xxx",
                            "name": "add.xml",
                            "tag_name": "file",
                            "finished": false,
                            "alias": null,
                        },
                        {
                            "module_path": ["a", "b"],
                            "localization_info": "xxx",
                            "name": "add.xml",
                            "tag_name": "file",
                            "finished": false,
                            "alias": [null, "test"]
                        },
                    ]
                }
            ]
        }
    """

    db = 'i18n'
    collection = 'localization_snap'

    required = ('appname', 'appversion')
    optional = (
        ('created_at', now_timestamp),
        ('creator_id', 1),
        ('tag', ""),
        ('comments', ""),
        ('items', []),
        ('task', ''),
        ('reason', ''),
        ('log_url', ''),
        ('lint_url', ''),
        ('apk_url', ''),
        ('qrcode_url', ''),
        ('status', 'new')
    )

    @classmethod
    def create_snap(
            cls, platform, appname, category, appversion, tag, locale=None,
            creator_id=1, comments="", with_items=True):
        LocalizationInfo.check_info(platform, appname, category, appversion)
        new_snap = {
            'appname': appname, 'appversion': appversion, "tag": tag,
            'creator_id': creator_id, 'comments': comments}
        if locale is not None:
            new_snap['task'] = LocalizationTask.check_task(
                appname, appversion, locale)['_id']
        if with_items:
            new_snap['items'] = LocalizationTask.to_snapshot(
                platform, appname, category, appversion)
        return cls.insert(new_snap, check_unique=False)
        # return generated _id

    @classmethod
    def fulfill_snap(cls, platform, category, snap_id):
        new_snap = cls.find({'_id': snap_id}, one=True)
        if not new_snap:
            raise exception.DataError(
                "can not find the snap with id %s", snap_id)
        new_snap['items'] = LocalizationTask.to_snapshot(
            platform, new_snap['appname'], category, new_snap['appversion'])
        return cls.update({'_id': snap_id}, new_snap)

    @classmethod
    def get_snap(cls, appname, appversion, uid=1):
        cond = {
            "appname": appname, "appversion": appversion,
            "creator_id": uid, "status": "building"}
        finished_totle = cls.find(cond).count()
        if finished_totle > 0:
            return False
        else:
            return True

    @classmethod
    def submit_project(
            cls, appname, appversion, tag, locale=None, platform="Android",
            category="Trunk", creator_id=1, comment="", missing_only=True):
        count = 1
        while count < 6:
            if cls.find({
                'appname': appname, 'appversion': appversion, 'status': 'new'},
                    {'_id': 1}, one=True):
                _LOGGER.warning(
                    "there's another task existed for appname: %s, "
                    "appversion: %s and locale: %s, the %s try",
                    appname, appversion, locale, count)
                time.sleep(2)
                count += 1
            else:
                break
        else:
            raise exception.UniqueCheckError(
                "there exists another new snap task")
        new_snap_id = cls.create_snap(
            platform, appname, category, appversion, tag, locale,
            creator_id, comment, with_items=False)
        try:
            if not new_snap_id:
                raise exception.UnknownError("snap creation failure")
            cls.fulfill_snap(platform, category, new_snap_id)
            xmlfile = LocalizationApps.generate_xml_file(
                platform, appname, category, appversion, locale='all',
                md5=None, missing_only=missing_only)
            upload_data = get_api.upload_xml_file(
                appname, appversion, new_snap_id, xmlfile, tag)
            if upload_data:
                cls.update({'_id': new_snap_id}, {'status': 'waiting'})
                return True
            else:
                return False
        except Exception as e:
            cls.remove({'_id': new_snap_id})
            raise e

    @classmethod
    def update_status(
            cls, snap_id, status, apk_url, reason, log_url, lint_url, items):
        '''
        update the status of snaps with current status 'building'
        notice that if you want to call the method from view you should know
        that it may cost pretty much time
        '''
        snap_simple = cls.find({'_id': snap_id}, {'items': 0}, one=True)
        if not snap_simple:
            return
        snap_status = snap_simple['status']
        if snap_status == "cancel":
            return
        appname = snap_simple['appname']
        appversion = snap_simple['appversion']
        if status == 1:
            snap_status = "building"
            update_data = {"status": snap_status}
            cls.update({'_id': snap_id}, update_data)
        if status == 2:
            snap_status = "finished"
            if apk_url:
                qrcode_url = cls.writeback_apk(
                    appname, appversion, snap_id, apk_url)
                update_data = {
                    "status": snap_status, "apk_url": apk_url,
                    "qrcode_url": qrcode_url}
            else:
                update_data = {
                    "status": snap_status, "reason": reason,
                    "log_url": log_url, "lint_url": lint_url}
            print "123update data"
            print update_data
            print "123update data"
            cls.update({'_id': snap_id}, update_data)
        elif status == 3:
            snap_status = "timeout"
            update_data = {"status": snap_status}
            cls.update({'_id': snap_id}, update_data)
        if items:
            LocalizationErrorlog.store_error_message(snap_id, items)
        else:
            return None

    @classmethod
    def get_snap_info(cls, uid=1):
        cond = {"creator_id": uid}
        fields = {"items": 0, "comments": 0, "task": 0}
        snap_info = cls.find(cond, fields).sort('created_at', -1).limit(15)
        snap_info = list(snap_info)
        for snap_item in snap_info:
            if snap_item.get("status") == "finished":
                if snap_item.get("apk_url"):
                    snap_item["status"] = "finished"
                else:
                    snap_item["status"] = "failed"
            snap_item["time"] = time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(
                    snap_item.get('created_at')))
            if snap_item.get("lint_url") is None:
                snap_item["lint_message"] = False
            else:
                snap_item["lint_message"] = True if snap_item["lint_url"] \
                    else False
            snap_item["id"] = str(snap_item["_id"])
            snap_item.pop("created_at")
            snap_item.pop("_id")
            if snap_item.get("log_url") is not None:
                snap_item.pop("log_url")
            if snap_item.get("lint_url") is not None:
                snap_item.pop("lint_url")
        return snap_info

    @classmethod
    def writeback_apk(cls, appname, appversion, snap_id, apk_file):
        app_dir = os.path.join(STATIC_ROOT, appname, appversion)
        qrcode_image_file_name = 'qrcode_pic_%s.jpg' % snap_id
        qrcode_image_file_path = os.path.join(app_dir, qrcode_image_file_name)
        try:
            full_qrcode_img_url = \
                "http://%s/admin/download?type=qrcode&file=%s&appname=%s"\
                "&appversion=%s" % (
                    HOST, qrcode_image_file_name, appname, appversion)
            make_qr(apk_file, qrcode_image_file_path)
            return full_qrcode_img_url
        except Exception as e:
            if os.path.exists(qrcode_image_file_path):
                os.remove(qrcode_image_file_path)
            _LOGGER.exception(e)
            return False
        else:
            return True


class LocalizationConfig(ModelBase):

    """
    examples:
        {
            "type": "available_locales",
            "items": [
                {
                    "appname": "xxx",
                    "appversion": "xxx",
                    "locales": [
                        {
                            "locale": "br",
                            "language": "Portuguese",
                            "country": "Brazil",
                        },
                    ]
                },
            ]
        }
    """

    db = 'i18n'
    collection = 'localization_config'

    unique = ('type',)

    @classmethod
    def get_app_locales(
            cls, appname="", appversion="", country=[], locale_only=False):
        # "" allows a common locales-config used widely
        locales = []
        country = list(country)
        temp_locales = cls.find(
            {'type': "available_locales"}, one=True)['items']
        for item in temp_locales:
            if item['appname'] == "" and item['appversion'] == "":
                # left to ...
                temp_locales = item['locales']
                break
        else:
            _LOGGER.warning(
                "can not find the locales of appname %s and appversion %s",
                appname, appversion)
            return
        if not country:
            locales = temp_locales
        else:
            for i in temp_locales:
                if i["country"] in country:
                    locales.append(i)
        if locale_only:
            return [l['locale'] for l in locales]
        else:
            return locales

    @classmethod
    def get_locale_info(cls, appname, appversion, locale):
        locales = cls.get_app_locales(appname, appversion)
        is_list = type(locale) in (list, tuple)
        if is_list:
            ret = []
        for l in locales:
            ll = l['locale']
            if ll in locale if is_list else ll == locale:
                if is_list:
                    ret.append(l)
                else:
                    return l
        return ret


class ReportConfig(ModelBase):

    """
    examples:
        {
            "type": "locale_dict",
            "first":
                {
                    "ru_RU": "Russia",
                    "pt_BR": "Brazil"
                },
            "second":
                {
                    "xxxx": "xxxx"
                },
        }
    """

    db = 'i18n'
    collection = 'report_config'

    unique = ('type',)

    @classmethod
    def get_classify_locales(cls, classify="first"):
        classify_locales = cls.find(
            {"type": "locale_dict1"}, {classify: 1, "_id": 0}, toarray=True)
        return classify_locales[0][classify]

    @classmethod
    def get_needed_locales(cls):
        first = cls.get_classify_locales("first")
        second = cls.get_classify_locales("second")
        return first.keys() + second.keys()


class LocalizationApps(ModelBase):
    """
    examples:
        {
            'appname': 'xxx',
            'appversion': 'yyy',
            'created_at': 'zzz',
            'tag': ["v11.2.3_beta","v11.2.3 ","v11.2.3_release"],
            'xml_files': [
                {
                    'md5': 'xxx',
                    'url': 'yyy',
                    'created_at': 'zzz'
                    # 'is_active': true,
                },
                {
                    'md5': 'xxx',
                    'url': 'yyy',
                    'created_at': 'zzz'
                }
            ]
        }
    """

    db = 'i18n'
    collection = 'localization_apps'

    required = ('appname', 'appversion')
    optional = (
        ('created_at', now_timestamp),
        ('tag', []),
        ('xml_files', [])
        # status can be new, ongoing and finished
    )

    @classmethod
    def get_by_app(cls, appname, appversion=None, id_only=False):
        cond = {'appname': appname}
        if appversion is None:
            apps = cls.find(cond, id_only=id_only).sort('created_at', -1)
            if apps:
                return apps[0]
            else:
                return None
        else:
            cond['appversion'] = appversion
            return cls.find(cond, id_only=id_only, one=True)

    @classmethod
    def get_by_app_version(cls, appname):
        cond = {'appname': appname}
        find_list = cls.find(cond).sort('appversion', -1)
        ret = {}
        appversion = []
        for i in find_list:
            appversion.append(i["appversion"])
        ret["appname"] = appname
        ret["appversion"] = appversion
        return ret

    @classmethod
    def get_tag_by_app(cls, appname, appversion):
        cond = {'appname': appname, "appversion": appversion}
        fields = {"tag": 1, "_id": 0}
        return cls.find(cond, fields, one=True)

    @classmethod
    def get_xml_file(cls, appname, appversion, md5=None):
        """
        return the xml zip file (bytes format) of specified appname and
        appversion. the md5 is optional and we'll get it from db if not
        specified
        """
        xml_info = cls.get_xml_info(appname, appversion, md5)
        if not xml_info:
            return
        url = xml_info.get("url")
        xml_file_name = "missing_xml_%s.zip" % md5
        app_dir = os.path.join(STATIC_ROOT, appname, appversion)
        if not os.path.exists(app_dir):
            subprocess.call("mkdir -p %s" % app_dir, shell=True)

        xml_file_path = os.path.join(app_dir, xml_file_name)
        if not os.path.exists(xml_file_path):
            r_xml_file = get_api.get_xml_file(
                appname, appversion, url, md5=md5)
            if r_xml_file is None:
                _LOGGER.warning(
                    "can not get xml_file from provider for appname: %s, "
                    "appversion: %s and md5: %s", appname, appversion, md5)
                return
            else:
                try:
                    with open(xml_file_path, 'wb') as f:
                        f.write(r_xml_file)
                except Exception as e:
                    _LOGGER.exception(e)
                    return
        return xml_file_path

    @classmethod
    def generate_xml_file(
            cls, platform, appname, category, appversion, locale='all',
            md5=None, missing_only=True):
        """
        generate/return the xml zip file (bytes format) according to the
        current strings in db.
        you can specified a md5 or use the latest one in db.
        generate two types of xml file: total or only the missing part
        """
        app = cls.get_by_app(appname, appversion)
        locales = []
        if not app:
            flag_app = False
        else:
            flag_app = True
        if flag_app:
            if md5 is None:
                md5 = cls.get_xml_info(appname, appversion)['md5']
        if locale == 'all':
            locales = LocalizationConfig.get_app_locales(
                appname, appversion, locale_only=True)
        else:
            locales.append(locale)
        ret_sio = StringIO()
        ret_zip = zipfile.ZipFile(ret_sio, 'w')
        if missing_only:
            if flag_app:
                the_xml_dir = "miss_xml_%s" % md5
            else:
                the_xml_dir = "miss_xml_data"
            middle_dir = "res-missing"
        else:
            if flag_app:
                the_xml_dir = "xml_%s" % md5
            else:
                the_xml_dir = "xml_data"
            middle_dir = "res"

        for l in locales:
            values_dir = 'values' if l == '' else "values-%s" % l
            xml_dir_path = os.path.join(
                STATIC_ROOT, appname, appversion, the_xml_dir,
                middle_dir, values_dir)

            l_strings = LocalizationTask.organize_strings(
                platform, appname, category, appversion, l, md5,
                missing_only=missing_only)

            if os.path.exists(xml_dir_path):
                files = os.listdir(xml_dir_path)
                for f in files:
                    if f not in l_strings:
                        sio = StringIO()
                        sio.write(
                            file(os.path.join(xml_dir_path, f)).read())
                        sio.flush()
                        ret_zip.writestr(
                            os.path.join(
                                middle_dir,
                                "values-%s" % l if l else 'values',
                                f),
                            sio.getvalue())

            for k, v in l_strings.iteritems():
                # to adapt to standard of client side
                filepath = os.path.join(
                    middle_dir, "values-%s" % l if l else 'values', k)
                sio = StringIO()
                v.write(sio, encoding='utf-8', xml_declaration=True)
                ret_zip.writestr(filepath, sio.getvalue())

        ret_zip.close()
        return ret_sio.getvalue()

    @classmethod
    def generate_xls_file(
            cls, platform, appname, category, appversion, locale='all'):
        """
        generate/return the xls file (bytes format) according to the
        current strings in db.
        """
        locales = []
        if locale == 'all':
            locales = LocalizationTask.get_in_task_locales(
                platform, category, appname, appversion)
        else:
            app_info = LocalizationConfig.get_locale_info(
                appname, appversion, locale)
            language = app_info.get("language")
            i = {"locale": locale, "language": language}
            locales.append(i)
        print "123locales"
        print locales
        strings = []
        for locale_item in locales:
            string = {}
            locale = locale_item.get("locale")
            language = locale_item.get("language")
            string["display"] = "%s(%s)" % (language, locale)
            string["items"] = LocalizationStrings.generate_edit_data(
                appname, appversion, locale, platform,
                category, store=False)[1]
            string["filename"] = "values-%s" % locale if locale else 'values'
            strings.append(string)
        filepath = os.path.join(STATIC_ROOT, appname, appversion)
        return cls.store_xml_file(strings, filepath)

    @classmethod
    def store_xml_file(cls, strings, filepath):
        file = xlwt.Workbook(encoding='utf-8')
        style = xlwt.XFStyle()
        font = xlwt.Font()
        font.name = 'Times New Roman'
        font.bold = True
        style.font = font
        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_CENTER
        style.alignment = alignment
        for string_item in strings:
            temp_strings = [
                "name", "Chinese(Simplified)", "English",
                "Translation Language:%s" % string_item["display"]]
            table = file.add_sheet(
                string_item["filename"], cell_overwrite_ok=True)
            for col_i in range(4):
                table.col(col_i).width = 15000
            for i, string in enumerate(temp_strings):
                table.write(0, i, string, style)
            string_content = string_item["items"]
            for i, string in enumerate(string_content):
                table.write(i + 1, 0, string["name"])
                table.write(i + 1, 1, string["alias"][0]["zh-rCN"])
                table.write(i + 1, 2, string["alias"][0]["en-US"])
                content = string["alias"][0]["content"] if \
                    string["alias"][0]["content"] \
                    else string["alias"][0]["reference"]
                table.write(i + 1, 3, content)
        xml_file_path = os.path.join(filepath, "xml.xls")
        file.save(xml_file_path)
        return xml_file_path

    @classmethod
    def generate_diff_xml(
            cls, platform, appname, category, appversion, locale='all',
            md5=None):
        """
        generate/return the xml zip file (bytes format) according to the
        current strings in db.
        you can specified a md5 or use the latest one in db.
        generate two types of xml file: total or only the missing part
        """
        app = cls.get_by_app(appname, appversion)
        locales = []
        if not app:
            flag_app = False
        else:
            flag_app = True
        if flag_app:
            if md5 is None:
                md5 = cls.get_xml_info(appname, appversion)['md5']
        if locale == 'all':
            locales = LocalizationTask.get_in_task_locales(
                platform, category, appname, appversion, locale_only=True)
        else:
            locales.append(locale)
        if locale == "all":
            locales.remove("")
        ret_sio = StringIO()
        ret_zip = zipfile.ZipFile(ret_sio, 'w')
        middle_dir = "res"
        for l in locales:
            LocalizationTask.update_diff_strings(
                platform, appname, category, appversion, l, md5)

        for l in locales:

            l_strings = LocalizationTask.generate_diff_strings(
                platform, appname, category, appversion, l, md5)

            for k, v in l_strings.iteritems():
                # to adapt to standard of client side
                diff_filename = "%s_diff%s" % tuple(os.path.splitext(k))
                filepath = os.path.join(
                    middle_dir, "values-%s" % l if l else 'values',
                    diff_filename)
                sio = StringIO()
                v.write(sio, encoding='utf-8', xml_declaration=True)
                ret_zip.writestr(filepath, sio.getvalue())

        ret_zip.close()
        return ret_sio.getvalue()

    @classmethod
    def get_xml_info(cls, appname, appversion, md5=None):
        app = cls.get_by_app(appname, appversion)
        if not app:
            _LOGGER.warning(
                "can not find app for appname: %s and appversion: %s",
                appname, appversion)
            return
        xml_files = app.get('xml_files')
        if md5 is None:
            if xml_files:
                xml_info = xml_files[-1]
            else:
                _LOGGER.warning("the app does not have xml_files")
                return
        else:
            if xml_files:
                for xml_item in xml_files:
                    if xml_item['md5'] == md5:
                        xml_info = xml_item
                        break
                else:
                    _LOGGER.warning(
                        "the xml info for the specified md5 %s is not found",
                        md5)
                    return
            else:
                _LOGGER.warning("the app does not have xml_files")
                return
        return xml_info

    @classmethod
    def update_apps(cls, appname=None, appversion=None):
        """
        get the app_info_list and compare with data in db and do actions
        according to the result: add a new app or update the xml of an existed
        app
        """
        info_list = get_api.get_app_info_list(appname, appversion)
        ret = {}
        if info_list:
            info_list = info_list.get("data")
            appname = info_list.get("appname")
            appversion = info_list.get("appversion")
            xml_temp = {}
            xml_temp["md5"] = info_list.get("md5code")
            xml_temp["url"] = info_list.get("xml_link")
            xml_temp["created_at"] = now_timestamp()
            xml_info = []
            xml_file = cls.get_xml_info(appname, appversion)
            if xml_file is None:
                xml_info.append(xml_temp)
                insert_data = {
                    "appname": appname,
                    "appversion": appversion,
                    "tag": ["new"],
                    "xml_files": xml_info}
                cls.insert(insert_data)
            else:
                used_md5 = xml_file.get("md5")
                xml_info.append(xml_file)
                if used_md5 != xml_temp["md5"]:
                    xml_info.append(xml_temp)
                    cond = {"appname": appname, "appversion": appversion}
                    cls.update(cond, {"xml_files": xml_info})
                else:
                    return ret
            ret["appname"] = appname
            ret["appversion"] = appversion
            ret["md5"] = info_list.get("md5code")
            ret["url"] = info_list.get("xml_link")
            return ret
        else:
            return None

    @classmethod
    def update_apptag(cls, appname=None, appversion=None):
        """
        get the app_tag_list and update the tag of an existed app
        """
        tag_list = get_api.get_app_tag_list(appname, appversion)
        if tag_list:
            tag = tag_list.get("data").get("tags")
            if appname is None:
                appname = "mobi.mgeek.TunnyBrowser"
            for item in tag.items():
                appversion = item[0]
                version_tag = item[1]
                cond = {"appname": appname, "appversion": appversion}
                if cls.find(cond, {'_id': 1}, one=True) is None:
                    continue
                cls.update(cond, {"tag": version_tag})
            return True
        else:
            return False


class MailConfig(ModelBase):
    db = 'i18n'
    collection = 'user_config'

    @classmethod
    def _get_all_data(cls):
        cond = {}
        fields = {'_id': 0, 'email': 1, 'country': 1}
        return cls.find(cond, fields, id_only=False, toarray=True)

    @classmethod
    def get_mailto_list(cls, id_only=False):
        result = cls._get_all_data()
        mail_to_list = []
        mail_cc_list = []
        for item in result:
            mail_cc_list.append(item.get('email'))
            for country in item.get('country'):
                owner = country.values()[0]
                mail_to_list.append(owner[0])
        return list(set(mail_to_list)), mail_cc_list

    @classmethod
    def get_mailto_by_country(cls, country_name, id_only=False):
        result = cls._get_all_data()
        mail_to = []
        mail_cc = []
        for item in result:
            for country in item.get('country'):
                country_values = country.get(country_name)
                if country_values:
                    mail_to.append(country_values[0])
                    mail_cc.append(item.get('email'))
        return list(set(mail_to)), list(set(mail_cc))


class LocalizationHistory(ModelBase):

    """
    examples:
        {
            "module_path": ["a", "b", "c"],
            "target": 1231231,
            "name": "home_add",
            "alias": "home add",
            "modified_at": 1404460538,
            "modifier_id": 3,
            "xml_file" : "tips_strings.xml",
        },
        the alias can also be:
            [
                null,
                'test'
            ]
    """

    db = 'i18n'
    collection = "localization_history"

    required = (
        'module_path', 'target', 'name', 'tag_name', 'alias', 'modified_at',
        'modifier_id', 'xml_file')

    @classmethod
    def insert_history(
            cls, platform, category, appname, appversion, locale, module_path,
            name, alias, tag_name, xml_file, modifier_id=1):
        target_cond = {
            'appname': appname, 'appversion': appversion,
            'platform': platform, 'category': category, 'locale': locale}
        target = LocalizationInfo.find_id_by_unique(target_cond)
        if not target:
            _LOGGER.warning("invalid target: %s", locale)
            raise exception.DataError("invalid target")

        str_alias = '['
        if len(alias) > 1:
            for alias_item in alias:
                content = alias_item.get("content")
                if type(content) is dict:
                    content = content['content']
                str_alias = str_alias + content + ','
            str_alias = str_alias + ']'
        else:
            content = alias[0].get("content")
            if type(content) is dict:
                content = content['content']
            str_alias = content

        history_data = {
            'module_path': module_path, 'target': target,
            'name': name, 'tag_name': tag_name, 'alias': str_alias,
            "modified_at": now_timestamp(), 'modifier_id': modifier_id,
            "xml_file": xml_file}

        # left to be replaced with detailed exception class
        _LOGGER.info("insert history info: %s", history_data)
        cls.insert(history_data, check_unique=False)

    @classmethod
    def get_history_by_userid(
            cls, cond, platform, category, appname,
            appversion, locale, sort=None):
        """
        get history info by user_id
        """
        target_cond = {
            'appname': appname, 'appversion': appversion,
            'platform': platform, 'category': category, 'locale': locale}
        target = LocalizationInfo.find_id_by_unique(target_cond)
        if not target:
            _LOGGER.warning("invalid target: %s", locale)
            raise exception.DataError("invalid target")
        cond["target"] = target
        fields = {"modified_at": 1, "name": 1, "alias": 1, "_id": 0}
        data = [{
            'time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
                s.get('modified_at'))),
            "name": s.get("name"),
            "alias": s.get("alias")}
            for s in cls.find(cond, fields).sort(sort)]
        f = lambda x, y: x if y in x else x + [y]
        data = reduce(f, [[], ] + data)
        return data


class LocalizationErrorlog(ModelBase):

    """
    examples:
        {
            "name": "share_page",
            "message": "123456",
            'target': ObjectId('53d771d9bc3dcaf6979f2890')
        }
    """

    db = 'i18n'
    collection = 'localization_errorlog'

    required = ('target', 'name', 'message')

    @classmethod
    def store_error_message(cls, target_id, items):
        items = list(items)
        if not isinstance(target_id, ObjectId):
            target_id = ObjectId(target_id)
        for error_item in items:
            name = error_item.get("string_name")
            message = error_item.get("error_msg")
            error_log_info = {
                'target': target_id, "name": name, "message": message}
            cls.save(error_log_info)

    @classmethod
    def get_errorlog_by_target(cls, target):
        """
        get history info by user_id
        """
        if not isinstance(target, ObjectId):
            target_id = ObjectId(target)
        fields = {"_id": 0, "target": 0}
        target_info = cls.find({'target': target_id}, fields, toarray=True)
        if not target_info:
            raise exception.DataError(
                "can not find the error log info with target %s", target)
        return target_info


class LocalizationPicture(ModelBase):

    """
    examples:
        {
            "appname": "mobi.mgeek.TunnyBrowser",
            "name": "share_page",
            "picture_id": "1.1.1.png",
            'description': ''
        }
    """

    db = 'i18n'
    collection = 'localization_picture'

    required = ('appname', 'name', 'picture_id')
    optional = (('description', ''),)

    @classmethod
    def store_picture_info(cls, appname, picture_info):
        picture_info['appname'] = appname
        obj = cls.find(
            {'appname': appname,
                'name': picture_info.get("name")}, one=True)
        if obj:
            _id = obj.get("_id")
            cls.update({'_id': _id}, picture_info)
        else:
            cls.save(picture_info)

    @classmethod
    def get_picture_by_appname(cls, appname, name):
        """
        get history info by user_id
        """
        fields = {"_id": 0, "appname": 0}
        picture_info = cls.find(
            {'appname': appname, "name": name}, fields, one=True)
        if not picture_info:
            picture_info = {}
            picture_info["pic_url"] = ""
            picture_info["description"] = ""
            _LOGGER.warn(
                "localization_picture not found for appname: %s; name: "
                "%s", appname, name)
        pic_id = picture_info.get("picture_id", "")
        if pic_id:
            picture_info["pic_url"] = "http://%s/admin/media/%s/%s" % (
                HOST, appname, pic_id)
        else:
            picture_info["pic_url"] = ""
        return picture_info


class CommentedTreeBuilder(ET.XMLTreeBuilder):

    def __init__(self, html=0, target=None):
        ET.XMLTreeBuilder.__init__(self, html, target)
        self._parser.CommentHandler = self.handle_comment

    def handle_comment(self, data):
        self._target.start(ET.Comment, {})
        self._target.data(data)
        self._target.end(ET.Comment)

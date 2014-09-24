# -*- coding: UTF-8 -*-
import logging
import sys
import os
import subprocess
import re
import xml.etree.cElementTree as ET
ET.register_namespace('xliff', 'urn:oasis:names:tc:xliff:document:1.2')
ET.register_namespace('tools', 'http://schemas.android.com/tools')
import xlrd
from pymongo import Connection
from provisionadmin.model.base import ModelBase
from provisionadmin.model.i18n import LocalizationStrings, LocalizationTask
from provisionadmin.settings import ADAPTER_MAP_PATH
from provisionadmin.utils.common import unix_time
from provisionadmin.settings import DB_SETTINGS


logger = logging.getLogger("adapter")


class LocaleInfo(ModelBase):

    @classmethod
    def new(cls, appname, appversion, locale=""):
        '''
        create a new locale title
        locale=='' means default values
        '''
        instance = cls()
        instance.appname = appname
        instance.appversion = appversion
        instance.locale = locale
        instance.creator_id = 1
        instance.created_at = unix_time()
        return instance


class LocalizationModules(ModelBase):

    @classmethod
    def new(cls, localization_info, modules=[]):
        instance = cls()
        instance.localization_info = localization_info
        instance.modules = modules
        return instance


class LocalizationTask_Adapter(ModelBase):

    @classmethod
    def new(cls, target_id, refer_id, total, finished, status, creator_id=1):
        instance = cls()
        instance.target= target_id
        instance.reference = refer_id
        instance.creator_id = creator_id
        instance.created_at = instance.last_built_at = unix_time()
        instance.strings = {'modified_at': unix_time(),\
                            'total': total,\
                            'finished': finished,\
                            'status': status}
        return instance


class TranslationString(ModelBase):

    _INDEXES = {'check_uniq': {'localization_info': 1, 'name': 1}}

    @classmethod
    def new(cls, localization_info, module_path, xml_file, string_name, string_type, string_alias, finished=False):
        '''
        create a new translation string
        '''
        instance = cls()
        instance.localization_info = localization_info
        instance.module_path = module_path
        finished = False if not string_alias else True
        instance.xml_file = xml_file
        instance.name = string_name
        instance.tag_name = string_type
        instance.alias = string_alias
        instance.finished = finished
        return instance


DECOMPILE_PATH = '/root/test/i18nAdapter/apk_static/decompile-apk'
DEFAULT_MAP_PATH = '/root/test/i18nAdapter/adapter_map'
SRC_XML_PATH = '/root/test/i18nAdapter/res-src'

STRING_TAG_RE = r'^<string .*?name="(.*?)".*?>(.*?)</string>'
string_tag_compile = re.compile(STRING_TAG_RE, re.S)
ARRAY_TAG_RE = r'^<item.*?>(.*?)</item>'
ARRAY_TAG_RE_BLANK = r'^<item.*?/>'
array_tag_compile = re.compile(ARRAY_TAG_RE, re.S)
array_tag_blank_compile = re.compile(ARRAY_TAG_RE_BLANK, re.S)

TAG_NAMES = ['string', 'string-array', 'plurals']

adapter_map = {}

#MONGO_CONN_STR = 'mongodb://127.0.0.1'
MONGO_CONN_STR = DB_SETTINGS['i18n']['host']

_db_conn = Connection(host=MONGO_CONN_STR, max_pool_size=10, safe=True, network_timeout=5)
I18N_DB = _db_conn['i18n']


'''
after upladed xml files and apk file, we call this function to init adapter
'''
def init_adapter(uploaded_xml_path=SRC_XML_PATH, decompile_path=DECOMPILE_PATH):
    global adapter_map
    adapter_map = {}
    #load_adapter_map(ADAPTER_MAP_PATH)
    load_adapter_from_xls(ADAPTER_MAP_PATH)
    default_values = {}
    other_values = load_xml(uploaded_xml_path)
    package_name, version_name = load_manifest(decompile_path)

    '''
    core logic
    '''
    xml_to_module(uploaded_xml_path, default_values, other_values)

    #logger.debug('default:%s' % default_values)
    #logger.debug('others:%s' % other_values)

    save_to_db(package_name, version_name, default_values, is_origin=True)
    for other_value in other_values:
        logger.debug('ready to save %s to db' % other_value)
        save_to_db(package_name, version_name, other_values.get(other_value), lang=other_value[7:])
    refresh_locale_task(package_name, version_name)

    logger.debug('finished init_adapter for [%s] [%s]' % (package_name, version_name))
    return package_name, version_name


'''
for version 1.3
'''
def init_adpter_Ex(package_name, version_name, uploaded_xml_path=SRC_XML_PATH):
    global adapter_map
    adapter_map = {}
    #load_adapter_map(ADAPTER_MAP_PATH)
    load_adapter_from_xls(ADAPTER_MAP_PATH)
    default_values = {}
    other_values = load_xml(uploaded_xml_path)
    '''
    core logic
    '''
    xml_to_module(uploaded_xml_path, default_values, other_values)

    #logger.debug('default:%s' % default_values)
    #logger.debug('others:%s' % other_values)

    save_to_db(package_name, version_name, default_values, is_origin=True)
    for other_value in other_values:
        logger.debug('ready to save %s to db' % other_value)
        save_to_db(package_name, version_name, other_values.get(other_value), lang=other_value[7:])
    refresh_locale_task(package_name, version_name)

    logger.debug('finished init_adapter for [%s] [%s]' % (package_name, version_name))
    return package_name, version_name


def load_adapter_from_xls(xls_path):
    data = xlrd.open_workbook(xls_path)
    for sheet_name in data.sheet_names():
        module_name = sheet_name
        table = data.sheet_by_name(sheet_name)
        nrows = table.nrows
        ncols = table.ncols
        for row_index in range(nrows):
            if row_index == 0:
                continue
            row_data = table.row_values(row_index)
            adapter_key = row_data[0] + '/' + row_data[1]
            adapter_value = module_name + '.' + row_data[2]
            adapter_map[adapter_key] = adapter_value


def load_adapter_map(map_path):
    fp = open(map_path, 'r')
    for item in fp:
        item = item.replace('\n','')
        src, dst = item.split('\t')
        adapter_map[src] = dst


def get_adapter_module(adapter_key):
    return adapter_map.get(adapter_key)


'''
adapter logic
get element from origin xml file, then put it into module by adapter_map
'''
def xml_to_module(origin_xml_path, default_values, other_values):
    #firstly, load default values's xml
    default_values_path = os.path.join(origin_xml_path, 'values')
    map_to_module(default_values_path, default_values)
    #secondly, load other language value's xml
    for other_lang_name in other_values:
        other_values_path = os.path.join(origin_xml_path, other_lang_name)
        map_to_module(other_values_path, other_values.get(other_lang_name))


def parse_tag(ele):
    if ele.tag == 'string':
        match_group = string_tag_compile.match(ET.tostring(ele, encoding='utf-8'))
        if not match_group:
            logger.warn('string tag not match regex![%s]' % ET.tostring(ele, encoding='utf-8'))
            return None
        return {'name': ele.attrib.get('name'), 'tag': 'string', 'alias': match_group.group(2)}

    if ele.tag == 'string-array':
        item_list = []
        for sub_ele in ele:
            match_group = array_tag_compile.match(ET.tostring(sub_ele, encoding='utf-8'))
            if not match_group:
                match_blank = array_tag_blank_compile.match(ET.tostring(sub_ele, encoding='utf-8'))
                if not match_blank:
                    logger.warn('string-array item not match regex![%s]' % ET.tostring(sub_ele, encoding='utf-8'))
                    continue
                else:
                    item_list.append('')
            else:
                item_list.append(match_group.group(1))
        return {'name': ele.attrib.get('name'), 'tag': 'string-array', 'alias': item_list}

    if ele.tag == 'plurals':
        '''
        plurals_map = {}
        for sub_ele in ele:
            quantity_name = sub_ele.attrib.get('quantity')
            match_group = array_tag_compile.match(ET.tostring(sub_ele, encoding='utf-8'))
            if not match_group:
                logger.warn('plurals item not match regex![%s]' % ET.tostring(sub_ele, encoding='utf-8'))
                continue
            plurals_map[quantity_name] = match_group.group(1)
        return {'name': ele.attrib.get('name'), 'tag': 'plurals', 'alias': plurals_map}
        '''
        plurals_list = []
        for sub_ele in ele:
            quantity_name = sub_ele.attrib.get('quantity')
            match_group = array_tag_compile.match(ET.tostring(sub_ele, encoding='utf-8'))
            if not match_group:
                match_blank = array_tag_blank_compile.match(ET.tostring(sub_ele, encoding='utf-8'))
                if not match_blank:
                    logger.warn('plurals-array item not match regex![%s]' % ET.tostring(sub_ele, encoding='utf-8'))
                    continue
                else:
                    plurals_list.append({'tips': quantity_name, 'content': ''})
            else:
                plurals_list.append({'tips': quantity_name, 'content': match_group.group(1)})

        #return {'name': ele.attrib.get('name'), 'tag': 'plurals', 'alias': plurals_list}
        return None

    #return {'name': ele.attrib.get('name'), 'tag': 'other', 'alias': ele.text}
    return None


def map_to_module(values_path, module_map):
    values_xmls = os.listdir(values_path)
    for xml_file in values_xmls:
        xml_path = os.path.join(values_path, xml_file)
        if os.path.isfile(xml_path):
            xml_tree = ET.ElementTree(file=xml_path)
            xml_root = xml_tree.getroot()
            for sub_ele in xml_root:
                translatable = sub_ele.attrib.get('translatable')
                if translatable == 'false':
                    continue
                i18n_enable = sub_ele.attrib.get('i18n')
                if i18n_enable == 'false':
                    continue
                sub_ele_name = sub_ele.attrib.get('name')
                if sub_ele_name is None:
                    logger.warn('name attrib not found, skip...[%s]' % ET.tostring(sub_ele))
                    continue
                adapter_key = xml_file+'/'+sub_ele_name
                adapter_module = get_adapter_module(adapter_key)
                if not adapter_module:
                    '''
                    if not found module, we specify other module so that we
                    will not miss any xml element
                    '''
                    adapter_module = 'other'

                module_list = module_map.setdefault(adapter_module, [])
                parsed_dict = parse_tag(sub_ele)
                if parsed_dict is not None:
                    parsed_dict.update({'xml_file': xml_file})
                    module_list.append(parsed_dict)


def save_locale_info(locale_info):
    assert locale_info
    obj = I18N_DB.localization_info.find_one({'appname': locale_info.appname,\
                                              'appversion': locale_info.appversion,\
                                              'locale': locale_info.locale})
    if obj:
        return LocaleInfo(obj)._id

    obj_id = I18N_DB.localization_info.save(locale_info)
    return obj_id


def refresh_locale_task(appname, appversion):
    locale_infos = I18N_DB.localization_info.find({'appname': appname, 'appversion': appversion, 'locale':{'$ne':''}})
    for locale_info in locale_infos:
        locale = locale_info['locale']
        logger.info('refresh locale[%s] task' % locale)
        LocalizationStrings.refresh_app_strings(appname, appversion, locale)
        LocalizationTask.refresh_task(appname, appversion, locale)


def save_modules_info(module_info):
    assert module_info


def save_trans_string(trans_string):
    assert trans_string
    import simplejson
    from bson import ObjectId
    cond = {'localization_info': trans_string.localization_info,\
            'name': trans_string.name}
    obj = I18N_DB.localization_strings.find_one(cond)
    if obj:
        old_string = TranslationString(obj)
        if old_string.module_path == trans_string.module_path:
            I18N_DB.localization_strings.update({'_id': old_string._id}, trans_string)
            return old_string._id
    else:
        obj_id = I18N_DB.localization_strings.save(trans_string)
        return obj_id


def save_to_db(package_name, version_name, module_map, lang='en', is_origin=False):
    if is_origin:
        locale = ''
    else:
        locale = lang

    '''
    save locale info into LocaleInfo Collection
    '''
    new_locale = LocaleInfo.new(package_name, version_name, locale)
    locale_info_id = save_locale_info(new_locale)
    if is_origin:
        LocalizationTask.clear_task_strings(package_name, version_name, locale)

    '''
    create modules collection data for each locale info id

    '''
    module_info = LocalizationModules.new(locale_info_id)
    exists_locale = I18N_DB.localization_modules.find_one({'localization_info': locale_info_id})
    if exists_locale:
        module_info = LocalizationModules(exists_locale)
        if not module_info.modules:
            module_info.modules = []

    xml_count = 0
    '''
    save translation string into TranslationString Collection
    '''
    for module_name, string_list in module_map.items():
        module_paths = module_name.split('.')
        for string_item in string_list:
            xml_count += 1
            new_trans_string = TranslationString.new(locale_info_id,\
                                                    module_paths,\
                                                    string_item['xml_file'],\
                                                    string_item['name'],\
                                                    string_item['tag'],\
                                                    string_item['alias']
                                                    )
            save_trans_string(new_trans_string)
        '''
        check module path in module collection
        '''
        check_module_list(module_info.modules, module_paths)

    '''
    find and modify module collection with new modules
    '''
    I18N_DB.localization_modules.find_and_modify({'localization_info': locale_info_id}, module_info, upsert=True, new=True)

    '''
    create task for origin values
    '''
    if is_origin:
        #check unique
        print 'adapter origin xml count:%d' % xml_count
        new_task = LocalizationTask_Adapter.new(locale_info_id, locale_info_id, xml_count, xml_count, 'finished')
        I18N_DB.localization_task.find_and_modify({'target': locale_info_id}, new_task, upsert=True, new=True)
    '''
    else:
        #refresh task for other locale
        LocalizationTask.refresh_task(package_name, version_name, locale)
    '''


'''
merge and refresh module path
'''
def check_module_list(origin_list, dist_list):
    temp_list = origin_list
    for module in dist_list:
        if temp_list is None:
            temp_list = []
        is_find = False
        temp_temp_list = list(temp_list)
        for o_module in temp_temp_list:
            if o_module['name'] == module:
                temp_list = o_module.get('modules')
                if not temp_list:
                    o_module.update({'modules':[]})
                    temp_list = o_module.get('modules')
                is_find=True
                break
        if not is_find:
            new_item = {'name': module, 'modules': []}
            temp_list.append(new_item)
            temp_list = new_item.get('modules')


def load_xml(origin_xml_path):
    other_modules = {}
    f = lambda s: s.startswith('values-')
    src_xmls = filter(f, os.listdir(origin_xml_path))
    for src_xml in src_xmls:
        other_modules.setdefault(src_xml, {})
    return other_modules


def load_manifest(decompile_dir):
    '''
    load basic info fron AndroidManifest.xml
    '''
    manifest_path = os.path.join(decompile_dir, 'AndroidManifest.xml')
    manifest_tree = ET.ElementTree(file=manifest_path)
    manifest_root = manifest_tree.getroot()
    version_name = manifest_root.attrib.get('{http://schemas.android.com/apk/res/android}versionName')
    package_name = manifest_root.attrib.get('package')

    new_locale = LocaleInfo.new(package_name, version_name, '')
    locale_info_id = save_locale_info(new_locale)

    return package_name, version_name


if __name__ == "__main__":
    init_adapter()

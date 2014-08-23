'''
Created on Feb 9, 2012

@author: fli
'''
import logging
from dolphinop.db import cursor_to_array

logger = logging.getLogger('dolphinop.db')

_db = None

LAYOUT_LIST = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
DEFAULT_SOURCE = 'ofw'


_SECTION_FIELDS = {
    '_id': 0,
    'id': 1,
    'title': 1,
    'ico': 1,
    'order': 1,
    'time': 1,
    'groups': 1,
    'layout': 1,
    'sources': 1,
}


def get_section_by_id(section_id):
    cond = {'id': section_id}
    return _db.contentSections.find_one(cond, fields=_SECTION_FIELDS)


def get_section(cond):
    return _db.contentSections.find_one(cond, fields=_SECTION_FIELDS)


def get_section_by_package(package_name, source, modified_time, api):
    cond = {'packages': package_name, 'api': api}
    sections = []
    for item in LAYOUT_LIST:
        cond['layout'] = item
        section_list = _db.contentSections.find(cond, fields=_SECTION_FIELDS)
        section = None
        section_default = None
        for sec in section_list:
            if source in sec['sources']:
                section = sec
            if DEFAULT_SOURCE in sec['sources']:
                section_default = sec
        if section:
            if section['time'] > modified_time:
                del section['sources']
                sections.append(section)
        elif section_default:
            if section_default['time'] > modified_time:
                del section_default['sources']
                sections.append(section_default)
    return cursor_to_array(sections)


def get_section_by_layout(layout, package_name, source, modified_time, api):
    cond = {'packages': package_name, 'api': api, 'layout': layout}
    section_list = _db.contentSections.find(cond, fields=_SECTION_FIELDS)
    result = None
    section = None
    section_default = None
    for sec in section_list:
        if source in sec['sources']:
            section = sec
        if DEFAULT_SOURCE in sec['sources']:
            section_default = sec
    if not section:
        section = section_default
    if section:
        if section['time'] > modified_time:
            del section['sources']
            result = section
    return result


def update_section(cond, data):
    status = _db.contentSections.update(cond, data, upsert=True, multi=True)
    return status


def package_novel(item):
    result_dict = {
        'title': item['title'],
        'url': item['url'],
        'items': item['items'],
    }
    return result_dict


def get_novels(package_name, source, title):
    cond = {'packages': package_name, 'sources': source}
    if title:
        cond['title'] = title
    novels = {}
    coll = _db.contentNovel.find_one(cond)
    if coll:
        novels = package_novel(coll)

    return novels

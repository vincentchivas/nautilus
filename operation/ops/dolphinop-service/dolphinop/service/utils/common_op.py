#!/usr/bin/env python
# -*- coding:utf-8 -*-
# coder yfhe

import json
import sys
import httplib
import logging
import datetime
from django.http import HttpResponse
from dolphinop.service.errors import parameter_error, internal_server_error
from dolphinop.service.utils.content import ALL_FLAG, ALL_WEIGHT, MATCH_WEIGHT

def get_logger(role):
    matchs = {
        'service': 'dolphinop.service',
        'db': 'dolphinop.db',
    }
    return logging.getLogger(matchs[role])

LOGGER = get_logger('service')


def get_cond(args, ORIGINIZE, fields):
    cond = {}
    for key, value in args.items():
        if key in ORIGINIZE and key in fields:
            match = ORIGINIZE[key]
            if not match[1]:
                cond.update(eval(match[0]))
            else:
                cond.update(eval(match[0] % (value, value))
                            if match[1] == 2 else eval(match[0] % value))
    return cond

def filter_gray_level(sections, mark):
    result = []
    for item in sections:
        min_mark = item['_rule'].get('min_mark', 1)
        max_mark = item['_rule'].get('max_mark', 101)
        try:
            mark = int(mark)
        except:
            mark = None

        if mark != None and mark <= 100 and mark >= 1:
            if mark >= max_mark or mark < min_mark:
                continue

        elif min_mark != 1 or max_mark != 101:
            continue

        result.append(item)
    return result

def filter_sdk(sections, sdk):
    result = []
    if sdk != None:
        try:
            sdk = int(sdk)
        except:
            sdk = None

    for section in sections:
        min_sdk = section['_rule'].get('min_sdk')
        max_sdk = section['_rule'].get('max_sdk')
        if min_sdk == None or not max_sdk or (sdk != None and sdk >= min_sdk and sdk <= max_sdk):
            result.append(section)
    return result

def filter_operators(sections, op):
    specials = []
    commons = []
    for item in sections:
        if op in item['_rule']['operators']:
            specials.append(item)
        elif ALL_FLAG in item['_rule']['operators']:
            commons.append(item)
    return specials if len(specials) else commons

def paras_sort(sections, paras_dic):
    if not sections:
        return []
    for index, value in paras_dic.items():
        sections.sort(key = lambda x:x['_rule'][index], reverse=value)
        test_para = sections[0]['_rule'][index]
        results = []
        for section in sections:
            if section['_rule'][index] == test_para:
                results.append(section)
            else:
                break
        sections = results
    return sections

def filter_rule(sections, dicts, paras_dic=None):
    if 'operators' in dicts:
        sections = filter_operators(sections, dicts.pop('operators') )
    for index, section in enumerate(sections):
        section['_rate_'] = 0
        for key, value in dicts.items():
            alternative_rule = section["_rule"].get(key)
            include = alternative_rule.get('include') if alternative_rule else None
            exclude = alternative_rule.get('exclude') if alternative_rule else None
            if value not in exclude:
                if value in include:
                    section['_rate_'] += MATCH_WEIGHT
                    continue
                elif ALL_FLAG in include:
                    section['_rate_'] += ALL_WEIGHT
                    continue
            section['_rate_'] -= 1000
    sections.sort(key= lambda x:x['_rate_'], reverse=True)
    max_rate = sections[0]['_rate_']
    results = [s for s in sections if s.pop('_rate_') == max_rate]
    if paras_dic:
            sections = paras_sort(results, paras_dic)
    if max_rate < 0 or len(sections) == 0:
        return []
    return sections[0]

def _parse_rule(sections, arg, name, types=None):
    commons = []
    specials = []
    deletes = []
    for key, section in enumerate(sections):
        alternative_rule = section["_rule"].get(name)
        include = alternative_rule.get('include') if alternative_rule else None
        exclude = alternative_rule.get('exclude') if alternative_rule else None
        if exclude and arg in exclude:
            deletes.append(key)
        elif include:
            if arg in include:
                specials.append(key)
            elif ALL_FLAG in include:
                commons.append(key)
            else:
                deletes.append(key)
        elif not include:
            deletes.append(key)
            #if arg == None:
            #    commons.append(key)
            #else:
            #    deletes.append(key)
    if specials and types not in ['especial']:
        abandons = deletes + commons
    else:
        abandons = deletes
    if len(abandons):
        abandons.sort(reverse=True)
        for key in abandons:
            del sections[key]


def parse_rule(section_infos, args, rules, types=None):
    #print 'enter parse_rule'
    if rules == None or not isinstance(rules, (list,dict)):
        return section_infos
    for key, value in rules.items():
        if types and key in types['especial']:
            #print 'enter  _parse_rule'
            _parse_rule(section_infos, args.get(key), value, 'especial')
        else:
            _parse_rule(section_infos, args.get(key), value)


def _convert_func(func):
    def wrapper(*args, **kwargs):
        if func == bool:
            return bool(int(*args, **kwargs))
        return func(*args, **kwargs)
    return wrapper


def get_params(request, method, keys):
    # valid example:
    #    pn&need
    #    src&option&ofw
    #    vn&option&0&int
    try:
        result = {}
        query_dict = request.__getattribute__(method.upper())
        for key in keys:
            paras = key.split('&')
            lenth = len(paras)
            if lenth > 0:
                tmp1 = paras[0]
                tmp = query_dict.get(tmp1)
                if lenth > 1:
                    tmp2 = paras[1]
                    if tmp2 == 'need' and not tmp:
                        return parameter_error(request, tmp1)
                    if tmp2 == 'notNeed' and not tmp:
                        continue
                    if lenth > 2 and tmp == None:
                        tmp = paras[2]
                    if lenth > 3 and tmp != None:
                        try:
                            tmp = _convert_func(eval(paras[3]))(tmp)
                        except Exception, e:
                            LOGGER.exception(e)
                            tmp = _convert_func(eval(paras[3]))(paras[2])
                            return parameter_error(request, tmp1)
                    result[tmp1] = tmp
        return result
    except Exception, e:
        LOGGER.exception(e)
        return internal_server_error(request, e, sys.exc_info())


def json_response(func):
    def json_responsed(request, *args, **kwargs):
        status_code = httplib.OK
        retval = func(request, *args, **kwargs)
        if isinstance(retval, HttpResponse):
            return retval
        content = json.dumps(retval, skipkeys=True, ensure_ascii=False)
        response = HttpResponse(
            content, content_type='application/json; charset=utf-8', status=status_code)
        return response
    return json_responsed

### old ####


def now():
    return datetime.datetime


def dup_by_key(items, sort=True, cmp_func=None):
    dup_dict = {}
    for item in items:
        label = item['_key']
        dup_key = json.dumps(label)
        if dup_key not in dup_dict or dup_dict[dup_key].get('_priority') < item.get('_priority'):
            dup_dict[dup_key] = item
    keys = dup_dict.keys()
    if sort:
        keys.sort(cmp=cmp_func)
    result_section = []
    for label in keys:
        result_section.append(dup_dict[label])
    return result_section


def _or(*l):
    for v in l:
        if v is not None:
            return v
    return None


def normalize_result(res, required=None):
    ret = {}
    if required is None:
        return res
    for q in required:
        ret[q] = _or(res.get(q), res["_key"].get(q), res['_meta'].get(q),
                     res['_meta_extend'].get(q) if '_meta_extend' in res else None)
    return ret


def _rule_parse(section, args, name):
    alternative_rule = section["_rule"].get(name)
    if not alternative_rule:
        return True
    if alternative_rule and alternative_rule.get("include") and args.get(name) is not None and ALL_FLAG not in alternative_rule["include"] and args[name] not in alternative_rule["include"]:
        return False
    if alternative_rule and alternative_rule.get("exclude") and args.get(name) is not None and args[name] in alternative_rule["exclude"]:
        return False
    return True


def rule_parse(section_infos, args, rules=None):
    sections = []
    if rules == None:
        rules = []
    for section in section_infos:
        flag = True
        for rule_name in rules:
            if not _rule_parse(section, args, rule_name):
                flag = False
                break
        if flag:
            sections.append(section)
    return sections

#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On Jan 25, 2013
# @Author : Jun Wang
# Email: jwang@bainainfo.com

import json
import datetime


def now():
    return datetime.datetime.now()


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
    if alternative_rule and alternative_rule.get("include") and args.get(name) is not None and args[name] not in alternative_rule["include"]:
        return False
    if alternative_rule and alternative_rule.get("exclude") and args.get(name) is not None and args[name] in alternative_rule["exclude"]:
        return False
    return True


def rule_parse(section_infos, args, rules=[]):
    sections = []
    for section in section_infos:
        flag = True
        for rule_name in rules:
            if not _rule_parse(section, args, rule_name):
                flag = False
                break
        if flag:
            sections.append(section)
    return sections

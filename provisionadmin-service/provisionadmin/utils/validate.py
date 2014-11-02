#! /usr/bin/env python
# coding=utf-8
import types
import re


class MetaValidate(object):
    @classmethod
    def check_validate(cls, shape, value):
        handle = None
        methodName = "Is" + shape
        handle = getattr(cls, methodName)
        return handle(value)

    @classmethod
    def IsNumber(cls, varObj):
        return isinstance(varObj, types.IntType)

    @classmethod
    def IsString(cls, varObj):
        return isinstance(varObj, types.StringType)

    @classmethod
    def IsFloat(cls, varObj):
        return isinstance(varObj, types.FloatType)

    @classmethod
    def IsDict(cls, varObj):
        return isinstance(varObj, types.DictType)

    @classmethod
    def IsTuple(cls, varObj):
        return isinstance(varObj, types.TupleType)

    @classmethod
    def IsList(cls, varObj):
        return isinstance(varObj, types.ListType)

    @classmethod
    def IsBoolean(cls, varObj):
        return isinstance(varObj, types.BooleanType)

    @classmethod
    def IsEmpty(cls, varObj):
        if len(varObj) == 0:
            return True
        return False

    @classmethod
    def IsNone(cls, varObj):
        return isinstance(varObj, types.NoneType)

    @classmethod
    def IsDate(cls, varObj):
    # 判断是否为日期格式,并且是否符合日历规则 2010-01-31
        if len(varObj) == 10:
            rule = '(([0-9]{3}[1-9]|[0-9]{2}[1-9][0-9]{1}|[0-9]{1}[1-9][0-9]{2}|[1-9][0-9]{3})-(((0[13578]|1[02])-(0[1-9]|[12][0-9]|3[01]))|((0[469]|11)-(0[1-9]|[12][0-9]|30))|(02-(0[1-9]|[1][0-9]|2[0-8]))))|((([0-9]{2})(0[48]|[2468][048]|[13579][26])|((0[48]|[2468][048]|[3579][26])00))-02-29)$/'
            match = re.match(rule, varObj)
            if match:
                return True
            return False
        return False

    @classmethod
    def IsEmail(cls, varObj):
    # 判断是否为邮件地址
        rule = '[\w-]+(\.[\w-]+)*@[\w-]+(\.[\w-]+)+$'
        match = re.match(rule, varObj)
        if match:
            return True
        return False

    @classmethod
    def IsChineseCharString(cls, varObj):
    # 判断是否为中文字符串
        for x in varObj:
            if (x >= u"\u4e00" and x <= u"\u9fa5") or (x >= u'\u0041' and x <= u'\u005a') or (x >= u'\u0061' and x <= u'\u007a'):
                continue
            else:
                return False
        return True

    @classmethod
    def IsChineseChar(cls, varObj):
    # 判断是否为中文字符
        if varObj[0] > chr(127):
            return True
        return False

    @classmethod
    def IsLegalAccounts(cls, varObj):
    # 判断帐号是否合法 字母开头，允许4-16字节，允许字母数字下划线
        rule = '[a-zA-Z][a-zA-Z0-9_]{3,15}$'
        match = re.match(rule, varObj)
        if match:
            return True
        return False

    @classmethod
    def IsIpAddr(cls, varObj):
    # 匹配IP地址
        rule = '\d+\.\d+\.\d+\.\d+'
        match = re.match(rule, varObj)
        if match:
            return True
        return False

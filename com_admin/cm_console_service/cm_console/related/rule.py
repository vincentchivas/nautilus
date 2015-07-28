# -*- coding: utf-8 -*-
import requests
import logging
import simplejson

from cm_console import settings
from cm_console.model import ArmoryMongo
from cm_console.model.common import classing_model

from armory.marine.respcode import (PARAM_REQUIRED, METHOD_ERROR, PARAM_ERROR)

_LOGGER = logging.getLogger(__name__)
RULE_HOST = settings.RULE_SERVICE_HOST


def refered_rule(appname, target_id, target_field, refered_data, old_id=None):
    """
    add the info of referenced rule
    """
    headers = {
        "Content-type": "application/json", "Accept": "text/plain"}
    url = "http://%s/%s/rule/v1/referInfo/add" % (RULE_HOST, appname)

    upload_para = {}
    upload_para["target_id"] = target_id
    upload_para["target_field"] = target_field
    upload_para["refered_data"] = refered_data
    if old_id:
        upload_para["old_target_id"] = old_id

    try:
        res = requests.post(
            url, data=simplejson.dumps(upload_para), headers=headers)
        if res.status_code != 200:
            _LOGGER.warning("add rule refered failed")
            return None
        else:
            upload_return = simplejson.loads(res.text)
            if upload_return["status"] == 0:
                return True
            elif upload_return["status"] == PARAM_REQUIRED:
                _LOGGER.warning("add refered info failed")
                return PARAM_REQUIRED
            elif upload_return["status"] == PARAM_ERROR:
                _LOGGER.warning("add refered info failed")
                return PARAM_ERROR
            else:
                return METHOD_ERROR
    except Exception as error:
        _LOGGER.exception(error)


def unrefered_rule(appname, target_id, target_field, unrefered_data):
    """
    add the info of referenced rule
    """
    headers = {
        "Content-type": "application/json", "Accept": "text/plain"}
    url = "http://%s/%s/rule/v1/referInfo/delete" % (RULE_HOST, appname)

    upload_para = {}
    upload_para["target_id"] = target_id
    upload_para["target_field"] = target_field
    upload_para["unrefered_data"] = unrefered_data

    try:
        res = requests.post(
            url, data=simplejson.dumps(upload_para), headers=headers)
        if res.status_code != 200:
            _LOGGER.warning("add rule refered failed")
            return None
        else:
            upload_return = simplejson.loads(res.text)
            if upload_return["status"] == 0:
                return True
            elif upload_return["status"] == PARAM_REQUIRED:
                _LOGGER.warning("add refered info failed")
                return PARAM_REQUIRED
            elif upload_return["status"] == PARAM_ERROR:
                _LOGGER.warning("add refered info failed")
                return PARAM_ERROR
            else:
                return METHOD_ERROR
    except Exception as error:
        _LOGGER.exception(error)


def inc_rule(appname, modelname, res_dict):
    # to make sure that the rule can not be delete if refered
    new_id = res_dict.get('id')
    rule_dict = res_dict.get('aosruledata')
    if rule_dict:
        rule_id = rule_dict.get('id')
        refered_data = {
            'modelName': modelname, 'id': new_id, 'modelField': 'aosruledata'}
        refered_rule(appname, rule_id, 'rule', refered_data)


def mod_rule(appname, modelname, req_dict, old_item):
    # make sure when modified predata, will change the refere info
    item_id = req_dict.get('id')
    rule_dict = req_dict.get('aosruledata')
    if rule_dict:
        rule_id = rule_dict.get('id')
        old_rule = old_item.get('aosruledata')
        old_id = old_rule.get('id')
        if old_id != rule_id:
            refered_data = {
                'modelName': modelname,
                'id': item_id,
                'modelField': 'aosruledata'}
            refered_rule(appname, rule_id, 'rule', refered_data, int(old_id))


def release_rule(appname, modelname, rawid):
    Model_Class = classing_model(modelname)
    item = Model_Class.find_one(appname, {'id': rawid})
    rule_dict = item.get('aosruledata')
    rule_id = rule_dict.get('id')
    unrefered_data = {
        'modelName': modelname, 'id': rawid, 'modelField': 'aosruledata'}
    unrefered_rule(appname, rule_id, 'rule', unrefered_data)

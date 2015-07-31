# -*- coding: utf-8 -*-
import logging

from cm_console.model.common import classing_model
from cm_console.view.common_base import CommonBase
from cm_console.view.check_data import check_save_dict

from cm_console.utils.validate_params import get_valid_params
from cm_console.utils.status import UploadStatus
from cm_console.utils.common import common_filter
from cm_console.related.rule import inc_rule, mod_rule
from cm_console.related.icon import inc_icon, mod_icon, get_icon_url

from armory.marine.respcode import PARAM_ERROR
from armory.marine.exception import ParamError
from armory.marine.util import unixto_string, now_timestamp
from armory.marine.json_rsp import json_response_ok, json_response_error


_LOGGER = logging.getLogger(__name__)


def check_release(modelname):
    Model_Name = classing_model(modelname)
    if hasattr(Model_Name, 'list_api'):
        fields = Model_Name.list_api['fields']
        return True if 'release' in fields else False
    return False


def common_check_unique(appname, modelname, temp_dict):
    Model_Name = classing_model(modelname)
    method = temp_dict.pop('method', None)
    temp_dict.pop('original_value', None)
    item_id = temp_dict.pop('id', 0)
    # when pop method and id, only "unique_key": "value" left
    name = temp_dict.keys()[0]
    value = temp_dict.get(name)
    unique_pass = False
    if hasattr(Model_Name, "unique"):
        unique_list = Model_Name.unique
        if name not in unique_list:
            return json_response_error(PARAM_ERROR, msg="%s not exist" % name)
        if method == 'add':
            if not Model_Name.find_one(appname, temp_dict):
                unique_pass = True
        elif method == 'update':
            old_item = Model_Name.find_one(appname, {'id': int(item_id)})
            if not Model_Name.find_one(appname, temp_dict):
                unique_pass = True
            else:
                old_val = old_item.get(name)
                # when update if old title not change
                unique_pass = True if old_val == value else False
        else:
            return json_response_error(PARAM_ERROR, msg="method is not apply")
    else:
        unique_pass = True
    return json_response_ok({"unique": unique_pass})


def common_create(appname, modelname, temp_dict):
    Model_Name = classing_model(modelname)
    try:
        temp_dict = CommonBase.clean_data(modelname, temp_dict)
    except ParamError as e:
        return json_response_error(PARAM_ERROR, msg=e.msg)
    # when save data, filter some useless data
    pop_list = [
        'id', 'last_release_ec2', 'last_release_local', 'release',
        'is_upload_local', 'is_upload_ec2']
    for key in pop_list:
        temp_dict.pop(key, None)
    if hasattr(Model_Name, "fields_check"):
        try:
            temp_dict = get_valid_params(temp_dict, Model_Name.fields_check)
        except ParamError as e:
            return json_response_error(PARAM_ERROR, msg=e.msg)
    temp_dict['first_created'] = temp_dict['last_modified'] = now_timestamp()

    #this is a factory function, to check some save data before insert if need
    (check_success, msg) = check_save_dict(appname, modelname, temp_dict)
    if not check_success:
        return json_response_error(PARAM_ERROR, msg=msg)
    insert_id = Model_Name.insert(appname, temp_dict)

    temp_dict['id'] = insert_id
    # if the model has ref icon and rule, increase the reference
    inc_icon(appname, modelname, temp_dict)
    inc_rule(appname, modelname, temp_dict)
    return json_response_ok(temp_dict)


def common_delete(appname, modelname, comfirm, item_ids):
    success_list = []
    data = {}
    Model_Name = classing_model(modelname)
    items = Model_Name.find(
        appname, {'id': {'$in': item_ids}}, fields={'_id': 0}, toarray=True)
    for item in items:
        item_id = item.get('id')
        success_list.append(common_filter(item))
        ret = CommonBase.delete_base(appname, modelname, item_id, comfirm)
        if ret:
            status = ret.get('status')
            model_dict = ret.get('model')
            if status:  # none or not zero, return directly
                success_list.remove(common_filter(model_dict))
                data['userlog'] = success_list
                return json_response_error(
                    status, msg="item has been refered", data=data)
    data['userlog'] = success_list
    return json_response_ok(data=data, msg='delete success items')


def common_update(appname, modelname, temp_dict, item_id):
    Model_Name = classing_model(modelname)
    temp_dict.pop("id", 0)
    try:
        temp_dict = CommonBase.clean_data(modelname, temp_dict)
    except ParamError as e:
        return json_response_error(PARAM_ERROR, msg=e.msg)
    if hasattr(Model_Name, "fields_check"):
        try:
            temp_dict = get_valid_params(temp_dict, Model_Name.fields_check)
        except ParamError as e:
            return json_response_error(PARAM_ERROR, msg=e.msg)
    cond = {"id": int(item_id)}
    temp_dict['last_modified'] = now_timestamp()
    # if the model has release field
    if check_release(modelname):
        temp_dict['release'] = UploadStatus.UNUPLOAD_LOCAL
    # find the old item before update, aim to track icon and rule
    old_item = Model_Name.find_one(appname, {'id': item_id}, {'_id': 0})

    #this is a factory function, to check some save data before save if need
    (check_success, msg) = check_save_dict(
        appname, modelname, temp_dict, item_id)
    if not check_success:
        return json_response_error(PARAM_ERROR, msg=msg)

    Model_Name.update(appname, cond, temp_dict)
    temp_dict['id'] = item_id
    # if model has refered icon and rule
    mod_icon(appname, modelname, temp_dict, old_item)
    mod_rule(appname, modelname, temp_dict, old_item)
    return json_response_ok(temp_dict)


def common_detail(appname, modelname, item_id):
    Model_Name = classing_model(modelname)
    cond = {'id': item_id}
    item = Model_Name.find_one(appname, cond, fields={'_id': 0})
    detail_item = CommonBase.viewdetail(appname, modelname, item)
    return json_response_ok(detail_item)


def common_list(appname, modelname, query_dict):
    model_list = []
    page_models = CommonBase.list_base(appname, modelname, query_dict)
    items = page_models['results']
    total = page_models['total']
    for item in items:
        if item.get('aosruledata'):
            item.update(
                CommonBase.fetch_lcpn(appname, item.get('aosruledata')))
        item['first_created'] = unixto_string(item.get('first_created'))
        item['last_modified'] = unixto_string(item.get('last_modified'))
        if item.get('last_release_ec2'):
            item['last_release_ec2'] = unixto_string(
                item.get('last_release_ec2'))
        else:
            item['last_release_ec2'] = ''
        if item.get('icon') is not None:
            item["icon"] = get_icon_url(appname, item['icon']['id'])
        model_list.append(item)
    data = {}
    data['total'] = total
    data['items'] = model_list
    return json_response_ok(data, msg='get model list')

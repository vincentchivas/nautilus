import logging

from cm_console.model import ArmoryMongo
from cm_console.model.common import classing_model
from cm_console.model.upload import package_data

from cm_console.view.common_base import CommonBase

from cm_console.utils.status import UploadStatus, PackageType
from cm_console.utils.common import upload_status

from cm_console.related.rule import release_rule

from armory.marine.util import now_timestamp
from armory.marine.respcode import (
    ONLINE_DATA_UNDELETE, DUPLICATE_DELETE,
    DATA_NOT_UPLOAD_TO_PRE, PACKAGE_DATA_ERROR)

_ADMIN = "admin"
_LOCAL = "local"
_EC2 = "ec2"
_LOGGER = logging.getLogger(__name__)


def refresh_status(appname, modelname, model_id):
    Model_Class = classing_model(modelname)
    result_dict = {}
    new_item = Model_Class.find_one(
        appname, {'id': model_id}, fields={'_id': 0})
    new_item = upload_status(new_item)
    fields = [
        'id', 'title', 'name', 'last_release_ec2', 'last_release_local',
        'release', 'is_upload_local', 'is_upload_ec2']
    for field in fields:
        result_dict[field] = new_item.get(field)
    return result_dict


def get_upload_table(modelname):
    '''
    every model has one map upload collection
    '''
    Model_Class = classing_model(modelname)
    upload_table = ''
    if hasattr(Model_Class, "upload_table"):
        upload_table = Model_Class.upload_table
    else:
        upload_table = modelname
    return upload_table


def _del_data_admin(appname, modelname, items):
    status = 0
    delete_success = []
    delete_failed = []
    Model_Class = classing_model(modelname)
    upload_table = get_upload_table(modelname)
    Local_db = ArmoryMongo[_LOCAL]
    for item in items:
        rawid = item.get('id')
        item_local = Local_db[upload_table].find_one(
            {"id": rawid}, fields={"_id": 0})
        if item_local:
            status = ONLINE_DATA_UNDELETE
            delete_failed.append(item)
            _LOGGER.error("id:%d should delete from local first" % rawid)
        else:
            release_rule(appname, modelname, rawid)
            model_dict = Model_Class.find_one(appname, {'id': rawid})
            _LOGGER.info(model_dict)
            CommonBase.dec_icon(appname, modelname, model_dict, rawid)
            # de referenced icon and rule
            delete_success.append(model_dict)
            Model_Class.remove(appname, {"id": rawid})
            _LOGGER.info("id:%d delete from admin success", rawid)
    return status, delete_success, delete_failed


def _del_data_local(appname, modelname, items):
    status = 0
    delete_success = []
    delete_failed = []
    Model_Class = classing_model(modelname)
    up_table = get_upload_table(modelname)
    Local_db = ArmoryMongo[_LOCAL]
    Ec2_db = ArmoryMongo[_EC2]
    for item in items:
        rawid = item.get('id')
        if not Ec2_db[up_table].find_one({"id": rawid}):
            if Local_db[up_table].find_one({"id": rawid}, fields={"_id": 0}):
                upt_status = {}
                upt_status = {
                    'is_upload_local': False,
                    'release': UploadStatus.UNUPLOAD_LOCAL,
                    'last_release_local': 0}
                Model_Class.update(appname, {"id": rawid}, upt_status)
                Local_db[up_table].remove({"id": rawid})

                item_suc = refresh_status(appname, modelname, rawid)
                delete_success.append(item_suc)

                _LOGGER.info("id:%d delete from local success", rawid)
            else:
                status = DUPLICATE_DELETE
                delete_failed.append(item)
        else:
            status = ONLINE_DATA_UNDELETE,
            item_fail = refresh_status(appname, modelname, rawid)
            delete_failed.append(item_fail)
            _LOGGER.error("id:%d should delete from ec2 first" % rawid)
    return status, delete_success, delete_failed


def _del_data_ec2(appname, modelname, items):
    status = 0
    delete_success = []
    delete_failed = []
    Model_Class = classing_model(modelname)
    up_table = get_upload_table(modelname)
    Ec2_db = ArmoryMongo[_EC2]
    for item in items:
        rawid = item.get('id')
        if Ec2_db[up_table].find_one({"id": rawid}):
            upt_status = {
                'is_upload_ec2': False,
                'last_release_ec2': 0,
                'release': UploadStatus.UNUPLOAD_EC2}
            Model_Class.update(
                appname, {"id": rawid}, upt_status)
            item_suc = refresh_status(appname, modelname, rawid)
            delete_success.append(item_suc)
            Ec2_db[up_table].remove({"id": rawid})
            _LOGGER.info("id:%d delete from ec2 success", rawid)
        else:
            status = DUPLICATE_DELETE
            item_fail = refresh_status(appname, modelname, rawid)
            delete_failed.append(item_fail)
    return status, delete_success, delete_failed


def _upload_local(appname, modelname, items):
    status = 0
    out_msg = 'upload to local successfully'
    upload_success = []
    upload_failed = []
    for item in items:
        save_info = upload2server(appname, modelname, item, server=_LOCAL)
        item_upload = refresh_status(appname, modelname, item.get('id'))
        if save_info[0]:
            upload_success.append(item_upload)
        else:
            status = PACKAGE_DATA_ERROR
            out_msg = save_info[1]
            upload_failed.append(item_upload)
    return status, out_msg, upload_success, upload_failed


def _upload_ec2(appname, modelname, items):
    status = 0
    out_msg = 'upload to ec2 successfully'
    upload_success = []
    upload_failed = []
    for item in items:
        release = item.get('release')
        if release == UploadStatus.UNUPLOAD_LOCAL:
            status = DATA_NOT_UPLOAD_TO_PRE
            item_upload = refresh_status(appname, modelname, item.get('id'))
            upload_failed.append(item_upload)
        else:
            save_info = upload2server(appname, modelname, item, server=_EC2)
            item_upload = refresh_status(appname, modelname, item.get('id'))
            if save_info[0]:
                upload_success.append(item_upload)
            else:
                status = PACKAGE_DATA_ERROR
                out_msg = save_info[1]
                upload_failed.append(item_upload)
    return status, out_msg, upload_success, upload_failed


def pack_save_data(req_dict):
    '''
     {
       '_sync_key':{'id': 123} ,
       '_rule':{'locale':[]},
       '_meta':{}
        }
    '''
    pack_type = req_dict.get('pack_type')
    save_data = {}
    if pack_type == PackageType.Common:
        save_data = {
            'id': req_dict.get('id'),
            '_meta': req_dict.get('_meta'),
            '_rule': req_dict.get('_rule'),
            '_sync_key': req_dict.get('_sync_key'),
            'last_modified': now_timestamp()}
    elif pack_type == PackageType.Inject:
        rule_dict = req_dict.get('_rule')
        packages = rule_dict.pop('packages', [])
        if len(packages) == 1:
            rule_dict['package'] = ','.join(packages)
        else:
            rule_dict['package'] = packages

        save_data.update(req_dict.get('_meta'))
        save_data.update(rule_dict)
        save_data['id'] = req_dict.get('id')
        save_data['last_modified'] = now_timestamp()
    else:
        save_data.update(req_dict.get('_meta'))
        save_data['_rule'].update(req_dict.get('_rule'))
        save_data['id'] = req_dict.get('id')
        save_data['last_modified'] = now_timestamp()
    return save_data


def upload2server(appname, modelname, item, server):
    Model_Class = classing_model(modelname)
    upload_table = get_upload_table(modelname)
    Remote_db = ArmoryMongo[server]
    # update status upload to local
    results = package_data(appname, modelname, item, server)
    # param1: success/failed true/false param2:msg  param3:return dict
    if not results[0]:
        return False, results[1]
    else:
        item_id = item.get('id')
        cond = {"id": item_id}
        res_dict = results[2]

        is_upload_server = "is_upload_%s" % server
        last_release_server = "last_release_%s" % server

        upt_status = {}
        upt_status[is_upload_server] = True
        upt_status[last_release_server] = now_timestamp()
        if server == _LOCAL:
            upt_status['release'] = UploadStatus.UNUPLOAD_EC2
        if server == _EC2:
            upt_status['release'] = UploadStatus.NOMORAL
        Model_Class.update(appname, cond, upt_status)

        save_data = pack_save_data(res_dict)
        Remote_db[upload_table].update(cond, save_data, True)
        return True, results[1]


def online_data(appname, modelname, place, items):
    status = 0
    upload_success = []
    upload_failed = []
    if place == _LOCAL:
        return _upload_local(appname, modelname, items)
    elif place == _EC2:
        return _upload_ec2(appname, modelname, items)
    else:
        status = -1
    return status, upload_success, upload_failed


def offline_data(appname, modelname, place, items):
    status = 0
    delete_success = []
    delete_failed = []
    if place == _ADMIN:
        return _del_data_admin(appname, modelname, items)
    elif place == _LOCAL:
        return _del_data_local(appname, modelname, items)
    elif place == _EC2:
        return _del_data_ec2(appname, modelname, items)
    else:
        status = -1
    return status, delete_success, delete_failed

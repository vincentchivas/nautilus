# -*- coding: utf-8 -*-
import requests
import logging
import simplejson
from cm_console.model import ArmoryMongo
from armory.marine.respcode import PARAM_REQUIRED, METHOD_ERROR
from cm_console import settings

_LOGGER = logging.getLogger(__name__)
RESOURCE_HOST = settings.RESOURCE_SERVICE_HOST
HOST = settings.HOST


def upload_icon_to_server(server, appname, icon_id):
    '''
     server: local or ec2
     appname:  pushadmin or provisionadmin
     icon_id: [1,2,3,4]
    '''
    headers = {
        "Content-type": "application/json", "Accept": "text/plain"}
    url = "http://%s/%s/resource/v1/icon/upload" % (RESOURCE_HOST, appname)
    upload_para = {}
    upload_para["server"] = server
    upload_para["items"] = icon_id

    try:
        res = requests.post(
            url, data=simplejson.dumps(upload_para), headers=headers)
        if res.status_code != 200:
            _LOGGER.warning("upload icon failed")
            return None
        else:
            upload_return = simplejson.loads(res.text)
            if upload_return["status"] == 0:
                return True
            elif upload_return["status"] == PARAM_REQUIRED:
                _LOGGER.warning("upload icon failed")
                return PARAM_REQUIRED
            else:
                return METHOD_ERROR
    except Exception as error:
        _LOGGER.exception(error)


def delete_icon_from_server(server, appname, icon_id):
    headers = {
        "Content-type": "application/json", "Accept": "text/plain"}
    url = "http://%s/%s/resource/v1/icon/delete" % (RESOURCE_HOST, appname)
    upload_para = {}
    upload_para["server"] = server
    upload_para["items"] = [icon_id]

    try:
        res = requests.post(
            url, data=simplejson.dumps(upload_para), headers=headers)
        if res.status_code != 200:
            _LOGGER.warning("delete icon failed")
            return None
        else:
            upload_return = simplejson.loads(res.text)
            if upload_return["status"] == 0:
                return True
            elif upload_return["status"] == PARAM_REQUIRED:
                _LOGGER.warning("delete icon failed")
                return PARAM_REQUIRED
            else:
                return METHOD_ERROR
    except Exception as error:
        _LOGGER.exception(error)


def get_icon_url(appname, icon_id, server="admin"):
    '''
    used for the list page to show icon
    '''
    server_url = "%s_url" % server
    icon_info = ArmoryMongo[appname]["icon"].find_one({"_id": icon_id})
    if icon_info:
        if server == "admin":
            return "http://%s/media/%s" % (HOST, icon_info['icon'])
        else:
            return icon_info[server_url]
    else:
        _LOGGER.error("icon:%s not in db", icon_id)
        return ""


def derefered_icon(appname, modelName, id, model_id, icon_field="icon"):
    """
    deference icon resource
    """
    icon_id = int(id) if not isinstance(id, int) else id
    icon_cond = {"_id": icon_id}
    icon_info = ArmoryMongo[appname]["icon"].find_one(icon_cond)
    if not icon_info:
        raise ValueError("icon:%s not in db", icon_id)
    refered_info = {}
    refered_info["id"] = int(model_id)
    refered_info["modelName"] = modelName
    refered_info["modelField"] = icon_field
    if not icon_info.get("refered_info"):
        icon_info["refered_info"] = []
    if refered_info in icon_info["refered_info"]:
        icon_info["refered_info"].remove(refered_info)
    icon_info.pop("_id")
    ArmoryMongo[appname]["icon"].update(icon_cond, {'$set': icon_info})
    _LOGGER.info("update the id refer info:%s", icon_id)


def refered_icon(
        appname, modelName, id, model_id, icon_field="icon", old_id=None):
    """
    add the info of referenced icon resource
    """
    icon_id = int(id) if not isinstance(id, int) else id
    icon_cond = {"_id": icon_id}
    icon_info = ArmoryMongo[appname]["icon"].find_one(icon_cond)
    if not icon_info:
        raise ValueError("icon:%s not in db", icon_id)
    if not icon_info.get("refered_info"):
        icon_info["refered_info"] = []
    refered_info = {}
    refered_info["id"] = int(model_id)
    refered_info["modelName"] = modelName
    refered_info["modelField"] = icon_field
    icon_info["refered_info"].append(refered_info)
    icon_info.pop("_id")
    ArmoryMongo[appname]["icon"].update(icon_cond, {'$set': icon_info})
    _LOGGER.info("update the id refer info:%s", icon_id)
    if old_id:
        old_icon_id = int(old_id) if not isinstance(old_id, int) else old_id
        old_cond = {"_id": old_icon_id}
        old_icon_info = ArmoryMongo[appname]["icon"].find_one(old_cond)
        if not old_icon_info:
            raise ValueError("icon:%s not in db", old_icon_id)
        if not old_icon_info.get("refered_info"):
            old_icon_info["refered_info"] = []
        if refered_info in old_icon_info["refered_info"]:
            old_icon_info["refered_info"].remove(refered_info)
        old_icon_info.pop("_id")
        ArmoryMongo[appname]["icon"].update(old_cond, {'$set': old_icon_info})
        _LOGGER.info("update the id refer info:%s", old_icon_id)


def inc_icon(appname, modelname, temp_dict):
    icon_fields = ['icon', 'logo']
    for icon_field in icon_fields:
        if temp_dict.get(icon_field):
            icon_dict = temp_dict[icon_field]
            model_id = temp_dict.get('id')
            icon_id = icon_dict.get('id')
            _LOGGER.debug(
                'modelname:%s, icon_id:%s, model_id:%s, icon_field:%s',
                modelname, icon_id, model_id, icon_field)
            refered_icon(appname, modelname, icon_id, model_id, icon_field)


def mod_icon(appname, modelname, temp_dict, old_item):
    icon_fields = ['icon', 'logo']
    for icon_field in icon_fields:
        model_id = temp_dict.get('id')
        if temp_dict.get(icon_field):
            icon_dict = temp_dict.get(icon_field)
            _LOGGER.info(icon_dict)
            new_icon_id = icon_dict.get('id')
            old_icon_dict = old_item.get(icon_field)
            if not old_icon_dict:
                continue
            old_icon_id = old_icon_dict.get('id', None)
            _LOGGER.info(old_icon_dict)
            if new_icon_id == old_icon_id:
                continue
            refered_icon(
                appname, modelname, new_icon_id, model_id, icon_field,
                old_icon_id)


def fetch_icon_url(appname, icon_dict={}, server_name="local", force=False):
    '''
    if the icon is not upload, upload the icon first and return the
    download url
    if force is true, upload icon derectly
    '''
    if not icon_dict:
        return ""
    else:
        icon_id = icon_dict.get("id")
        icon_info = ArmoryMongo[appname]['icon'].find_one({'_id': icon_id})
        if not icon_info:
            return ''
        url_name = "%s_url" % server_name
        if force:
            upload_icon_to_server(server_name, appname, [icon_id])
        icon_new_info = ArmoryMongo[appname]['icon'].find_one({'_id': icon_id})
        return icon_new_info.get(url_name)

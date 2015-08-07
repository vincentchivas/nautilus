# -*- coding: utf-8 -*-
import logging
import simplejson
import requests
from functools import wraps
from cm_console.api import request
from pylon.frame import make_response

from armory.marine.json_rsp import json_response_error
from cm_console.settings import MONGO_CONFIG, MODELS, AUTH_SERVICE_HOST
from armory.marine.respcode import PARAM_ERROR


_LOGGER = logging.getLogger(__name__)


def check_url_params(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # check appname args
        appname = kwargs.get("appname")

        if appname not in MONGO_CONFIG:
            return json_response_error(
                PARAM_ERROR, msg="appname error, check url")

        # check modelName args
        modelName = kwargs.get("modelname")
        if modelName:
            if modelName not in MODELS:
                return json_response_error(
                    PARAM_ERROR, msg="invalid modelname: %s" % modelName)

        # check modelName args
        mid = kwargs.get("item_id")
        if mid:
            try:
                mid = int(mid)
            except ValueError:
                return json_response_error(PARAM_ERROR, msg="id format error")
        return func(*args, **kwargs)
    return wrapper


def savelog(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        resp = make_response(func(*args, **kwargs))
        raw_data = resp.data
        res_d = simplejson.dumps(raw_data)
        urlpath = request.path
        sid = request.cookies.get('sessionid')
        # if not sid:
        #    return json_response_error(PERMISSION_DENY, msg='sid is not find')
        try:
            headers = {
                "Content-type": "application/json", "Accept": "text/plain"}
            url = 'http://%s/auth/loginfo' % AUTH_SERVICE_HOST
            params = {'sid': sid, 'url': urlpath, 'data': res_d}
            res = requests.post(
                url, data=simplejson.dumps(params), headers=headers)
            if res.status_code >= 200 and res.status_code <= 300:
                res_data = res.json()
                data_info = res_data['data']
                if data_info:
                    data_status = data_info.get('status')
                    if data_status and data_status != 0:
                        _LOGGER.error(
                            'save user log error, error code %d' % data_status)
                        #  return json_response_error(
                        #     PERMISSION_DENY, msg='sid is not exist in db')
                else:
                    _LOGGER.info('response data is empty')
            else:
                _LOGGER.error('reponse error from auth service')
        except Exception, e:
            _LOGGER.error(e)
        finally:
            return resp
    return decorated_function

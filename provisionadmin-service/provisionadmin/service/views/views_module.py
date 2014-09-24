# -*-coding: utf-8 -*-
"""
@author: yqyu
@date: 2014-07-15
@description: Get module list of strings
"""

from provisionadmin.utils.json import json_response_error, json_response_ok
from provisionadmin.utils.respcode import PARAM_REQUIRED, DATA_ERROR, \
    METHOD_ERROR
from provisionadmin.model.i18n import LocalizationModules
from provisionadmin.decorator import check_session, exception_handler


@exception_handler()
@check_session
def get_modules(request, user):
    """
    Get module list of strings by appname & appversion
    Parameters:
        -appname: package name,
        -appversion: package version
    Return:
        -1. found module data
        {
            "status": 0,
            "data":{
                ...
            }
        }
        -2. not found module date
        {
            "status": 4,
            "data":{
                ...
            }
         }
        -3. error http method
        {
            "status": 11,
            "data":{
                ...
            }
        }
    """
    if request.method == 'GET':
        data = request.GET

        appname = data.get("appname")
        if not appname:
            return json_response_error(
                PARAM_REQUIRED, msg="parameter 'appname' invalid")
        appversion = data.get("appversion")
        if not appversion:
            return json_response_error(
                PARAM_REQUIRED, msg="parameter 'appversion' invalid")
        # name = data.get("name")

        modules = LocalizationModules.get_by_app(appname, appversion)
        if not modules:
            return json_response_error(DATA_ERROR, msg='not found modules')

        return json_response_ok(modules)
    else:
        return json_response_error(METHOD_ERROR, msg="http method wrong")

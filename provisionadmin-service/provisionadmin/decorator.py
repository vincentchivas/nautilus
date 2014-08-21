# -*- coding: utf-8 -*-

import datetime
from django.http import HttpResponse
# from django.conf import settings
import logging
# from django.http import HttpResponse
from django.conf import settings
from provisionadmin.db import user
from provisionadmin.utils import json, respcode, exception


EXCEPTION_DEBUG = settings.EXCEPTION_DEBUG and settings.DEBUG
AUTH_DEBUG = settings.DEBUG and settings.AUTH_DEBUG
logger = logging.getLogger('provisionadmin')

EXCEPTION_CODE_PAIRS = (
    (respcode.AUTH_ERROR, exception.AuthFailureError,),
    (respcode.DB_ERROR, exception.DbError,),
    (respcode.DATA_ERROR, exception.DataError,),
    (respcode.DATA_ERROR, exception.UniqueCheckError,),
    (respcode.PARAM_ERROR, exception.ParamsError,),
    (respcode.IO_ERROR, IOError,),
    (respcode.UNKNOWN_ERROR, exception.UnknownError,),
)


def _get_respcode_of_exception(e):
    e_type = type(e)
    for code, exception_type in EXCEPTION_CODE_PAIRS:
        if e_type == exception_type:
            return code
    else:
        return respcode.UNKNOWN_ERROR


def exception_handler(as_json=True):
    """
    catch the exception and return specified respcode
    """
    def e_wrapper(func):
        def wrapper(request, *args, **kwargs):
            try:
                if request.method == 'OPTIONS':
                    return json.json_response_ok({}, 'can cross-domain')
                return func(request, *args, **kwargs)
            except Exception as e:
                logger.exception(e)
                if EXCEPTION_DEBUG:
                    raise e
                else:
                    if as_json:
                        return json.json_response_error(
                            _get_respcode_of_exception(e), {}, e.message)
                    else:
                        return HttpResponse(e.message)
        return wrapper
    return e_wrapper


def check_session(func):
    '''
     check user session
    '''
    def wrapper(req, *args, **kv):
        check = False
        session_key = req.session.session_key
        if session_key:
            item = user.find_session(
                {
                    'session_key': session_key,
                    'expire_date': {
                        '$gt': datetime.datetime.now()
                    }
                }
            )
            if item:
                uid = req.session.get('uid')
                if uid:
                    u = user.find_one_user({'_id': uid})
                    if u.is_active:  # 可以加上鉴权
                        check = True
        if check or AUTH_DEBUG:
            return func(req, *args, **kv)
        else:
            return json.json_response_error(
                respcode.AUTH_ERROR, {}, 'auth error')
    return wrapper

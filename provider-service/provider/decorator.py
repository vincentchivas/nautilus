# -*- coding: utf-8 -*-

from django.http import HttpResponse
import logging
from django.conf import settings
from provisionadmin.utils import json, respcode, exception


EXCEPTION_DEBUG = settings.EXCEPTION_DEBUG and settings.DEBUG
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

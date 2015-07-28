# -*- coding:utf-8 -*-
import logging
import simplejson
import types
from armory.marine.exception import ParamError, UnknownError
from armory.marine.util import now_timestamp


_LOGGER = logging.getLogger(__name__)
PARAM_OPTION_LIST = ["need", "noneed", "option"]


def _conv(func):
    '''
    internal func for converting data type
    '''
    def wrapper(*args, **kwargs):
        if func == bool:
            return bool(int(*args, **kwargs))
        return func(*args, **kwargs)
    return wrapper


def get_valid_params(query_dict, keys):
    '''
    get valid params by params rule
    '''
    try:
        result = {}
        for key in keys:
            paras = key.split('&')
            (param_key, param_option,
             param_type, default_value) = tuple(
                paras) + (None,) * (4 - len(paras))
            if not param_key or param_option not in PARAM_OPTION_LIST:
                # invalid config for parameter %key%
                continue
            param_value = query_dict.get(param_key)
            if param_value is None or param_value is '':
                if param_option == 'need':
                    msg = param_key + ' is required'
                    raise ParamError(msg)
                if param_option == 'noneed':
                    # the key will not put into the result
                    continue
                if param_option == 'option':
                    if default_value is not None:
                        param_value = _conv(eval(param_type))(default_value)
                    else:
                        if param_type == 'time':
                            param_value = now_timestamp()
                        elif param_type == 'str':
                            param_value = ''
                        else:
                            param_value = None
                        # if default_value is None
            else:
                try:
                    if param_type.startswith('list') and param_type != 'list_dict':
                        if param_value:
                            sub_type = param_type.split('_')[1]
                            param_value = [_conv(eval(sub_type))(it) for it in param_value]
                    elif param_type == "json":
                        val = simplejson.loads(param_value)
                        if not isinstance(val, types.DictType):
                            msg = param_key + " param value error"
                            raise ParamError(msg)
                    else:
                        if param_type not in ["str", "list_dict", "dict", "time"]:
                            param_value = _conv(eval(param_type))(param_value)
                except Exception as e:
                    msg = param_key + " param value error"
                    raise ParamError(msg)
            result[param_key] = param_value
        return result
    except Exception as e:
        _LOGGER.exception(e)
        if not isinstance(e, ParamError):
            raise UnknownError('get param error')
        else:
            _LOGGER.warn('check parameter exception![%s]' % e.msg)
            raise e

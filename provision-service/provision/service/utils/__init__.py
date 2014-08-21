# Copyright (c) 2011 Baina Info Inc. All rights reserved.
# author:kunli
# date:2011-11-19
# email:kunli@bainainfo.com
from django.conf import settings
from provision.service.errors import parameter_error

_CLIENT_ARGS = settings.CLIENT_ARGS

_FIELDS_LASTMODIFIED = {
    '_id': 0,
    'timestamp': 1
}


def _normalize(value):
    if value and isinstance(value, basestring):
        value = value.lower()
    return value


def get_optional_parameter(request, name, default=None, formatter=None):
    value = request.GET.get(name, default)
    if value and formatter:
        try:
            value = formatter(value)
        except:
            return None, parameter_error(request, name) if default is None else default
    return value, None


def _convert_func(func):
    def wrapper(*args, **kwargs):
        if func == bool:
            return bool(int(*args, **kwargs))
        return func(*args, **kwargs)
    return wrapper


def _get_parameter(request, query_dict, name, convert_func=None, required=True, default=None, alternative_name=None):
    item = query_dict.get(name, None)
    if item is None and alternative_name is not None:
        item = query_dict.get(alternative_name, None)
    if item is None and default is not None:
        item = default

    if required and item is None:
            return parameter_error(request, name)
    if convert_func and item is not None:
            try:
                item = _convert_func(convert_func)(item)
            except:
                return parameter_error(request, name)
    return item


def get_parameter_GET(request, name, convert_func=None, required=True, default=None, alternative_name=None):
    return _get_parameter(request, request.GET, name, convert_func=convert_func, required=required, default=default, alternative_name=alternative_name)


def get_parameter_POST(request, name, convert_func=None, required=True, default=None, alternative_name=None):
    return _get_parameter(request, request.POST, name, convert_func=convert_func, required=required, default=default, alternative_name=alternative_name)


def get_parameter_META(request, name, convert_func=None, required=True, default=None, alternative_name=None):
    return _get_parameter(request, request.META, name, convert_func=convert_func, required=required, default=default, alternative_name=alternative_name)

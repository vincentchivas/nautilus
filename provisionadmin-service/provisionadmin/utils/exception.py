# -*- coding: utf-8 -*-
"""
@author: zhhfang
@date: 2014-07-15
@description: define the exceptions
"""


class ParamsError(Exception):
    pass


class AuthFailureError(Exception):
    pass


class UnknownError(Exception):
    pass


class UniqueCheckError(ValueError):
    pass


class DbError(Exception):
    pass


class DataError(ValueError):
    pass

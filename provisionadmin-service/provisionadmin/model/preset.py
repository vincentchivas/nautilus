# coding: utf-8
from provisionadmin.model.base import ModelBase


def config(model_name):
    ATTRS = {}
    ATTRS["db"] = "i18n"
    ATTRS["collection"] = "bookmark"
    ATTRS["required"] = ("name", "url")
    ATTRS["optional"] = (("time", "123"),)
    ATTRS["unique"] = (("name"), )
    return type(model_name, (ModelBase,), ATTRS)

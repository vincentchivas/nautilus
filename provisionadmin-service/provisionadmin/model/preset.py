# coding: utf-8
from provisionadmin.model.base import ModelBase

ATTRS = {}
MODEL_NAME = ""


def config(model_name):
    ATTRS["name"] = "name"
    ATTRS["age"] = "age"
    MODEL_NAME = model_name


CLASS_NAME = type(MODEL_NAME, (ModelBase,), ATTRS)

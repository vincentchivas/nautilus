# coding: utf-8
from provisionadmin.model.base import ModelBase
from provisionadmin.settings import MODELS


def config(model_name):
    ATTRS = MODELS[model_name]
    return type(model_name, (ModelBase,), ATTRS)

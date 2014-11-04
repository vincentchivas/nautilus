# coding: utf-8
from provisionadmin.model.base import ModelBase
from provisionadmin.settings import MODELS


def classing_model(model_name):
    '''
    type method can be used as a metaclass funtion, when a string "model_name"
    came, it can be return the class
    '''
    if MODELS.get(model_name):
        ATTRS = MODELS.get(model_name)
        return type(model_name, (ModelBase,), ATTRS)
    else:
        return None

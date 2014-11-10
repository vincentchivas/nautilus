# coding: utf-8
from provisionadmin.model.base import ModelBase
from provisionadmin.settings import MODELS
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


@classmethod
def get_rules():
    return "get"


def classing_model(model_name):
    '''
    type method can be used as a metaclass funtion, when a string "model_name"
    came, it can be return the class
    '''
    if MODELS.get(model_name):
        ATTRS = MODELS.get(model_name)
        if model_name== "bookmarkfolder":
            ATTRS["get_rules"] = get_rules
        return type(model_name, (ModelBase,), ATTRS)
    else:
        return None

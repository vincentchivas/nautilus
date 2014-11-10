# coding: utf-8
from provisionadmin.model.base import ModelBase
from provisionadmin.settings import MODELS
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


@classmethod
def get_rules(cls, conn):
    item = {}
    engine = create_engine(conn)
    Session = sessionmaker(bind=engine)
    sess = Session()
    # sess.execute("create database abc")
    # sess.execute("show databases")
    print sess.execute("select * from persons where uid=1").first()
    person = sess.execute(
        ("select * from persons where uid=:id", {"id": 1}).first()
    # return a tuple (1, "anel")
    print person


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

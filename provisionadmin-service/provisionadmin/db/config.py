'''
Created on Jul 8, 2014

@author: xshu
'''
import logging
from pymongo import Connection
from provisionadmin.db.mongodb_proxy import MongoProxy
from provisionadmin import settings


_LOGGER = logging.getLogger(__name__)

RAW_CONNS = {}
CONNS = {}
DBS = {}


def _config_db(conn_str):
    assert conn_str

    try:
        _raw_conn = Connection(host=conn_str,
                               max_pool_size=20,
                               safe=True,
                               network_timeout=5)
        return _raw_conn
    except Exception, e:
        _LOGGER.critical(e)
        raise e


def config(module):
    dbname = module.__name__.split('.')[-1][:-2]
    # from userdb module get name user
    db_config = settings.DB_SETTINGS
    if dbname in db_config:
        raw_conn = _config_db(db_config[dbname].get('host'))
        RAW_CONNS[dbname] = raw_conn
        conn = MongoProxy(raw_conn, logger=_LOGGER, wait_time=10)
        CONNS[dbname] = conn
        DBS[dbname] = conn[db_config[dbname].get('name')]
        module._db = DBS[dbname]
# eg: from config {"user": {"host": "xxhost", "name": "xxcoll"}} we can get
# raw_conn_user ---> user_conn ---> USER_DB

raw_conn_id = _config_db(settings.DB_SETTINGS['id'].get('host'))
raw_conn_user = _config_db(settings.DB_SETTINGS['user'].get('host'))
raw_conn_preset = _config_db(settings.DB_SETTINGS['preset'].get('host'))
raw_conn_trans = _config_db(settings.DB_SETTINGS['i18n'].get('host'))

id_conn = MongoProxy(raw_conn_id, logger=_LOGGER, wait_time=10)
ID_DB = id_conn[settings.DB_SETTINGS['id'].get('name')]

user_conn = MongoProxy(raw_conn_user, logger=_LOGGER, wait_time=10)
USER_DB = user_conn[settings.DB_SETTINGS['user'].get('name')]

preset_conn = MongoProxy(raw_conn_preset, logger=_LOGGER, wait_time=10)
PRESET_DB = user_conn[settings.DB_SETTINGS['preset'].get('name')]

trans_conn = MongoProxy(raw_conn_trans, logger=_LOGGER, wait_time=10)
TRANS_DB = user_conn[settings.DB_SETTINGS['i18n'].get('name')]

import sys
import traceback
import re
import logging
from pymongo.connection import Connection
from dolphinopadmin.utils import ReadOnlyPropertyTable

from pymongo import ReplicaSetConnection, ReadPreference, Connection
from pymongo import DESCENDING, ASCENDING

logger = logging.getLogger('dolphinopadmin.admin')

_connections = {}

_CONN_RE = re.compile(
    r"(?P<hosts>(?P<host>[A-Z0-9_.-]+)(?P<portpart>:(?P<port>\d+))?(?P<repls>(?P<repl>,[A-Z0-9_.-]+(:\d+)?)*))/(?P<db>\w+)", re.IGNORECASE)


def parse_conn_string(conn_str):
    m = _CONN_RE.search(conn_str)
    if m:
        if m.group('repls'):
            host = m.group('hosts')
            port = None
        else:
            host = m.group('host')
            port = int(m.group('port')) if m.group('port') else 27017
        db = m.group('db')
        return ReadOnlyPropertyTable({
            'server': host,
            'port': port,
            'db': db
        })
    else:
        raise ValueError('The connection string "%s" is incorrect.' % conn_str)


def connect(host, port=None):
    '''
    Connect to the database.
    '''
    assert host, 'host of the database server may not be null.'
    global _connections
    key = (host, port or 27017)
    conn = None
    if key in _connections:
        conn = _connections[key]
    else:
        conn = Connection(host, port, slave_okay=True)
        _connections[key] = conn
    return conn


def disconnect(host, port=None):
    '''
    Connect from the database.
    '''
    assert host, 'host of the database server may not be null.'
    global _connections
    key = (host, port or 27017)
    if key in _connections:
        conn = _connections[key]
        conn.disconnect()
        del _connections[key]


class Remotedb(object):

    def __init__(self, env):
        self.env = env
        self._config(env)

    def _config(self, env):
        pass

    def _save(self, collection, items, query_keys):
        logger.debug('REMOTEDB--SAVE: %s,%s,%s' %
                     (collection, len(items), query_keys))
        error_info = []
        for item in items:
            try:
                cond = {}
                for key in query_keys:
                    cond[key] = item[key]
                collection.update(cond, item, True)
            except Exception:
                trace_stack = '\n'.join(
                    traceback.format_exception(*sys.exc_info()))
                logger.error('REMOTEDB--SAVE FAILED:%s %s,STACK:%s' %
                             (collection, cond, trace_stack))
                error_info.append('upload item: %s  failed' % cond)
        return '\n'.join(error_info) if error_info else None

    def _remove(self, collection, items, query_keys):
        logger.debug('REMOTEDB--REMOVE: %s,%s,%s' %
                     (collection, len(items), query_keys))
        error_info = []
        for item in items:
            try:
                cond = {}
                for key in query_keys:
                    cond[key] = item[key]
                item_in_db = collection.find_one(cond)
                if item_in_db:
                    collection.remove(cond)
                else:
                    error_info.append('item: %s is not in remote db' % cond)
            except Exception:
                trace_stack = '\n'.join(
                    traceback.format_exception(*sys.exc_info()))
                logger.error('REMOTEDB--REMOVE FAILED:%s %s,STACK:%s' %
                             (collection, cond, trace_stack))
                error_info.append('remove item: %s  failed' % item['title'])
        return '\n'.join(error_info) if error_info else None


class IncrementalId(object):

    """implement incremental id for collection in mongodb
    """

    def __init__(self, db):
        self.db = db
        self.colls = {}

    def _ensure_next_id(self, coll_name):
        """ensure next_id item in collection ,if not, next_id method will throw exception rasie by pymongo"""
        cond = {'_id': coll_name}
        id_info = self.db.ids.find_one(cond)
        if not id_info:
            self.db.ids.insert({'_id': coll_name, 'seq': 0L})

    def next_id(self, coll):
        """get next increment id and increase it """
        self._ensure_next_id(coll)
        cond = {'_id': coll}
        update = {'$inc': {'seq': 1L}}
        self.db.update(cond, update, upsert=True)
        coll = self.db.find_one(cond)
        return coll['seq']


def config(module, servers):
    '''
    Configure a data access module.
    '''
    module._db = {}
    for key, value in servers.iteritems():
        try:
            conn = connect(value['host'], value['port'])
            module._db[key] = conn[value['db']]
        except Exception, e:
            logger.error(e)


def cursor_to_array(cursor):
    return [i for i in cursor]


class MongodbStorage(object):
    _db = None
    ORDER_DESC = DESCENDING
    ORDER_ASC = ASCENDING
    DEFAULT_ORDER = [("order", ORDER_ASC)]

    def __init__(self, conn_str, db_name):
        try:
            if conn_str.find("replicaSet") == -1:
                _conn = Connection(conn_str,
                                   max_pool_size=30,
                                   safe=True,
                                   read_preference=ReadPreference.SECONDARY_ONLY)
            else:
                _conn = ReplicaSetConnection(conn_str,
                                             max_pool_size=30,
                                             safe=True,
                                             read_preference=ReadPreference.SECONDARY_ONLY)
            self._db = _conn[db_name]
        except Exception, e:
            logger.exception('Can not connect to mongodb: %s', e)
            raise e

    def inser_item(self, table, item):
        eval('self._db.%s.insert(%s)' % (table, item))

    def delete_item(self, table, cond):
        eval('self._db.%s.remove(%s)' % (table, cond))

    def upsert_item(self, table, cond, item, upsert=False, multi=False):
        eval("self._db.%s.update(%s, {'$set': %s}, upsert=%s, multi=%s)" %
             (table, cond, item, upsert, multi))

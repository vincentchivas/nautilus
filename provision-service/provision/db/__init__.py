import re
import logging
from time import time
from pymongo.connection import Connection

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
        return {
            'server': host,
            'port': port,
            'db': db
        }
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

perf_logger = logging.getLogger('dolphinop.db')


def dbperf_logging(func):
    """
    Record the performance of each method call.

    Also catches unhandled exceptions in method call and response a 500 error.
    """
    def pref_logged(*args, **kwargs):
        argnames = func.func_code.co_varnames[:func.func_code.co_argcount]
        fname = func.func_name
        msg = 'DB - -> %s(%s)' % (fname, ','.join('%s=%s' %
                                                  entry for entry in zip(argnames, args) + kwargs.items()))
        startTime = time()
        perf_logger.info('%s -> Start time: %d.' % (msg, 1000 * startTime))
        retVal = func(*args, **kwargs)
        perf_logger.info('%s -> End Start time: %d.' % (msg, 1000 * startTime))
        endTime = time()
        perf_logger.debug('%s <- %s ms.' % (msg, 1000 * (endTime - startTime)))
        return retVal
    return pref_logged


def cursor_to_array(cursor, start=None, limit=None):
    if start >= 0 and limit >= 0:
        items = []
        le = 0
        for i, item in enumerate(cursor):
            if i < start:
                continue
            items.append(item)
            le += 1
            if le >= limit:
                break
    else:
        items = [i for i in cursor]
    return items


def config(module, server, port=None, db=None):
    '''
    Configure a data access module.
    '''
    assert server and db, 'Either "server" or "db" may not be None.'
    conn = connect(server, port)
    module._db = conn[db]
    if hasattr(module, '_INDEXES'):
        ensure_indexes(module, module._INDEXES)


def ensure_index(module, collection_name, indexes):
    '''
    Ensure a data access module's collection indexes.
    '''
    collection = module._db[collection_name]
    for index in indexes:
        collection.ensure_index(index)


def ensure_indexes(module, index_table):
    '''
    Ensure a data access module's indexes.
    '''
    for collection, indexes in index_table.items():
        ensure_index(module, collection, indexes)

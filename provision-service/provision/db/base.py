from time import time
from functools import wraps
from pymongo import ReplicaSetConnection, ReadPreference, Connection
from pymongo import DESCENDING, ASCENDING
from provision.service.utils.common_op import get_logger
from django.conf import settings

LOGGER = get_logger('db')


def dbperf_logging(func):
    """
    Record the performance of each method call.

    Also catches unhandled exceptions in method call and response a 500 error.
    """
    @wraps(func)
    def pref_logged(*args, **kwargs):
        argnames = func.func_code.co_varnames[:func.func_code.co_argcount]
        fname = func.func_name
        msg = 'DB - -> %s(%s)' % (fname, ','.join('%s=%s' %
                                                  entry for entry in zip(argnames, args) + kwargs.items()))
        startTime = time()
        LOGGER.info('%s -> Start time: %d.' % (msg, 1000 * startTime))
        retVal = func(*args, **kwargs)
        LOGGER.info('%s -> End Start time: %d.' % (msg, 1000 * startTime))
        endTime = time()
        LOGGER.debug('%s <- %s ms.' % (msg, 1000 * (endTime - startTime)))
        return retVal

    return pref_logged


def cursor_to_list(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        retval = func(*args, **kwargs)
        return [i for i in retval]

    return wrapper


class MongodbStorage(object):
    _db = None
    ORDER_DESC = DESCENDING
    ORDER_ASC = ASCENDING
    DEFAULT_ORDER = [("order", ORDER_ASC)]

    def __init__(self):
        conn_str = settings.DB_CONN
        db_name = 'dolphinop'
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
            LOGGER.exception('Can not connect to mongodb: %s', e)
            raise e

    @dbperf_logging
    @cursor_to_list
    def get_item(self, cond, field=None, table=None):
        if not table:
            table = self.table
        return eval('self._db.%s.find(%s,%s)' % (table, cond, field))

    @dbperf_logging
    def delete_item(self, cond, table=None):
        if not table:
            table = self.table
        return eval('self._db.%s.remove(%s)' % (table, cond))

    @dbperf_logging
    def upsert_item(self, cond, item=None, upsert=False, multi=False, table=None):
        if not table:
            table = self.table
        if not item:
            return eval('self._db.%s.insert(%s)' % (table, cond))
        else:
            return eval("self._db.%s.update(%s, {'$set': %s}, upsert=%s, multi=%s)" % (table, cond, item, upsert, multi))

    @dbperf_logging
    @cursor_to_list
    def get_paging_items(self, cond, field=None, page=1, page_size=30, table=None):
        if not table:
            table = self.table
        return eval('self._db.%s.find' % table)(cond, field).sort([('order', self.ORDER_ASC)]).skip((page - 1) * page_size).limit(page_size)

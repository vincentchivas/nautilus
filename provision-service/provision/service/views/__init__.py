import httplib
import json

from django.utils import simplejson
from django.http import HttpResponse, HttpResponseNotFound, \
    HttpResponseServerError

from bson.son import SON
from functools import wraps
from pymongo.cursor import Cursor
from pymongo import ReplicaSetConnection, ReadPreference, Connection
from pymongo import DESCENDING, ASCENDING


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
            self.db.ids.insert({'_id': coll_name, 'seq': 1L})

    def next_id(self, coll):
        """get next increment id and increase it """
        if coll not in self.colls:
            self._ensure_next_id(coll)
        cond = {'_id': coll}
        update = {'$inc': {'seq': 1L}}
        son = SON([('findandmodify', 'ids'), ('query', cond),
                  ('update', update), ('new', True)])
        seq = self.db.command(son)
        return seq['value']['seq']


def cursor_to_list(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        retval = func(*args, **kwargs)

        if isinstance(retval, Cursor):
            retval = [x for x in retval]
            map(remove_id, retval)

        elif isinstance(retval, dict) and 'results' in retval and 'total' in retval:
            if isinstance(retval['results'], Cursor):
                retval['results'] = [x for x in retval['results']]
        return retval

    def remove_id(tmp_dict):
        del tmp_dict['_id']

    return wrapper


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
            raise e

    def delete_item(self, table, cond):
        eval('self._db.%s.remove(%s)' % (table, cond))

    def upsert_item(self, table, cond, item, upsert=False, multi=False):
        eval("self._db.%s.update(%s, {'$set': %s}, upsert=%s, multi=%s)" %
             (table, cond, item, upsert, multi))


DEFAULT_SOURCE = 'ofw'
ALL_FLAG = 'all_condition'
OTHER = 'other_condition'
OPERATORS = ['00', '01', '02', '03']
ALL_WEIGHT = 1
MATCH_WEIGHT = 100


def json_response(func):
    def json_responsed(request, *args, **kwargs):
        status_code = httplib.OK
        retval = func(request, *args, **kwargs)
        content = json.dumps(retval, skipkeys=True, ensure_ascii=False)
        response = HttpResponse(
            content, content_type='application/json; charset=utf-8', status=status_code)
        response['Access-Control-Allow-Origin'] = "*"
        return response
    return json_responsed


def response_json(obj):
    content = simplejson.dumps(obj, ensure_ascii=False)
    response = HttpResponse(
        content, content_type='application/json; charset=utf-8')
    response['Access-Control-Allow-Origin'] = "*"
    '''
    if isinstance(content, unicode):
        response['Content-Length'] = len(content.encode('utf-8'))
    else:
        response['Content-Length'] = len(content)
    '''
    return response


def error404(request):
    return HttpResponseNotFound(""""
Sorry, we can't find what you want...
""")


def error500(request):
    return HttpResponseServerError("""
Sorry, we've encounter an error on the server.<br/> Please leave a feedback <a href="/feedback.htm">here</a>.
""", content_type="text/html; charset=utf-8")

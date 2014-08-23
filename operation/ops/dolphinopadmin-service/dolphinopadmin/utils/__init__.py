import datetime
import time
try:
    from pymongo.son import SON
except ImportError:
    from bson.son import SON
import pytz
from django.utils import simplejson
from django.http import HttpResponse
import hashlib

ONE_DAY = datetime.timedelta(days=1)
timezone = pytz.timezone('Asia/Shanghai')


def date_part(date):
    '''
    Return the date part of a given day.
    '''
    if date:
        return date.replace(hour=0, minute=0, second=0, microsecond=0)
    return None


def now():
    '''
    Return now.
    '''
    return datetime.datetime.now()


def today():
    '''
    Return the date part of today.
    '''
    return date_part(datetime.datetime.now())


def tomorrow():
    '''
    Return the date part of tomorrow.
    '''
    return today() + ONE_DAY


def yesterday():
    '''
    Return the date part of yesterday.
    '''
    return today() - ONE_DAY


def lastmonth():
    '''
    Return the date list of last 30 days.
    '''
    days = []
    # for i in range(30):
    for i in range(1, 30):
        pre = datetime.timedelta(days=i)
        days.append(today() - pre)
    return days


def utc2local(dt):
    dt = dt.replace(tzinfo=pytz.utc)
    local = dt.astimezone(timezone)
    local = local.replace(tzinfo=None)
    return local

def toTimestampMs(dt):
    result = 1000 * long(time.mktime(dt.timetuple()))
    return result

def dict2PropertyTable(d, recursive=True):
    '''
    Converts an dict to PropertyTable.

    If the give paremeter is not a dict, it is returned directly.
    '''
    if d:
        if isinstance(d, dict) and not isinstance(d, PropertyTable):
            d = PropertyTable(d)
        if recursive:
            if isinstance(d, dict):
                for k in d:
                    d[k] = dict2PropertyTable(d[k])
            elif hasattr(d, '__iter__'):
                d = map(dict2PropertyTable, d)
    return d


class ReadOnlyDict(dict):

    '''
    A dictionary that is read-only.
    '''

    def mutatableCopy(self):
        '''
        Return a mutable copy of this property table.
        '''
        return dict(self)

    def __setattr__(self, name, value):
        pass

    def __delattr__(self, name):
        pass

    def __setitem__(self, key, value):
        pass

    def __delitem__(self, key):
        pass


class PropertyTable(dict):

    '''
    A property table that allows create/get/set property that is not in the property list by using attribute syntax.
    '''

    @classmethod
    def fromJson(
            s, encoding=None, cls=None, object_hook=None, parse_float=None,
            parse_int=None, parse_constant=None, object_pairs_hook=None,
            use_decimal=False, **kw):
        '''
        Creates an PropertyTable from a JSON string.
        '''
        if s:
            dict = simplejson.loads(
                s, encoding=encoding, cls=cls, object_hook=object_hook, parse_float=parse_float,
                parse_int=parse_int, parse_constant=parse_constant, object_pairs_hook=object_pairs_hook, use_decimal=use_decimal, **kw)
            return PropertyTable(dict)
        else:
            return PropertyTable()

    def __getattr__(self, name):
        '''
        Delegate self.name to self[name]. If name not in self, None is returned.
        '''
        if name in self:
            return self[name]
        else:
            return self.getdefault(name)

    def getdefault(self, name):
        '''
        Retrieve the default value of a attribute.
        '''
        base = self.__dict__
        if '__defaults__' in base:
            defaults = base['__defaults__']
            if name in defaults:
                return defaults[name]
        return None

    def setdefault(self, name, value):
        '''
        Retrieve the default value of a attribute.
        '''
        base = self.__dict__
        if '__defaults__' in base:
            defaults = base['__defaults__']
        else:
            defaults = {}
            base['__defaults__'] = defaults
        defaults[name] = value

    def __setattr__(self, name, value):
        '''
        Delegate self.name = value to self[name] = value
        '''
        self[name] = value

    def __delattr__(self, name):
        '''
        Delegate the 'remove' action.
        '''
        del self[name]

    def readOnlyCopy(self):
        '''
        Return a read-only copy of this property table.
        '''
        return ReadOnlyPropertyTable(self)

    def tojson(self, skipkeys=False, ensure_ascii=True, check_circular=True,
               allow_nan=True, cls=None, indent=None, separators=None,
               encoding='utf-8', default=None, use_decimal=False, **kw):
        '''
        Convert the property table to a JSON string.
        '''
        return simplejson.dumps(self, skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular, allow_nan=allow_nan, cls=cls, indent=indent, separators=separators, encoding=encoding, default=default, use_decimal=use_decimal, **kw)


class ReadOnlyPropertyTable(PropertyTable):

    '''
    A read-only property table which attributes or properties can not be changed.
    '''

    def mutatableCopy(self):
        '''
        Return a mutable copy of this property table.
        '''
        return PropertyTable(self)

    def setdefault(self, name, value):
        pass

    def __setattr__(self, name, value):
        pass

    def __delattr__(self, name):
        pass

    def __setitem__(self, key, value):
        pass

    def __delitem__(self, key):
        pass


class LastModified(object):

    """implement last modified ability for track  collection modified  date
    """

    def __init__(self, db):
        self.db = db
        self.items = {}

    def _ensure_last_modified(self, item):
        """ensure item for lastModifed collection specified initilized, if not update_last_modified will throw exception raise by pymongo"""
        cond = {'_id': item}
        last_modified_info = self.db.lastModifieds.find_one(cond)
        if not last_modified_info:
            now = datetime.datetime.utcnow()
            self.db.lastModifieds.insert(
                {'_id': item, 'createTime': now, 'lastModified': now})

    def update_last_modified(self, item):
        """update collection last modified time"""
        if item not in self.items:
            self._ensure_last_modified(item)
        cond = {'_id': item}
        update = {'$set': {'lastModified': datetime.datetime.utcnow()}}
        son = SON([('findandmodify', 'lastModifieds'),
                  ('query', cond), ('update', update), ('new', True)])
        self.db.command(son)

    def get_last_modified(self, item):
        if item not in self.items:
            self._ensure_last_modified(item)
        cond = {'_id': item}
        last_modified_info = self.db.lastModifieds.find_one(cond)
        return last_modified_info

from functools import wraps


def last_modified(last_modified_func):
    def wrapper_func(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'get_last_modified' in kwargs and kwargs['get_last_modified']:
                del kwargs['get_last_modified']
                return last_modified_func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        return wrapper
    return wrapper_func


def dotted_quad_to_num(ip):
    "convert decimal dotted quad string to long integer"

    hexn = ''.join(["%02X" % long(i) for i in ip.split('.')])
    return long(hexn, 16)


def _checkoverflow(val, max_v):
    if abs(val) >= max_v:
        raise Exception('Value %d overflowed.' % val)


def unsigned(v, base=64):
    '''
    Convert a signed integer to unsigned integer of a given base.
    '''
    max_v = 1 << base
    _checkoverflow(v, max_v)
    if v < 0:
        v += max_v
    return v


def hashdigest(s, algorithm=None, hexlify=True):
    '''
    Return hash digest of a given string, using specified algorithm or default hash.
    '''
    if s is None:
        return None
    if isinstance(s, unicode):
        s = s.encode('utf-8')
    if algorithm:
        l = algorithm() if callable(algorithm) else hashlib.new(algorithm)
        l.update(s)
        digest = l.hexdigest() if hexlify else False
    else:
        h = hash(s)
        digest = '%016x' % unsigned(h) if hexlify else h
    return digest


def md5(s, hexlify=True):
    '''
    Return md5 digest of a given string.
    '''
    return hashdigest(s, algorithm=hashlib.md5, hexlify=hexlify)


def sha1(s, hexlify=True):
    '''
    Return sha1 digest of a given string.
    '''
    return hashdigest(s, algorithm=hashlib.sha1, hexlify=hexlify)


class string_with_title(str):

    def __new__(cls, value, title):
        instance = str.__new__(cls, value)
        instance._title = title
        return instance

    def title(self):
        return self._title

    __copy__ = lambda self: self
    __deepcopy__ = lambda self, memodict: self


def response_json(obj):
    content = simplejson.dumps(obj, ensure_ascii=False)
    response = HttpResponse(
        content, content_type='application/json; charset=utf-8')
    '''
    if isinstance(content, unicode):
        response['Content-Length'] = len(content.encode('utf-8'))
    else:
        response['Content-Length'] = len(content)
    '''
    return response

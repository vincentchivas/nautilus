'''
Created on Feb 22, 2013

@author: fli
'''
import logging
from dolphinop.db import connect, cursor_to_array
logger = logging.getLogger('dolphinop.db')

_db = None


DISPLAY_FIELDS = {
    '_id': 0,
    'data': 1,
    'sources': 1,
    'locales': 1,
    'min_version': 1,
}


def config(server, db, port=None):
    # check the server and db.
    assert server and db, 'Either "host" or "db" should not be None'
    global _db
    try:
        conn = connect(server, port)
    except Exception, e:
        logger.debug(e)
    _db = conn[db]


def get_desktops(cond):
    colls = _db.desktops.find(cond, fields=DISPLAY_FIELDS)
    return cursor_to_array(colls)

import logging
from provision.db import connect, cursor_to_array
logger = logging.getLogger('dolphinop.db')

_db = None


DISPLAY_FIELDS = {
    '_id': 0,
    '_meta': 1,
    '_rule': 1,
    'first_created': 1,
    'last_modified': 1,
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


def get_share(cond):
    colls = _db.share.find(cond, fields=DISPLAY_FIELDS)
    return cursor_to_array(colls)

def get_data(cond):
    return get_share(cond)

import logging
from pymongo import DESCENDING
from dolphinop.db import cursor_to_array, dbperf_logging
logger = logging.getLogger('dolphinop.db')

_db = None
DISPLAY_FIELDS = {
    '_id': 0,
    '_rule': 0,
}


@dbperf_logging
def get_update(cond, fields=DISPLAY_FIELDS):
    colls = _db.adblock.find(cond, fields=fields).sort(
        [('last_modified', DESCENDING)])
    return cursor_to_array(colls)

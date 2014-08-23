import logging
from datetime import datetime

_db = None

logger = logging.getLogger("dolphinop.db")

'''
Need to configurate the mongoDB setting first,
or raise an exception
'''


def save_feedback(obj):
    assert _db, 'Dolphin Operation/Feedback database server not correctly configured, review your setting.py.'
    _db.feedbacks_en.save(obj)

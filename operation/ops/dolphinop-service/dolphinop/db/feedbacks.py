# Copyright (c) 2011 Baina Info Inc. All rights reserved.
# @author: Wenyuan Wu
# date:2011-11-16

import logging
from datetime import datetime

_db = None

logger = logging.getLogger("dolphinop.db")

'''
Need to configurate the mongoDB setting first,
or raise an exception
'''


def save_feedback(remote_address, name, contact_info, feedback_type, message, os, locale, product, package, source, version):
    assert _db, 'Dolphin Operation/Feedback database server not correctly configured, review your setting.py.'
    feedback_item = {
        'remote_address': remote_address,
        'name': name,
        'contact_info': contact_info,
        'feedback_type': feedback_type,
        'message': message,
        'os': os,
        'locale': locale,
        'time': datetime.utcnow(),
        'product': product,
        'package': package,
        'source': source,
        'version': version,
        'sync': False,
    }
    _db.feedbacks.save(feedback_item)

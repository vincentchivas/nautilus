# -*- coding:utf-8 -*-
'''
Copyright (c) 2011 Baina Info Inc. All rights reserved.
@Author: Wenyuan Wu
@Date:2011-11-30
'''

import logging
from dolphinop.db import connect

logger = logging.getLogger("dolphinop.db")

_db = None
_navigation = None

'''
Need to configurate the mongoDB setting first,
or raise an exception
'''


def config(server, db, port=None):
    # check the server and db.
    assert server and db, 'Either "host" or "db" should not be None'
    global _db, _navigation
    try:
        conn = connect(server, port)
    except Exception, e:
        logger.debug(e)
    _db = conn[db]
    _navigation = _db['navigations']


def get_navigation(os, local):
    assert _navigation, \
        'Dolphin Operation/navigation database \
            server not correctly configured, review your setting.py.'
    navigation = _navigation.find_one({'os': os, 'local': local})
    return navigation

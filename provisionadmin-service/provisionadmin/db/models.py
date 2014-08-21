# -*- coding: utf-8 -*-
"""
@author: zhhfang
@date: 2014-07-15
@description: config the modules under db to have a _db configured each
"""

from provisionadmin.db.config import config
from provisionadmin.db import i18ndb

print 'init app db'
config(i18ndb)

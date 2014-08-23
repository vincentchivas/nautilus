'''
Copyright (c) 2011 Baina Info Inc. All rights reversed.
@Author: Wenyuan Wu
@Date: 2011-12-01
'''
import logging
import time
from dolphinopadmin.remotedb import connect, Remotedb
from django.conf import settings

logger = logging.getLogger('dolphinopadmin.remotedb')


class Navigationdb(Remotedb):

    def _config(self, env):
        try:
            conn = connect(env['host'], env['port'])
            _db = conn[env['db']]
            self._navigations = _db['navigations']
        except Exception, e:
            logger.error(e)

    def save_navigations(self, items):
        for item in items:
            item['timestamp'] = int(time.time())
        self._save(self._navigations, items, ('name',))

    def remove_navigations(self, items):
        self._remove(self._navigations, items, ('name',))


def _initialize(envs):
    dbs = {}
    for env, env_config in envs.iteritems():
        db = Navigationdb(env_config)
        dbs[env] = db
    return dbs

NAVIGATION_DB = _initialize(settings.ENV_CONFIGURATION)

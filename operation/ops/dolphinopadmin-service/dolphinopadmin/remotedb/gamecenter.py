import logging
from django.conf import settings
from dolphinopadmin.remotedb import MongodbStorage, IncrementalId
db_conf = settings.ENV_CONFIGURATION
db_confs = {}
for env in settings.ENV_CONFIGURATION.keys():
    db_confs[env] = 'mongodb://' + db_conf[env]['domain'] + \
        ':' + str(db_conf[env]['port'])


class GameCenterMongodbStorage(MongodbStorage):

    db_name = "dolphinop"

    def __init__(self):
        pass

    def connect_db(self, conn_str='ec2'):
        conn_str = db_confs[conn_str]
        super(GameCenterMongodbStorage, self).__init__(conn_str, self.db_name)
        self._ids = IncrementalId(self._db)

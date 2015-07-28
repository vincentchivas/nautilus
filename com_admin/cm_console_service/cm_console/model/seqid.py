# -*- coding: utf-8 -*-
import logging
from armory.tank.mongo import ArmoryMongo

_LOGGER = logging.getLogger(__name__)


def get_next_id(appname, id_name):
    seqid_db = ArmoryMongo[appname]
    result = seqid_db.seq_id.find_and_modify(
        {'_id': id_name}, {'$inc': {'seq': 1L}}, upsert=True, new=True)
    return result['seq']

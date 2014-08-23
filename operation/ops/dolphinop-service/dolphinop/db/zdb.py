import logging
from dolphinop.db import cursor_to_array, dbperf_logging

logger = logging.getLogger('dolphinop.db')

_db = None


@dbperf_logging
def delete_item(coll, cond):

    collection = _db[coll]
    collection.remove(cond)


@dbperf_logging
def save_list(coll, cond):
    '''
    Get array data of specified collection.
    '''
    for i, item in enumerate(coll):
        collection = _db[item]
        if not len(cond[i]):
            continue
        assert collection.insert(
            cond[i]), 'insert into promotion error,data:%s' % (cond[i],)

    return True


@dbperf_logging
def update_list(coll, cond, set_files, upsert=False):
    collection = _db[coll]
    collection.update(cond, set_files, upsert=upsert)

    return True


@dbperf_logging
def get_list(coll, cond, fields=None):
    '''
    Get object data of specified collection.
    '''
    collection = _db[coll]
    return collection.find(cond, fields=fields)


@dbperf_logging
def clear_list(coll):
    '''
    Get array data of specified collection.
    '''
    for i, item in enumerate(coll):
        collection = _db[item]
        collection.remove()


@dbperf_logging
def valid_base():
    base_db = _db['promotion_base']
    adver_bank = _db['promotion_bank']
    sid_s = cursor_to_array(
        base_db.find({}, {'_id': 1, 'sid': 1, 'title': 1, 'icon': 1}))
    for i in sid_s:
        _id = i.get('_id')
        sid = i.get('sid', 0)
        title = i.get('title', '')
        icon = i.get('icon', '')
        matchs = adver_bank.find(
            {'$or': [{'sid': sid}, {'title': title}, {'icon': icon}]}, {'_id': 0, 'sid': 0, 'a_uid': 0})
        if matchs.count():
            base_db.update({'_id': _id}, {'$set': matchs[0]})

    return True

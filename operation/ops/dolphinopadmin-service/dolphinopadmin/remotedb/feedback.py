'''
Copyright (c) 2011 Baina Info Inc. All rights reversed.
@Author: Wenyuan Wu
@Date: 2011-11-30
'''
import logging

_db = None

FEEDBACK_FIELDS = {
    '_id': 1,
    'remote_address': 1,
    'message': 1,
    'name': 1,
    'os': 1,
    'locale': 1,
    'time': 1,
    'feedback_type': 1,
    'contact_info': 1,
    'package': 1,
    'source': 1,
    'version': 1
}

FEEDBACK_EN_FIELDS = {
    '_id': 1,
    'remote_address': 1,
    'messages': 1
}

logger = logging.getLogger('dolphinopadmin.remotedb')


def get_feedbacks(server):
    cursor = _db[server].feedbacks.find(
        {'sync': False}, fields=FEEDBACK_FIELDS)
    results = []
    for item in cursor:
        _db[server].feedbacks.update(
            {'_id': item['_id']}, {'$set': {'sync': True}})
        del item['_id']
        results.append(item)
    return results


def get_feedbacks_en(server):
    cursor = _db[server].feedbacks_en.find({'sync': False})
    results = []
    for item in cursor:
        _db[server].feedbacks_en.update(
            {'_id': item['_id']}, {'$set': {'sync': True}})
        del item['_id']
        results.append({
            'remote_address': item.get('remote_address', ''),
            'message': item.get('message', ''),
            'name': 'none',
            'os': 'unknown',
            'locale': item.get('locale', 'en_US'),
            'time': item.get('time', ''),
            'feedback_type': 'feedback',
            'contact_info': item.get('contact_info'),
            'package': 'unknown',
            'source': 'unknown',
            'version': 1
        })
    return results

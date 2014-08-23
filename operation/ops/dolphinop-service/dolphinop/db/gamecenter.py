# Copyright (c) 2011 Baina Info Inc. All rights reserved.
# @author: Chen Qi
# date:2011-11-20
# email:qchen@bainainfo.com

import logging
from dolphinop.db import connect

logger = logging.getLogger('dolphinop.db')

_db = None
_category = None
_feature = None
_hoting = None
_subject = None
_application = None

PLAT_FORM_IPAD = ('iPad_CN', 'iPad_EN')

RELEVANT_APP_NUM = 3


def config(server, db, port=None):
    # check the server and db.
    assert server and db, 'Either "host" or "db" should not be None'
    global _db, _feature, _hoting, _category, _application, _subject
    try:
        conn = connect(server, port)
        _db = conn[db]
        _feature = _db['game_feature']
        _hoting = _db['game_hoting']
        _category = _db['game_category']
        _application = _db['game_application']
        _subject = _db['game_subject']
    except Exception, e:
        logger.error(e)


def package_app_simple_info(app_item):
    app_info = {
        'id': app_item['id'],
        'title': app_item['title'],
        'icon': app_item['icon'],
        'download_url': app_item['download_url'],
    }
    return app_info


def package_app_detail_info(app_item):
    app_info = {
        'id': app_item['id'],
        'title': app_item['title'],
        'icon': app_item['icon'],
        'app_rating': app_item['app_rating'],
        'app_size': app_item['app_size'],
        'app_developer': app_item['app_developer'],
        'app_version': app_item['app_version'],
        'detail_description': app_item['detail_description'],
        'download_url': app_item['download_url'],
        'screenshots': app_item['screenshots']
    }
    return app_info

APP_FIELDS = {
    '_id': 0,
    'id': 1,
    'title': 1,
    'icon': 1,
    'app_rating': 1,
    'app_size': 1,
    'app_type': 1,
    'app_developer': 1,
    'app_publishtime': 1,
    'app_version': 1,
    'short_description': 1,
    'create_time': 1,
    'price': 1,
    'download_url': 1,
    'detail_description': 1,
    'screenshots': 1
}


FEATURE_FIELDS = {
    '_id': 0,
    'id': 1,
    'top': 1,
    'picture': 1,
    'pic_kind': 1,
    'application': 1,
}


def get_features(cond=None, page_no=1, page_size=10):
    feature_list = []
    try:
        page_no = int(page_no)
        page_size = int(page_size)
    except ValueError, e:
        logger.error(e)
        return feature_list
    colls = _feature.find(cond, fields=FEATURE_FIELDS).sort(
        'position').skip((page_no - 1) * page_size).limit(page_size)
    if colls.count():
        for item in colls:
            app_info = package_app_simple_info(item['application'])
            for key in app_info:
                item[key] = app_info[key]
            del item['application']
            feature_list.append(item)
    return feature_list


def get_hoting_apps(cond=None, page_no=1, page_size=10):
    trendings = []
    try:
        page_no = int(page_no)
        page_size = int(page_size)
    except ValueError:
        logger.error('page_no:%d,page_size:%d' % (page_no, page_size))
        return trendings
    colls = _hoting.find(cond).sort('position').skip(
        (page_no - 1) * page_size).limit(page_size)
    if colls.count():
        for item in colls:
            trendings.append(package_app_simple_info(item['application']))
    return trendings


def get_application_detail(cond=None, fields=None):
    coll = _application.find_one(cond, fields=APP_FIELDS)
    app = {}
    if coll:
        detail = package_app_detail_info(coll)
        if fields == 'all':
            app = detail
        elif fields == 'screenshots':
            app['screenshots'] = detail['screenshots']
        elif fields == 'base':
            app = detail
            del app['screenshots']
        else:
            app = detail
    return app


def get_search(cond=None):
    apps = []
    colls = _application.find(cond)
    apps = map(package_app_simple_info, colls)
    return apps

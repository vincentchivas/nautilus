# Copyright (c) 2011 Baina Info Inc. All rights reserved.
# @author: Chen Qi
# date:2011-11-20
# email:qchen@bainainfo.com

import time
import logging
import random
from operator import itemgetter
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
        _feature = _db['addon_feature']
        _hoting = _db['addon_hoting']
        _category = _db['addon_category']
        _application = _db['addon_application']
        _subject = _db['addon_subject']
    except Exception, e:
        logger.error(e)


def package_app_simple_info(app_item):
    app_info = {
        'id': app_item['id'],
        'title': app_item['title'],
        'icon': app_item['icon'],
        'app_rating': app_item['app_rating'],
        'app_ratingcount': app_item['app_ratingcount'],
        'app_lovecount': 0,
        'app_size': app_item['app_size'],
        'app_type': app_item['app_type'],
        'app_developer': app_item['app_developer'],
        'short_description': app_item['short_description'],
        'detail_description': app_item['detail_description'],
        'is_new': app_item['is_new'],
        'is_hot': app_item['is_hot'],
        'download_url': app_item['download_url'],
        'screenshots': app_item['screenshots'],
    }
    return app_info


def package_app_detail_info(app_item):
    app_info = {
        'id': app_item['id'],
        'title': app_item['title'],
        'icon': app_item['icon'],
        'big_icon': app_item['big_icon'],
        'app_rating': app_item['app_rating'],
        'app_ratingcount': app_item['app_ratingcount'],
        'price': app_item['price'],
        'app_size': app_item['app_size'],
        'app_type': app_item['app_type'],
        'app_developer': app_item['app_developer'],
        'app_publishtime': app_item['app_publishtime'],
        'app_version': app_item['app_version'],
        'detail_description': app_item['detail_description'],
        'download_url': app_item['download_url'],
        'screenshots': app_item['screenshots']
    }
    return app_info

_APP_FIELDS = {
    '_id': 0,
    'id': 1,
    'title': 1,
    'icon': 1,
    'big_icon': 1,
    'backup_icon': 1,
    'app_rating': 1,
    'app_ratingcount': 1,
    'app_size': 1,
    'app_type': 1,
    'app_developer': 1,
    'app_publishtime': 1,
    'app_version': 1,
    'short_description': 1,
    'create_time': 1,
    'price': 1,
    'is_new': 1,
    'is_hot': 1,
    'download_url': 1,
    'top_ranking': 1,
    'ranking_position': 1,
    'top_new': 1,
    'new_position': 1,
    'top_web': 1,
    'web_position': 1,
    'detail_description': 1,
    'screenshots': 1
}


def get_category(cond=None):
    categories = []
    colls = _category.find(cond).sort('position')
    if colls.count():
        for item in colls:
            item_content = {
                'id': item['id'],
                'title': item['category_name'],
                'icon': item['icon'],
                'short_description': item['short_description']
            }
            categories.append(item_content)
    return categories


def get_category_apps_ranking(cond, page_no=1, page_size=10):
    applications = []
    try:
        page_no = int(page_no)
        page_size = int(page_size)
    except ValueError:
        logger.debug('page_no:%d,page_size:%d' % (page_no, page_size))
        return applications
    colls = _application.find(cond, fields=_APP_FIELDS)
    apps = []
    top_apps = []
    if colls.count():
        for item in colls:
            item['votes'] = item['app_rating'] * item['app_ratingcount']
            apps.append(item)
        for item in apps:
            if item['top_ranking']:
                top_apps.append(item)
                apps.remove(item)

        top_apps.sort(key=itemgetter('ranking_position'), reverse=False)
        apps.sort(key=itemgetter('votes'), reverse=True)
        top_apps.extend(apps)
        start_index = (page_no - 1) * page_size
        end_index = page_no * page_size
        length = len(top_apps)
        if length >= end_index:
            applications = top_apps[start_index:end_index]
        elif length >= start_index:
            applications = top_apps[start_index:]
        else:
            applications = []
        applications = map(package_app_simple_info, applications)
    return applications


def get_category_apps_new(cond, page_no=1, page_size=10):
    applications = []
    try:
        page_no = int(page_no)
        page_size = int(page_size)
    except ValueError:
        logger.debug('page_no:%d,page_size:%d' % (page_no, page_size))
        return applications
    colls = _application.find(cond, fields=_APP_FIELDS)
    apps = []
    top_apps = []
    if colls.count():
        apps.extend(colls)
        for item in apps:
            if item['top_new']:
                top_apps.append(item)
                apps.remove(item)

        top_apps.sort(key=itemgetter('new_position'), reverse=False)
        apps.sort(key=itemgetter('create_time'), reverse=True)
        top_apps.extend(apps)
        start_index = (page_no - 1) * page_size
        end_index = page_no * page_size
        length = len(top_apps)
        if length >= end_index:
            applications = top_apps[start_index:end_index]
        elif length >= start_index:
            applications = top_apps[start_index:]
        else:
            applications = []
        applications = map(package_app_simple_info, applications)
    return applications


def get_category_apps_webapp(cond, page_no=1, page_size=10):
    applications = []
    try:
        page_no = int(page_no)
        page_size = int(page_size)
    except ValueError:
        logger.debug('page_no:%d,page_size:%d' % (page_no, page_size))
        return applications
    cond['app_type'] = 'WebApp'
    colls = _application.find(cond, fields=_APP_FIELDS)
    apps = []
    top_apps = []
    if colls.count():
        apps.extend(colls)
        for item in apps:
            if item['top_web']:
                top_apps.append(item)
                apps.remove(item)

        top_apps.sort(key=itemgetter('web_position'), reverse=False)
        apps.sort(key=itemgetter('create_time'), reverse=True)
        top_apps.extend(apps)
        start_index = (page_no - 1) * page_size
        end_index = page_no * page_size
        length = len(top_apps)
        if length >= end_index:
            applications = top_apps[start_index:end_index]
        elif length >= start_index:
            applications = top_apps[start_index:]
        else:
            applications = []
        applications = map(package_app_simple_info, applications)
    return applications


def get_feature_apps(cond=None, page_no=1, page_size=10):
    featureds = []
    try:
        page_no = int(page_no)
        page_size = int(page_size)
    except ValueError:
        logger.error('page_no:%d,page_size:%d' % (page_no, page_size))
        return featureds
    colls = _feature.find(cond).sort('position').skip(
        (page_no - 1) * page_size).limit(page_size)
    if colls.count():
        for item in colls:
            featureds.append(package_app_simple_info(item['content']))
    return featureds


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


def get_subject(cond=None):
    subjects = []
    colls = _subject.find(cond).sort('position')
    if colls.count():
        for item in colls:
            item_content = {
                'id': item['id'],
                'title': item['subject_name'],
                'icon': item['icon'],
                'short_description': item['short_description'],
                'update_number': item['update_number'],
                'number': len(item['application'])
            }
            subjects.append(item_content)
    return subjects


def get_subject_apps(cond=None, page_no=1, page_size=24):
    apps = []
    try:
        time_now = int(time.time())
        page_no = int(page_no)
        page_size = int(page_size)
    except ValueError:
        logger.debug('page_no:%d,page_size:%d' % (page_no, page_size))
        return apps
    coll = _subject.find_one(cond)
    if coll:
        app_list = coll['application']
        number = 1
        for item in app_list:
            if item['online_time'] <= time_now and (item['offline'] == False or item['offline_time'] > time_now):
                if number > (page_no - 1) * page_size and number <= page_no * page_size:
                    apps.append(package_app_simple_info(item))
                number += 1
    return apps


def get_webapps(cond=None, page_no=1, page_size=24):
    apps = []
    try:
        page_no = int(page_no)
        page_size = int(page_size)
    except ValueError, e:
        logger.error(e)
        return apps
    cond['app_type'] = 'WebApp'
    colls = _application.find(cond).sort('position').skip(
        (page_no - 1) * page_size).limit(page_size)
    if colls.count():
        apps = map(package_app_detail_info, colls)
    return apps


def get_application_detail(cond=None, fields=None):
    coll = _application.find_one(cond, {'_id': 0})
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


def get_relevant_addons(cond=None):
    relevant_apps = []
    app = _application.find_one(cond)
    if app:
        relevant_cond = {"category": app["category"],
                         "platform": app["platform"], "id": {"$ne": app["id"]}}
        colls = _application.find(relevant_cond).limit(RELEVANT_APP_NUM)
        if colls.count() > RELEVANT_APP_NUM:
            count = colls.count()
            slice = int(random.random() * (count - RELEVANT_APP_NUM))
            colls = colls[slice: slice + RELEVANT_APP_NUM]

        if colls.count():
            relevant_apps = map(package_app_simple_info, colls)

    return relevant_apps


def get_search(cond=None):
    apps = []
    colls = _hoting.find(cond)
    apps = map(lambda app_item:
               package_app_simple_info(app_item['application']), colls)
    return apps

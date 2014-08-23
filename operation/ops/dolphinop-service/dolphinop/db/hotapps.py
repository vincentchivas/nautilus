# Copyright (c) 2011 Baina Info Inc. All rights reserved.
# @author: Chen Qi
# date:2011-11-20
# email:qchen@bainainfo.com

import time
import logging
import random
from dolphinop.db import connect

logger = logging.getLogger('dolphinop.db')

_db = None
_featureds = None
_trendings = None
_categories = None
_applications = None
_daily = None
_ads = None
_feature_new = None
_trending_new = None
_category_new = None
_application_new = None

PLAT_FORM_IPAD = ('iPad_CN', 'iPad_EN')

RELEVANT_APP_NUM = 3


def config(server, db, port=None):
    # check the server and db.
    assert server and db, 'Either "host" or "db" should not be None'
    global _db, _featureds, _trendings, _categories, _applications, _daily, _ads,\
        _feature_new, _trending_new, _category_new, _application_new
    try:
        conn = connect(server, port)
        _db = conn[db]
        _featureds = _db['feature']
        _trendings = _db['trending']
        _categories = _db['category']
        _applications = _db['application']
        _daily = _db['daily']
        _ads = _db['ad']
        _feature_new = _db['feature_new']
        _trending_new = _db['trending_new']
        _category_new = _db['category_new']
        _application_new = _db['application_new']
    except Exception, e:
        logger.debug(e)


def _package_app_info(app_item):
    app_info = {'id': app_item['id'], 'title': app_item['title'],
                'favicon': app_item['icon'], 'short_description':
                app_item['short_description'], 'is_new': app_item['is_new'],
                'detail_description': app_item['detail_description'],
                'original_price': app_item['original_price'],
                'price': app_item['price'], 'price_type': app_item['price_type'],
                # these two parts are hacks for the ads platform
                'is_ad': app_item['is_third_part'],
                'ad_id': app_item['is_third_part'], }
    app_info['download_url'] = './details.html?id=%s' % app_info['id'] \
        if app_item['show_details'] else app_item['download_url']
    return app_info


def _package_daily_info(app_item, cond):
    app_info = _package_app_info(app_item['application'])
    cate_id = int(app_item['application']['category'])
    app_info['category'] = _categories.find_one(
        {'id': cate_id, 'platform': cond['platform']})['category_name']

    app_info['reason'] = app_item['reason']
    return app_info


def _package_ads_info(app_item):
    app_info = {
        'title': app_item['title'], 'picture_url': app_item['picture_url'],
        'download_url': app_item['download_url']}
    return app_info


def _get_category_description(cond, cate_id):
    cond['category'] = cate_id
    applications = _applications.find(cond).sort('order')
    count = applications.count()
    if count > 1:
        description = '%s | %s' % (
            applications[0]['title'], applications[1]['title'])
    elif count == 1:
        description = applications[0]['title']
    else:
        return None
    return description


def _get_category_icon(cond, cate_id):
    cond['category'] = cate_id
    applications = _applications.find(cond).sort('order')
    if applications.count():
        icon = applications[0]['icon']
    else:
        return None
    return icon


def get_top_featured(cond=None):
    top_featured = []
    cond['feature_on_top'] = 1
    colls = _featureds.find(cond).sort('order')
    if colls:
        for item in colls:
            if item['feature_type'] == 'Category':
                category_id, category_title = item['content'].split(' ', 1)
                feature_info = {'top_pic': item['top_feature_pic'],
                                'category_id': category_id, 'category_title': category_title}
            else:
                application = item['content']
                feature_info = {'top_pic':
                                item['top_feature_pic'], 'title': application['title']}
                feature_info['download_url'] = './details.html?id=%s' % application['id'] \
                    if application['show_details'] else application['download_url']

            if item['platform'] in PLAT_FORM_IPAD:
                feature_info['small_pic'] = item['small_pic']

            # leverage the third party for web promotion
            feature_info['is_third_part'] = item['is_third_part']
            feature_info['third_part_url'] = item['third_part_url']

            top_featured.append(feature_info)
    return top_featured


def get_featured_apps(cond=None, page_no=1, page_size=10):
    featureds = []
    cond['feature_on_top'] = 0
    try:
        page_no = int(page_no)
        page_size = int(page_size)
    except ValueError:
        logging.debug('page_no:%d,page_size:%d' % (page_no, page_size))
        return featureds
    colls = _featureds.find(cond).sort('order').skip(
        (page_no - 1) * page_size).limit(page_size)
    if colls.count():
        for item in colls:
            featureds.append(_package_app_info(item['content']))
    return featureds


def get_trend_apps(cond=None, page_no=1, page_size=10):
    trendings = []
    try:
        page_no = int(page_no)
        page_size = int(page_size)
    except ValueError:
        logging.debug('page_no:%d,page_size:%d' % (page_no, page_size))
        return trendings
    colls = _trendings.find(cond).sort('order').skip(
        (page_no - 1) * page_size).limit(page_size)
    if colls.count():
        for item in colls:
            trendings.append(_package_app_info(item['application']))
    return trendings


def get_categories(cond=None):
    categories = []
    colls = _categories.find(cond).sort('order')
    if colls.count():
        for item in colls:
            item_content = {'id': item['id'], 'title': item['category_name'],
                            'favicon': item['icon'], 'short_description': item['short_description']}
            categories.append(item_content)
    return categories


def get_category_apps(cond, page_no=1, page_size=10):
    applications = []
    try:
        page_no = int(page_no)
        page_size = int(page_size)
    except ValueError:
        logging.debug('page_no:%d,page_size:%d' % (page_no, page_size))
        return applications
    colls = _applications.find(cond).sort('order').skip(
        (page_no - 1) * page_size).limit(page_size)
    if colls.count():
        for item in colls:
            applications.append(_package_app_info(item))
    return applications


def get_application_details(cond):
    application = _applications.find_one(cond)
    if application:
        category_cond = {'id': int(application['category']), 'platform':
                         application['platform']}
        category = _categories.find_one(category_cond)
        application['category'] = category[
            'category_name'] if category else 'None'
    return application


def get_advertisements(cond=None):
    apps = None
    colls = _ads.find(cond).sort('order')
    if colls:
        apps = map(_package_ads_info, colls)
    return apps


def get_daily_recommend_app(cond=None):
    apps = []
    colls = _daily.find(cond).sort('order')
    if colls:
        for item in colls:
            apps.append(_package_daily_info(item, cond))
    return apps


def get_applications(cond=None, page_no=1, page_size=35):
    apps = None
    try:
        page_no = int(page_no)
        page_size = int(page_size)
    except ValueError:
        logging.debug('page_no:%d,page_size:%d' % (page_no, page_size))
        return apps
    colls = _applications.find(cond).sort('order').skip(
        (page_no - 1) * page_size).limit(page_size)

    if colls:
        apps = map(_package_app_info, colls)
    return apps


def package_app_simple_info(app_item):
    app_info = {
        'id': app_item['id'],
        'title': app_item['title'],
        'icon': app_item['icon'],
        'app_rating': app_item['app_rating'],
        'app_ratingcount': app_item['app_ratingcount'],
        'app_lovecount': app_item['app_lovecount'],
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
        'app_rating': app_item['app_rating'],
        'app_ratingcount': app_item['app_ratingcount'],
        'app_lovecount': app_item['app_lovecount'],
        'app_size': app_item['app_size'],
        'app_type': app_item['app_type'],
        'app_developer': app_item['app_developer'],
        'short_description': app_item['short_description'],
        'detail_description': app_item['detail_description'],
        'pub_time': app_item.get('pub_time', ''),
        'is_new': app_item['is_new'],
        'is_hot': app_item['is_hot'],
        'download_url': app_item['download_url'],
        'screenshots': app_item['screenshots'],
    }
    return app_info


def get_top_featured_new(cond=None):
    top_featured = []
    cond['feature_on_top'] = 1
    colls = _feature_new.find(cond).sort('order')
    if colls:
        for item in colls:
            feature_info = {'top_pic': item['top_feature_pic']}
            if item['feature_type'] == 'Category':
                feature_info['category_id'] = item['content']['category_id']
                feature_info['category_name'] = item[
                    'content']['category_name']
            else:
                feature_info['application'] = package_app_detail_info(
                    item['content'])

            if item['platform'] in PLAT_FORM_IPAD:
                feature_info['small_pic'] = item['small_pic']

            top_featured.append(feature_info)
    return top_featured


def get_home_page(cond=None):
    home_page = {
        'top_feature': [],
        'daily': {},
        'apps': []
    }
#    daily = None
#    cond['hot_today'] = True
#    coll = _feature_new.find_one(cond)
#    if coll:
#        daily = package_app_detail_info(coll['content'])
#    else:
#        daily_cond = cond.copy()
#        del daily_cond['online_time']
#        del daily_cond['$or']
#        coll = _feature_new.find_one(daily_cond)
#        if coll:
#            daily = package_app_detail_info(coll['content'])
#    apps = []
#    cond['feature_on_top'] = 0
#    cond['hot_today'] = False
#    colls = _feature_new.find(cond).sort('order').limit(12)
#    if colls:
#        for item in colls:
#            apps.append(package_app_detail_info(item['content']))
#    home_page['top_feature'] = get_top_featured_new(cond)
#    home_page['daily'] = daily
#    home_page['apps'] = apps
    try:
        features = _feature_new.find(cond).sort('order')
        for item in features:
            if item['feature_on_top']:
                feature_info = {'top_pic': item['top_feature_pic']}
                if item['feature_type'] == 'Category':
                    feature_info['category_id'] = item[
                        'content']['category_id']
                    feature_info['category_name'] = item[
                        'content']['category_name']
                else:
                    feature_info['application'] = package_app_detail_info(
                        item['content'])

                if item['platform'] in PLAT_FORM_IPAD:
                    feature_info['small_pic'] = item['small_pic']
                home_page['top_feature'].append(feature_info)

            elif item['feature_type'] == 'Category':
                continue

            elif item['hot_today']:
                home_page['daily'] = package_app_detail_info(item['content'])

            else:
                home_page['apps'].append(
                    package_app_detail_info(item['content']))
        if not home_page['daily']:
            daily_cond = {'hot_today': True, 'platform': cond['platform']}
            coll = _feature_new.find_one(daily_cond)
            if coll:
                home_page['daily'] = package_app_detail_info(coll['content'])
    except Exception, e:
        logger.error(e)
        return home_page
    return home_page


def get_trend_apps_new(cond=None, page_no=1, page_size=24):
    trendings = []
    try:
        page_no = int(page_no)
        page_size = int(page_size)
    except ValueError:
        logging.debug('page_no:%d,page_size:%d' % (page_no, page_size))
        return trendings
    colls = _trending_new.find(cond).sort('order').skip(
        (page_no - 1) * page_size).limit(page_size)
    if colls.count():
        for item in colls:
            trendings.append(package_app_detail_info(item['application']))
    return trendings


def get_categories_new(cond=None):
    categories = []
    colls = _category_new.find(cond).sort('order')
    if colls.count():
        for item in colls:
            item_content = {'id': item['id'], 'title': item['category_name'],
                            'favicon': item['icon'], 'short_description': item['short_description'], 'update_number': item['update_number']}
            categories.append(item_content)
    return categories


def get_category_apps_new(cond=None, page_no=1, page_size=24):
    apps = []
    try:
        #time_now = int(time.time())
        page_no = int(page_no)
        page_size = int(page_size)
    except ValueError:
        logging.debug('page_no:%d,page_size:%d' % (page_no, page_size))
        return apps
    coll = _category_new.find_one(cond)
    if coll:
        app_list = coll['application']
        number = 1
        for item in app_list:
            #if item['online_time'] <= time_now and (item['offline'] == False or item['offline_time'] > time_now):
            if number > (page_no - 1) * page_size and number <= page_no * page_size:
                apps.append(package_app_detail_info(item))
            number += 1

    return apps


def get_application_details_new(cond=None):
    coll = _application_new.find_one(cond, {'_id': 0})
    if coll:
        return package_app_detail_info(coll)
    return None


def set_lovecount(cond=None):
    app = _application_new.find_one(cond)
    if app:
        app['app_lovecount'] += 1
        _application_new.update(cond, app, True)

    feature_cond = {'platform': cond['platform'], 'content.id': cond['id']}
    feature = _feature_new.find_one(feature_cond)
    if feature:
        feature['content']['app_lovecount'] += 1
        _feature_new.update(feature_cond, feature, True)

    trend_cond = {'platform': cond['platform'], 'application.id': cond['id']}
    trend = _trending_new.find_one(trend_cond)
    if trend:
        trend['application']['app_lovecount'] += 1
        _trending_new.update(trend_cond, trend, True)

    category_cond = {
        'application.platform': cond['platform'],
        'application.id': cond['id']
    }
    categories = _category_new.find(category_cond)
    if categories:
        for category in categories:
            cate_cond = category_cond.copy()
            cate_cond['id'] = category['id']
            for item in category['application']:
                if item['id'] == category_cond['application.id']:
                    item['app_lovecount'] += 1
            _category_new.update(cate_cond, category, True)


def get_relevant_apps(cond=None):
    relevant_apps = []
    category = _category_new.find_one(cond)
    if category:
        apps = category['application']
        length = len(apps)
        if length >= RELEVANT_APP_NUM + 1:
            rand = random.randint(0, length - (RELEVANT_APP_NUM + 1))
            relevant_apps = apps[rand:rand + RELEVANT_APP_NUM + 1]
        else:
            relevant_apps = apps
        num = 1
        for item in relevant_apps:
            if item['id'] == cond['application.id'] or num > RELEVANT_APP_NUM:
                relevant_apps.remove(item)
            num += 1
        relevant_apps = map(package_app_detail_info, relevant_apps)
    return relevant_apps

#!/usr/bin/python
import os
import sys
import urllib
import urllib2
import json
import time
import hashlib
import urlparse
import logging

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(PROJECT_PATH))

FORMAT = '%(asctime)s %(levelname)s %(name)s [%(filename)s:%(lineno)d] %(funcName)s %(message)s'
logging.basicConfig(filename='/tmp/api.log',level=logging.INFO, format=FORMAT)
logger = logging.getLogger()


STATUS_OK = 0
STATUS_INFO = 1
STATUS_WARNING = 2
STATUS_ERROR = 3
STATUS_DISASTER = 4

TIME_OUT = 25
MAX_UPDATE_TIME = 600 * 1000 * 1000
IMAGE_LENGTH = [16903, 16989]

HEADERS = {'Content-type': 'application/json', 'Accept': 'text/plain'}
WEIBO_URL_FORMAT = 'http://dzone.dolphin.com/api/infostream/weibo.json?wid=%d&https=1'
NEWS_VW_NEWS_FORMAT = 'http://news.dolphin-browser.com/vw/news/%d?t=0&mt=0'
NEWS_VW_GATHERS_FORMAT = 'http://news.dolphin-browser.com/vw/gathers/%d?rs=15&mi=%d&t=1'
RELEVANCE_NEWS_FORMAT = 'http://relevance.dolphin-browser.com/news/%d?t=1'
READER_VW2_SUB_CATEGORIES_SOURCES_FORMAT = 'http://reader.dolphin-browser.com/vw2/sub/categories/%d/sources'
READER_VW2_SOURCES_DOCS_FORMAT = 'http://reader.dolphin-browser.com/vw2/sources/%d/docs?t=0&rs=30'
READER_VW2_DOCS_FORMAT = 'http://reader.dolphin-browser.com/vw2/docs/%d?tp=0&chid=%d&t=3'
PICS_VW_GALLERIES_FORMAT = 'http://pics.dolphin-browser.com/vw/galleries/%d?tp=all&t=1370078820'
PICS_VW_GALLERIES_NEIGHBOR_FORMAT = 'http://pics.dolphin-browser.com/vw/galleries/%d/neighbor?gid=%d&tp=all'
FORUM_VW_POSTS_FORMAT = 'http://forum.dolphin-browser.com/vw/posts/%d?&t=1370079368879'
EN_V4_COLUMNS_FORMAT = 'http://en.mywebzines.com/v4/columns/%d?t=1370090755'
EN_V3_COLUMNS_FORMAT = 'http://en.mywebzines.com/v3/columns/%d/articles?rs=18&t=1370076586927'
CN_V4_COLUMNS_FORMAT = 'http://cn.mywebzines.com/v4/columns/%d?t=1370090755'
CN_V3_COLUMNS_FORMAT = 'http://cn.mywebzines.com/v3/columns/%d/articles?rs=18&t=1370076586927'

#opscn
url_opscn_api_addons = 'http://opscn.dolphin-browser.com/api/addons.json?pn=com.dolphin.browser.cn&src=ofw&mt=1'
url_opscn_api_1_builtins = 'http://opscn.dolphin-browser.com/api/1/builtins.json?pn=com.dolphin.browser.cn&vn=91&src=ofw&op=00'
url_opscn_api_1_sections = 'http://opscn.dolphin-browser.com/api/1/sections?pn=com.dolphin.browser.cn&vn=91&src=ofw&mt=1'
url_opscn_api_2_sections = 'http://opscn.dolphin-browser.com/api/2/sections?pn=com.dolphin.browser.cn&vn=91&src=ofw&mt=1'
url_opscn_api_2_sections_test = 'http://opscn.dolphin-browser.com/api/2/sections_test?pn=com.dolphin.browser.cn&src=ofw&mt=1'
url_opscn_api_2_section = 'http://opscn.dolphin-browser.com/api/2/section.json?pn=com.dolphin.browser.cn&vn=91&src=ofw&mt=1&ids=1,2'
url_opscn_api_1_novels = 'http://opscn.dolphin-browser.com/api/1/novels.html?pn=com.dolphin.browser.cn&src=ofw'
url_opscn_api_1_navigate = 'http://opscn.dolphin-browser.com/api/1/navigate.json?pn=com.dolphin.browser.cn&mt=1'
url_opscn_api_1_treasure = 'http://opscn.dolphin-browser.com/api/1/treasure.json?pn=com.dolphin.browser.xf&src=ofw&vn=100&op=00&mt=1'
url_opscn_api_2_treasure = 'http://opscn.dolphin-browser.com/api/2/treasure.json?pn=com.dolphin.browser.xf&src=ofw&vn=100&op=00&mt=1'
url_opscn_api_1_skins = 'http://opscn.dolphin-browser.com/api/1/skins.json?pn=com.dolphin.browser.xf&src=ofw&cv=1&page=1&type=skin&mt=1'
url_opscn_api_1_skin_promote = 'http://opscn.dolphin-browser.com/api/1/skin/promote.json?pn=com.dolphin.browser.xf&src=ofw&cv=1&mt=1'
url_opscn_api_1_adverts = 'http://opscn.dolphin-browser.com/api/1/adverts.json?pn=com.dolphin.browser.xf&src=ofw&vn=100&op=00&cid=8'
url_opscn_api_1_search_cats = 'http://opscn.dolphin-browser.com/api/1/search/cats.json?pn=com.dolphin.browser.xf&src=ofw&vn=100&op=00&mt=1'
url_opscn_api_2_search_cats = 'http://opscn.dolphin-browser.com/api/2/search/cats.json?pn=com.dolphin.browser.xf&src=ofw&vn=100&op=00&mt=1'
url_opscn_api_1_search_hotwords = 'http://opscn.dolphin-browser.com/api/1/search/hotwords.json?pn=com.dolphin.browser.xf&src=ofw&vn=100&op=00&mt=1'
url_opscn_api_1_search_tracks = 'http://opscn.dolphin-browser.com/api/1/search/tracks.json?pn=com.dolphin.browser.xf&src=ofw&vn=100&op=00&mt=1'
url_opscn_api_1_desktop = 'http://opscn.dolphin-browser.com/api/1/desktop.json?pn=com.dolphin.browser.xf&src=ofw&vn=100&op=00'
url_opscn_api_updateservice = 'http://opscn.dolphin-browser.com/api/updateservice.json?pn=com.dolphin.browser.cn&src=ofw&vn=80&op=00&auto=true'
url_opscn_api_2_updateservice = 'http://opscn.dolphin-browser.com/api/2/updateservice.json'
url_opscn_api_3_updateservice = 'http://opscn.dolphin-browser.com/api/3/updateservice.json'
url_opscn_api_4_updateservice = 'http://opscn.dolphin-browser.com/api/4/updateservice.json'
url_opscn_api_promolink = 'http://opscn.dolphin-browser.com/api/promolink.json?pn=com.dolphin.browser.xf&src=ofw&vn=100&op=00&mt=1'
url_opscn_api_splash = 'http://opscn.dolphin-browser.com/api/splash.json?pn=com.dolphin.browser.xf&src=ofw&vn=100&net=wifi&w=800&h=480&mt=1'
url_opscn_api_subnag = 'http://opscn.dolphin-browser.com/api/subnag.json?pname=com.dolphin.browser.cn&page=novel&last_modified=0'
url_opscn_service_1_weathers = 'http://opscn.dolphin-browser.com/service/1/weathers.json?pn=com.dolphin.browser.xf&src=ofw&vn=100&op=00&mt=1'
url_webapps_api_1_webapps_cats = 'http://webapps.dolphin.com/api/1/webapps/cats.json?pn=mobi.mgeek.TunnyBrowser&page=0'
url_webapps_api_1_webapps_subjects = 'http://webapps.dolphin.com/api/1/webapps/subjects.json?pn=mobi.mgeek.TunnyBrowser&banner=true&page=0'
url_webapps_api_1_webapps_apps = 'http://webapps.dolphin.com/api/1/webapps/apps.json?pn=mobi.mgeek.TunnyBrowser&page=0'
url_opscn_api_1_topsite = 'http://opscn.dolphin-browser.com/api/1/topsite.json?pn=com.dolphin.browser.iphone.chinese.xuanfeng&vn=100&mt=1'

#opsen
url_opsen_api_addons = 'http://opsen.dolphin-browser.com/api/addons.json?pn=mobi.mgeek.TunnyBrowser&src=ofw&mt=1'
url_opsen_api_1_builtins = 'http://opsen.dolphin-browser.com/api/1/builtins.json?pn=mobi.mgeek.TunnyBrowser&vn=200&src=ofw&op=00'
url_opsen_api_updateservice = 'http://opsen.dolphin-browser.com/api/updateservice.json?pn=mobi.mgeek.TunnyBrowser&src=ofw&vn=200&op=00&auto=true'
url_opsen_api_2_updateservice = 'http://opsen.dolphin-browser.com/api/2/updateservice.json'
url_opsen_api_promolink = 'http://opsen.dolphin-browser.com/api/promolink.json?pn=mobi.mgeek.TunnyBrowser&src=ofw&vn=200&op=00&mt=1'
url_opsen_api_1_webapp_notification = 'http://opsen.dolphin-browser.com/api/1/webapp/notification.json?pn=mobi.mgeek.TunnyBrowser&src=ofw&vn=207&locale=en_US&mt=0'
url_opsen_api_1_modes = 'http://opsen.dolphin-browser.com/api/1/modes.json?pn=mobi.mgeek.TunnyBrowser&src=ofw&vn=207&mt=0&mode=webapp'
url_opsen_api_1_topsite = 'http://opsen.dolphin-browser.com/api/1/topsite.json?pn=mobi.mgeek.TunnyBrowser&vn=207&mt=0'

#pnscn
url_pnscn_notification_android_messages = 'https://pnscn.dolphin-browser.com/notification/android/messages.json?pname=com.dolphin.browser.xf&version=211'
url_pnscn_notification_android_message = 'https://pnscn.dolphin-browser.com/notification/android/message.json?pname=com.dolphin.browser.xf&version=211&t=0'

#dzone
url_dzone_api_infostream = 'http://dzone.dolphin.com/api/infostream.json?https=1&rs=1'
url_dzone_api_token = 'http://dzone.dolphin.com/api/weibo/auth?https=1'

#webzine
url_news_vw_gathers_news = 'http://news.dolphin-browser.com/vw/gathers/news?drs=15&vrs=8&t=0'
url_hub_vw2_hub_hot = 'http://hub.dolphin.com/vw2/hub/hot.json'
url_hub_vw2_hub_widget = 'http://hub.dolphin.com/vw2/hub/widget.json?display=ios&count=15'
url_reader_vw2_sub_init = 'http://reader.dolphin-browser.com/vw2/sub/init?t=2'
url_reader_vw2_sub_categories = 'http://reader.dolphin-browser.com/vw2/sub/categories'
url_reader_vw2_sources_contents = 'http://reader.dolphin-browser.com/vw2/sources/2454/contents?t=2&rs=10&pic=1'
url_image_image = 'http://image.dolphin-browser.cn/image/aHR0cDovL2ltZzEuZ3RpbWcuY29tL2VudC9waWNzL2h2MS8xMDcvMTYvMTMzOC84NzAwNzYzNy5qcGc=/dz0zMDAmcT04MA=='
url_pics_vw_gathers_gallery = 'http://pics.dolphin-browser.com/vw/gathers/gallery?dg=0&rs=16&ds=8&gs=6&t=1370076151355'
url_forum_vw_gathers_post = 'http://forum.dolphin-browser.com/vw/gathers/post?drs=15&vrs=8&t=1370078702717'

#webzine client
url_en_columns_recommends = 'http://en.mywebzines.com/columns/recommends?t=1234567890'
url_en_v6_columns_featured = 'http://en.mywebzines.com/v6/columns/featured?dt=pad&locale=en_us&os=ios&t=1370089800'
url_cn_columns_recommends = 'http://cn.mywebzines.com/columns/recommends?t=1234567890'
url_cn_v6_columns_featured = 'http://cn.mywebzines.com/v6/columns/featured?dt=pad&locale=zh_cn&os=ios&t=1370089800'


#updateservice post request parameter
data_opscn_api_2_updateservice = {
        "did":"72a593e947291c16e78bcde69aa05af9",
        "app":[
            {
                "vn": 100,
                "pn": "com.dolphin.browser.xf",
                "src": "ofw",
                }
            ],
        }
data_opscn_api_3_updateservice = {
        "did":"72a593e947291c16e78bcde69aa05af9",
        "app":[
            {
                "hash": "28cb4640eb91168223bee4d6a42bc092",
                "vn": 100,
                "pn": "com.dolphin.browser.xf",
                "src": "ofw",
                }
            ],
        }
data_opscn_api_4_updateservice = {
        "did":"72a593e947291c16e78bcde69aa05af9",
        "app":[
            {
                "hash": "28cb4640eb91168223bee4d6a42bc092",
                "vn": 100,
                "pn": "com.dolphin.browser.xf",
                "src": "ofw",
                "asrc": "ofw",
                "type": "dolphin"
                }
            ],
        }

data_opsen_api_2_updateservice = {
        "did":"72a593e947291c16e78bcde69aa05af9",
        "app":[
            {
                "vn": 200,
                "pn": "mobi.mgeek.TunnyBrowser",
                "src": "ofw",
                }
            ],
        }

data_dzone_api_token = {
    'uid': 3268768533,
    'token': '2.00HB7NZDQSGkPE76ee43bc38_T9yLE',
    }


def _request_url(url, data=None, result_type=None, headers=HEADERS):
    logger.debug(url)
    logger.debug(data)
    if headers:
        req = urllib2.Request(url, headers=headers)
    else:
        req = urllib2.Request(url)
    logger.debug(req)
    if data is None:
        response = urllib2.urlopen(url, timeout=TIME_OUT)
    else:
        response = urllib2.urlopen(req, data=data, timeout=TIME_OUT)
        #response = urllib2.urlopen(req, data=data, timeout=TIME_OUT)
    content = response.read()
    if result_type == 'json':
        content = json.loads(content)
    return content


def gte(a, b):
    return a >= b

def equal(a, b):
    return a == b

def lte(a, b):
    return a <= b

def _generate_authorization(*args):
    s = ' '.join(args)
    #print s
    m = hashlib.md5()
    m.update(s)
    res = m.hexdigest()
    #print res
    return res

def create_request(url):
    parse = urlparse.urlparse(url)
    path = parse.path.lower()
    query = parse.query.lower()
    params = query.split('&')
    t = params[-1].replace('t=', '')
    q = params[:-1]
    q.sort()
    q = '&'.join(q)
    #print q
    auth = _generate_authorization(*('WebzineAuth', path, q, t))
    #print auth
    request = urllib2.Request(url)
    request.add_header('Authorization', auth)
    return request


def auth_request(url):
    req = create_request(url)
    fp = urllib2.urlopen(req)
    content = fp.read()
    return json.loads(content)


def check_api(result, result_type, number=None, cmp_func=None, fields=None, dic=None):
    logger.debug('result_type: %s' %result_type)
    logger.debug('number: %s' % number)
    logger.debug('cmp_func: %s' % cmp_func.__name__ if cmp_func else None)
    logger.debug('fields: %s' % fields)
    logger.debug('dic: %s' % dic)
    logger.debug('type result: %s' % type(result))
    if not isinstance(result, result_type):
        logger.error('result type error: %s' % type(result))
        return STATUS_ERROR
    if number is not None and cmp_func is not None:
        logger.debug(len(result))
        if result_type is list:
            if not cmp_func(len(result), number):
                logger.error('result length %s' % len(result))
                return STATUS_ERROR
    if fields is not None:
        if result_type is dict:
            for field in fields:
                if field not in result:
                    logger.error(field)
                    logger.info(result.keys())
                    return STATUS_ERROR
    if dic is not None:
        if result_type is dict:
            for key in dic:
                if not ((key in result) and (result[key] == dic[key])):
                    logger.error(key)
                    if key in result:
                        logger.error(result[key])
                    return STATUS_ERROR
    return STATUS_OK

def check_dzone_infostream(result, result_type, number=None, cmp_func=None):
    check_pass = check_api(result, result_type, number=number, cmp_func=cmp_func)
    if check_pass != STATUS_OK:
        return check_pass
    last_modified = result[0]['id']
    now = int(time.time() * 1000 * 1000)
    logger.debug(now - last_modified)
    if now - last_modified > MAX_UPDATE_TIME:
        return STATUS_ERROR
    wid = result[0]['data']['weiboId']
    weibo_url = WEIBO_URL_FORMAT % wid
    json_result = _request_url(weibo_url, result_type='json')
    return check_api(json_result, result_type=dict, fields=['cnt'])


def check_news_vw_gathers_news(result, result_type, fields, dic):
    check_pass = check_api(result, result_type, fields=fields, dic=dic)
    logger.debug(check_pass)
    if check_pass != STATUS_OK:
        return check_pass
    check_pass = check_api(result['vg'][0]['d']['art'], list, number=15, cmp_func=equal)
    logger.debug(check_pass)
    if check_pass != STATUS_OK:
        return check_pass
    check_pass = check_api(result['vg'][1]['d']['art'], list, number=8, cmp_func=equal)
    logger.debug(check_pass)
    if check_pass != STATUS_OK:
        return check_pass
    channel_id = result['vg'][0]['id']
    article_id = result['vg'][0]['d']['art'][0]['id']
    #detail API
    detail_url = NEWS_VW_NEWS_FORMAT % article_id
    json_result = _request_url(detail_url, result_type='json')
    check_pass = check_api(json_result, dict, dic={'sta': 0})
    logger.debug(check_pass)
    if check_pass != STATUS_OK:
        return check_pass
    #gathers API
    gather_url = NEWS_VW_GATHERS_FORMAT % (channel_id, article_id)
    json_result = _request_url(gather_url, result_type='json')
    check_pass = check_api(json_result, dict, dic={'sta': 0})
    if check_pass != STATUS_OK:
        return check_pass
    check_pass = check_api(json_result['d']['art'], list, number=15, cmp_func=lte)
    logger.debug(check_pass)
    if check_pass != STATUS_OK:
        return check_pass
    #relevance API
    relevance_url = RELEVANCE_NEWS_FORMAT % article_id
    json_result = _request_url(relevance_url, result_type='json')
    check_pass = check_api(json_result, dict, dic={'sta': 0})
    logger.debug(check_pass)
    if check_pass != STATUS_OK:
        return check_pass
    return STATUS_OK


def check_hub_vw2_hub_hot(result, result_type, number, cmp_func):
    check_pass = check_api(result, result_type, number=number, cmp_func=cmp_func)
    logger.debug(check_pass)
    if check_pass != STATUS_OK:
        return check_pass
    check_pass = check_api(result[0]['docs'], list, 7, equal)
    logger.debug(check_pass)
    if check_pass != STATUS_OK:
        return check_pass
    check_pass = check_api(result[-1]['posts'], list, 7, equal)
    logger.debug(check_pass)
    if check_pass != STATUS_OK:
        return check_pass
    return STATUS_OK


def check_hub_vw2_hub_widget(result, result_type, fields):
    check_pass = check_api(result, result_type, fields=fields)
    logger.debug(check_pass)
    if check_pass != STATUS_OK:
        return check_pass
    check_pass = check_api(result['posts'], list, 15, equal)
    logger.debug(check_pass)
    if check_pass != STATUS_OK:
        return check_pass
    check_pass = check_api(result['news'][0]['docs'], list, 15, equal)
    logger.debug(check_pass)
    if check_pass != STATUS_OK:
        return check_pass
    return STATUS_OK


def check_reader_vw2_sub_categories(result, result_type, dic):
    check_pass = check_api(result, result_type, dic=dic)
    logger.debug(check_pass)
    if check_pass != STATUS_OK:
        return check_pass
    cat_id = result['catinfo'][0]['catid']
    #categories API
    category_url = READER_VW2_SUB_CATEGORIES_SOURCES_FORMAT % cat_id
    json_result = _request_url(category_url, result_type='json')
    check_pass = check_api(json_result, dict, dic={'sta': 0})
    logger.debug(check_pass)
    if check_pass != STATUS_OK:
        return check_pass
    ch_id = json_result['subsrc'][0]['chid']
    #sources API
    source_url = READER_VW2_SOURCES_DOCS_FORMAT % ch_id
    json_result = _request_url(source_url, result_type='json')
    check_pass = check_api(json_result, dict, dic={'sta': 0})
    logger.debug(check_pass)
    if check_pass != STATUS_OK:
        return check_pass
    check_pass = check_api(json_result['docs'], list, number=30, cmp_func=equal)
    logger.debug(check_pass)
    if check_pass != STATUS_OK:
        return check_pass
    doc_id = json_result['docs'][0]['id']
    #doc API
    doc_url = READER_VW2_DOCS_FORMAT % (doc_id, ch_id)
    json_result = _request_url(doc_url, result_type='json')
    check_pass = check_api(json_result, dict, dic={'sta': 0})
    logger.debug(check_pass)
    if check_pass != STATUS_OK:
        return check_pass
    return STATUS_OK


def check_reader_vw2_sources_contents(result, result_type, dic):
    check_pass = check_api(result, result_type, dic=dic)
    logger.debug(check_pass)
    if check_pass != STATUS_OK:
        return check_pass
    check_pass = check_api(result['docs'], list, number=10, cmp_func=equal)
    logger.debug(check_pass)
    if check_pass != STATUS_OK:
        return check_pass
    return STATUS_OK


def check_image(encoded_str):
    length = len(encoded_str)
    if length not in IMAGE_LENGTH:
        return STATUS_ERROR
    return STATUS_OK


def check_pics(result, result_type, dic):
    check_pass = check_api(result, result_type, dic=dic)
    logger.debug(check_pass)
    if check_pass != STATUS_OK:
        return check_pass
    ch_id = result['vg'][0]['id']
    doc_id = result['vg'][0]['d'][0]['id']
    #API
    doc_url = PICS_VW_GALLERIES_FORMAT % doc_id
    json_result = _request_url(doc_url, result_type='json')
    check_pass = check_api(json_result, dict, dic={'sta': 0})
    logger.debug(check_pass)
    if check_pass != STATUS_OK:
        return check_pass
    neighbor_url = PICS_VW_GALLERIES_NEIGHBOR_FORMAT % (doc_id, ch_id)
    json_result = _request_url(neighbor_url, result_type='json')
    check_pass = check_api(json_result, dict, dic={'sta': 0})
    logger.debug(check_pass)
    if check_pass != STATUS_OK:
        return check_pass
    return STATUS_OK


def check_forum(result, result_type, dic):
    check_pass = check_api(result, result_type, dic=dic)
    logger.debug(check_pass)
    if check_pass != STATUS_OK:
        return check_pass
    doc_id = result['vg'][0]['d'][0]['id']
    #API
    doc_url = FORUM_VW_POSTS_FORMAT % doc_id
    json_result = _request_url(doc_url, result_type='json')
    check_pass = check_api(json_result, dict, dic={'sta': 0})
    logger.debug(check_pass)
    if check_pass != STATUS_OK:
        return check_pass
    return STATUS_OK

def check_webzine_addon(result, result_type, number, cmp_func, env):
    check_pass = check_api(result, result_type, number=number, cmp_func=cmp_func)
    logger.debug(check_pass)
    if check_pass != STATUS_OK:
        return check_pass
    ch_id = result[0]['ID']
    logger.debug(ch_id)
    v4_columns_format = globals()['%s_V4_COLUMNS_FORMAT' % env]
    v4_columns_url = v4_columns_format % ch_id
    json_result = auth_request(v4_columns_url)
    if json_result['ID'] != ch_id:
        return STATUS_ERROR
    v3_columns_format = globals()['%s_V3_COLUMNS_FORMAT' % env]
    v3_columns_url = v3_columns_format % ch_id
    json_result = auth_request(v3_columns_url)
    check_pass = check_api(result, result_type, number=1, cmp_func=gte)
    logger.debug(check_pass)
    if check_pass != STATUS_OK:
        return check_pass
    return STATUS_OK


IDS = {
        'opscn.api.addons': {
            'kwargs': {'result_type': dict, 'fields': ['items', 'last_modified']}},
        'opscn.api.1.builtins': {
            'kwargs': {'result_type': dict, 'fields': ['bookmarks', 'speedDials']}},
        'opscn.api.1.sections': {
            'kwargs': {'result_type': list, 'number': 7, 'cmp_func': equal}},
        'opscn.api.2.sections': {
            'kwargs': {'result_type': list, 'number': 7, 'cmp_func': equal}},
        'opscn.api.2.sections_test': {
            'kwargs': {'result_type': list, 'number': 6, 'cmp_func': equal}},
        'opscn.api.2.section': {
            'kwargs': {'result_type': list, 'number': 2, 'cmp_func': equal}},
        'opscn.api.1.novels': {
            'kwargs': {'result_type': dict, 'fields': ['url', 'items', 'title']}},
        'opscn.api.1.navigate': {
            'kwargs': {'result_type': dict, 'fields': ['sections', 'hotwords']}},
        'opscn.api.1.treasure': {
            'kwargs': {'result_type': list, 'number': 1, 'cmp_func': equal}},
        'opscn.api.2.treasure': {
            'kwargs': {'result_type': dict, 'fields': ['items', 'last_modified']}},
        'opscn.api.1.skins': {
            'kwargs': {'result_type': list, 'number': 1, 'cmp_func': gte}},
        'opscn.api.1.skin.promote': {
            'kwargs': {'result_type': dict, 'fields': ['skins', 'wallpapers', 'last_modified']}},
        'opscn.api.1.adverts': {
            'kwargs': {'result_type': list, 'number': 0, 'cmp_func': gte}},
        'opscn.api.1.search.cats': {
            'kwargs': {'result_type': list, 'number': 5, 'cmp_func': gte}},
        'opscn.api.2.search.cats': {
            'kwargs': {'result_type': list, 'number': 5, 'cmp_func': gte}},
        'opscn.api.1.search.hotwords': {
            'kwargs': {'result_type': dict, 'fields': ['categories', 'last_modified']}},
        'opscn.api.1.search.tracks': {
            'kwargs': {'result_type': dict, 'fields': ['tracks', 'last_modified']}},
        'opscn.api.1.desktop': {
            'kwargs': {'result_type': list, 'number': 2, 'cmp_func': gte}},
        'opscn.api.updateservice': {
            'kwargs': {'result_type': dict, 'fields': ['download_url']}},
        'opscn.api.2.updateservice': {
            'request': 'UPDATE',
            'kwargs': {'result_type': list, 'number': 0, 'cmp_func': gte}
            },
        'opscn.api.3.updateservice': {
            'request': 'UPDATE',
            'kwargs': {'result_type': list, 'number': 0, 'cmp_func': gte}
            },
        'opscn.api.4.updateservice': {
            'request': 'UPDATE',
            'kwargs': {'result_type': list, 'number': 0, 'cmp_func': gte}
            },
        'opscn.api.promolink': {
            'kwargs': {'result_type': list, 'number': 0, 'cmp_func': gte}},
        'opscn.api.splash': {
            'kwargs': {'result_type': list, 'number': 0, 'cmp_func': gte}},
        'opscn.api.subnag': {
            'kwargs': {'result_type': dict, 'fields': ['last_modified', 'categories', 'title']}},
        'opscn.service.1.weathers': {
            'kwargs': {'result_type': dict, 'fields': ['cityName', 'temNow']}},
        'webapps.api.1.webapps.cats': {
            'kwargs': {'result_type': dict, 'fields': ['categories']}},
        'webapps.api.1.webapps.subjects': {
            'kwargs': {'result_type': dict, 'fields': ['subjects']}},
        'webapps.api.1.webapps.apps': {
            'kwargs': {'result_type': dict, 'fields': ['apps']}},
        'opscn.api.1.topsite': {
            'kwargs': {'result_type': dict, 'fields': ['sites', 'last_modified']}},
        'opsen.api.addons': {
            'kwargs': {'result_type': dict, 'fields': ['items', 'lastModified']}},
        'opsen.api.1.builtins': {
            'kwargs': {'result_type': dict, 'fields': ['bookmarks', 'speedDials']}},
        'opsen.api.updateservice': {
            'kwargs': {'result_type': dict, 'fields': ['download_url']}},
        'opsen.api.2.updateservice': {
            'request': 'UPDATE',
            'kwargs': {'result_type': list, 'number': 0, 'cmp_func': gte}
            },
        'opsen.api.promolink': {
            'kwargs': {'result_type': list, 'number': 0, 'cmp_func': gte}},
        'opsen.api.1.webapp.notification': {
            'kwargs': {'result_type': dict, 'fields': ['last_modified', 'notifications']}},
        'opsen.api.1.topsite': {
            'kwargs': {'result_type': dict, 'fields': ['last_modified', 'sites']}},
        'opsen.api.1.modes': {
            'kwargs': {'result_type': dict, 'fields': ['last_modified', 'modes']}},
        'dzone.api.infostream': {
            'method': check_dzone_infostream,
            'kwargs': {'result_type': list, 'number': 1, 'cmp_func': gte}},
        'dzone.api.token': {
            'request': 'POST',
            'kwargs': {'result_type': dict, 'dic': {'sta': 0}}
            },
        'news.vw.gathers.news': {
            'method': check_news_vw_gathers_news,
            'kwargs': {'result_type': dict, 'fields': ['sta', 'vg'], 'dic': {'sta': 0}}},
        'hub.vw2.hub.hot': {
            'method': check_hub_vw2_hub_hot,
            'kwargs': {'result_type': list, 'number': 11, 'cmp_func': equal}},
        'hub.vw2.hub.widget': {
            'method': check_hub_vw2_hub_widget,
            'kwargs': {'result_type': dict, 'fields': ['news', 'posts', 'mt']}},
        'reader.vw2.sub.init': {
            'kwargs': {'result_type': dict, 'dic': {'sta': 0}}},
        'reader.vw2.sub.categories': {
            'method': check_reader_vw2_sub_categories,
            'kwargs': {'result_type': dict, 'dic': {'sta': 0}}},
        'reader.vw2.sources.contents': {
            'method': check_reader_vw2_sources_contents,
            'kwargs': {'result_type': dict, 'dic': {'sta': 0, 'dt': 4}}},
        'image.image': {
            'method': check_image,
            'response': 'binary',},
        'pics.vw.gathers.gallery': {
            'method': check_pics,
            'kwargs': {'result_type': dict, 'dic': {'sta': 0}}},
        'forum.vw.gathers.post': {
            'method': check_forum,
            'kwargs': {'result_type': dict, 'dic': {'sta': 0}}},
        'pnscn.notification.android.messages': {
            'kwargs': {'result_type': dict}},
        'pnscn.notification.android.message': {
            'kwargs': {'result_type': dict}},
        'en.columns.recommends': {
            'request': 'AUTH',
            'kwargs': {'result_type': list, 'number': 1, 'cmp_func': gte}},
        'en.v6.columns.featured': {
            'request': 'AUTH',
            'method': check_webzine_addon,
            'kwargs': {'result_type': list, 'number': 1, 'cmp_func': gte, 'env': 'EN'}},
        'cn.columns.recommends': {
            'request': 'AUTH',
            'kwargs': {'result_type': list, 'number': 1, 'cmp_func': gte}},
        'cn.v6.columns.featured': {
            'request': 'AUTH',
            'method': check_webzine_addon,
            'kwargs': {'result_type': list, 'number': 1, 'cmp_func': gte, 'env': 'CN'}},
}


def handle(api):
    try:
        api_info = IDS[api]
        api_url = 'url_' + api.replace('.', '_')
        url = globals()[api_url]
        if 'request' not in api_info or api_info['request'] == 'GET':
            if 'response' not in api_info or api_info['response'] == 'json':
                json_result = _request_url(url, result_type='json')
                if 'method' not in api_info:
                    return check_api(json_result, **api_info['kwargs'])
                else:
                    return api_info['method'](json_result, **api_info['kwargs'])
            elif api_info['response'] == 'binary':
                result = _request_url(url)
                return api_info['method'](result)
        elif api_info['request'] == 'UPDATE':
            data_url = 'data_' + api.replace('.', '_')
            data_value = globals()[data_url]
            data_str = json.dumps(data_value)
            json_result = _request_url(url, data_str, result_type='json')
            if 'method' not in api_info:
                return check_api(json_result, **api_info['kwargs'])
            else:
                return api_info['method'](json_result, **api_info['kwargs'])
        elif api_info['request'] == 'POST':
            data_url = 'data_' + api.replace('.', '_')
            data_value = globals()[data_url]
            data_str = urllib.urlencode(data_value)
            json_result = _request_url(url, data_str, result_type='json', headers=None)
            if 'method' not in api_info:
                return check_api(json_result, **api_info['kwargs'])
            else:
                return api_info['method'](json_result, **api_info['kwargs'])
        elif api_info['request'] == 'AUTH':
            json_result = auth_request(url)
            if 'method' not in api_info:
                return check_api(json_result, **api_info['kwargs'])
            else:
                return api_info['method'](json_result, **api_info['kwargs'])

    except urllib2.URLError, e:
        if hasattr(e, 'code') and e.code == 304:
            return STATUS_OK
        else:
            logger.debug(url)
            logger.exception(e)
        return STATUS_DISASTER
    except Exception, e:
        logger.exception(e)
        return STATUS_ERROR


api = sys.argv[1]
print handle(api)


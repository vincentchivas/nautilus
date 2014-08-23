import logging
from dolphinop.db import cursor_to_array
from dolphinop.service.views import json_response
from dolphinop.service.models import zdb
from dolphinop.service.errors import parameter_error
import urlparse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from datetime import datetime
import urllib
import urllib2
import simplejson
import hashlib
import re

logger = logging.getLogger('dolphinop.service')
coll = 'promotion'
ad_base_info = {
    'developer': 'app_developer',
    'app_type': 'app_type',
    'size': 'app_size',
    'description': 'detail_description',
    'shortDescription': 'short_description',
    'iconPath': 'icon',
    'downloadUrl': 'download_url',
    'title': 'title',
    'sid': 'sid',
}

ad_track_info = {
    'clickUrl': 'click_url',
    'categoryName': 'category',
}

lan_code = {
    'en-ca': 'eng',
    'en-au': 'aus',
    'en-gb': 'eng',
    'en-us': 'eng',
    'en-ie': 'eng',
    'en-nz': 'eng',
    'en-ph': 'fil',
    'fr-fr': 'fre',
    'de-de': 'ger',
    'ko-kr': 'kor',
    'vi-vn': 'vie',
    'zh-hk': 'chi',
    'zh-mo': 'chi',
    'zh-sg': 'chi',
    'zh-tw': 'chi',
    'zh-cn': 'chi',
    'gu-in': 'inc',
    'ja-jp': 'jpn',
    'ms-my': 'may',
    'mn-mn': 'mon',
    'pl-pl': 'pol',
    'ru-ru': 'rus',
    'pt-pt': 'por',
    'pt-br': 'por',
    'es-es': 'spa',
    'th-th': 'eng',
    'ur-pk': 'eng',
}

country_code = {
    'en-ca': 'CAN',
    'en-au': 'AUS',
    'en-gb': 'GBR',
    'en-us': 'USA',
    'en-ie': 'IRL',
    'en-nz': 'NZL',
    'en-ph': 'PHL',
    'fr-fr': 'FRA',
    'de-de': 'DEU',
    'ko-kr': 'KOR',
    'vi-vn': 'VNM',
    'zh-hk': 'HKG',
    'zh-mo': 'MAC',
    'zh-sg': 'SGP',
    'zh-tw': 'TWN',
    'zh-cn': 'CHN',
    'gu-in': 'IND',
    'ja-jp': 'JPN',
    'ms-my': 'MYS',
    'mn-mn': 'MNG',
    'pl-pl': 'POL',
    'ru-ru': 'RUS',
    'pt-pt': 'PRT',
    'pt-br': 'BRA',
    'es-es': 'ESP',
    'th-th': 'THA',
    'ur-pk': 'PAK',
}

ad_filter_info = ['install_limits', 'remain_points', 'targets',
                  'sid', 'cpc', 'points', 'expression', 'campaign_id']


def _get_loca(request):
    request_meta = request.META
    acc_lan = request_meta['HTTP_ACCEPT_LANGUAGE'].lower()
    ua = request_meta['HTTP_USER_AGENT'].lower()
    lan = re.search(
        r"en-ca|en-au|en-gb|en-us|en-ie|en-nz|en-ph|fr-fr|de-de|ko-kr|vi-vn|zh-hk|zh-mo|zh-sg|zh-tw|zh-cn|gu-in|ja-jp|ms-my|mn-mn|pl-pl|ru-ru|pt-pt|pt-br|es-es|th-th|ur-pk", ua)
    if lan == None:
        lan = re.search(
            r"en-ca|en-au|en-gb|en-us|en-ie|en-nz|en-ph|fr-fr|de-de|ko-kr|vi-vn|zh-hk|zh-mo|zh-sg|zh-tw|zh-cn|gu-in|ja-jp|ms-my|mn-mn|pl-pl|ru-ru|pt-pt|pt-br|es-es|th-th|ur-pk", acc_lan)
    dt = re.search(r'android.*?;', ua)
    osv = re.search(r'\d\.\d?', dt.group()) if dt else None
    return {'lan': lan, 'dt': dt, 'osv': osv}


def _filter_ads(paras):
    tmp_lan = paras['lan'].group()
    language = lan_code[tmp_lan]
    country = country_code[tmp_lan]
    version = paras['osv'].group() if paras['osv'] else 0
    coll = {}
    coll['targets.country'] = country
    #coll['targets.language'] = language
    coll['targets.version'] = version
    return coll


def _divide_ads(orginal_datas):
    ad_base = []
    ad_track = {}
    ad_filter = []
    for i, item in enumerate(orginal_datas):
        track_key = hashlib.md5(item['sid'] + item['campaign_id']).hexdigest()
        ad_base.append({})
        ad_filter.append({})
        ad_track[track_key] = {}
        ad_base[i].update({
            'id': 'ad_%d' % i,
            'aid': track_key,
            'screenshots': [{'pic_url': img, 'thumbnails': img, 'order': j} for j, img in enumerate(item['imgs'])],
            'app_rating': float(item.get('rating_value') or 0),
            'pub_time': '',
            'display_order': '',
            'display_area': '',
            'app_ratingcount': 0,
        })

        ad_filter[i]['aid'] = track_key
        for key in ad_base_info:
            ad_base[i][ad_base_info[key]] = item.get(key)

        for key in ad_track_info:
            ad_track[track_key][ad_track_info[key]] = item.get(key)

        for key in ad_filter_info:
            ad_filter[i][key] = item.get(key)
    zdb.clear_list(('promotion_base', 'promotion_track', 'promotion_filter'))
    zdb.save_list(('promotion_base', 'promotion_track', 'promotion_filter'),
                  (ad_base, ad_track, ad_filter))
    zdb.valid_base()


def get_list(request, disp_type='trend'):
    tmp = _get_loca(request)
    if tmp['dt'] == None or tmp['lan'] == None:
        return []

    results = []
    cond = _filter_ads(tmp)
    ads_cur = zdb.get_list('promotion_filter', cond, {'aid': 1, '_id': 0})
    if ads_cur.count():
        obj = [i for i in ads_cur]
        uids = [item['aid'] for item in obj]
        result_cursors = zdb.get_list(
            'promotion_base', {'aid': {'$in': uids}, 'display_area': disp_type, 'is_edit': True}, {'_id': 0, 'display_area': 0})
    results = []
    titles = []
    for i in result_cursors:
        try:
            titles.index(i['title'])
            continue
        except Exception:
            titles.append(i['title'])
            results.append(i)

    return results


def check_adver(request):
    return render_to_response('check_ad.html', {}, context_instance=RequestContext(request))


@json_response
def active_track(request):
    try:
        request_post = request.POST
        org_refer = request_post.get('ref')
        android_id = request_post.get('did')
        time = datetime.now().strftime('%y-%m-%d %H:%M:%S')
        lc = request_post.get('lc')
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        logger.info('%s;%s;%s;%s' % (org_refer, android_id, lc, ip))

        refer = org_refer.lower()
        if refer and android_id:
            try:
                qs = urlparse.parse_qs(refer)
                src = qs.get('utm_source', [])
                src = src[0] if len(src) else 'other'
            except Exception:
                if refer.find('appflood', 0) != -1:
                    src = 'appflood'
                else:
                    src = 'other'
            data = {'did': android_id, 'refer': org_refer, 'date':
                    time, 'ip': ip, 'src': src, 'is_new': True, 'lc': lc}
            logger.debug(data)
            zdb.save_list(('promotion_active',), (data,))
            return 1
        return 0
    except Exception, e:
        logger.info(e)
        return 0


@json_response
def edit_get(request):
    results = zdb.get_list('promotion_base', {}, {'_id': 0})
    tracks = zdb.get_list('promotion_sent_log', {}, {'_id': 0})
    return {'items': cursor_to_array(results), 'track_count': tracks.count()}


@json_response
def edit_sent(request):
    request_post = request.POST
    edit_len = request_post.get('len', 0)
    if edit_len:
        edit_keys = request_post.get('keys', '')
        edit_datas = request_post.get('datas', '')
        edit_keys = simplejson.loads(edit_keys) if edit_keys else []
        edit_datas = simplejson.loads(edit_datas) if edit_datas else []
        for i, item in enumerate(edit_keys):
            zdb.update_list('promotion_bank',
                            {'sid': item}, edit_datas[i], upsert=True)
            zdb.update_list('promotion_base', {'sid': item}, edit_datas[i])
        return 'ok'
    return 'fail'


def track(request):
    request_get = request.GET
    logger.debug('receive_track')
    target_url = request_get.get('target', '')
    target_url = urllib.unquote(
        target_url.encode('utf-8')).decode("utf-8") if target_url else False
    if target_url:
        target = HttpResponse("", status=302)
        target['Location'] = target_url
    else:
        target = HttpResponseRedirect(request.META['HTTP_REFERER'])
    tmp = _get_loca(request)
    if tmp['dt'] == None or tmp['lan'] == None:
        return target

    tmp_lan = tmp['lan'].group()
    cc = country_code[tmp_lan]
    lan = lan_code[tmp_lan]
    dt = 'PHONE'
    osv = tmp['osv'].group()
    did = request_get.get('did', '')
    a_uid = request_get.get('aid')
    track_match = zdb.get_list('promotion_track', {})
    now_date = datetime.now().strftime('%y_%m_%d')
    logger.debug(a_uid)
    body = None
    if track_match.count():
        d = {
            'country': cc,
            'version': osv,
            'device_type': dt,
            'language': lan,
        }
        track_match = track_match[0]
        if body:
            click_track = []
            for i in body:
                tmp_match = track_match[i]
                d['Category'] = tmp_match['category']
                click_track.append({
                    'aid': did,
                    'sent_url': tmp_match['click_url'],
                    'd': d,
                    'date': now_date,
                })
            zdb.save_list(('promotion_sent',), (click_track,))
            logger.debug('receive %d track body:%s' % (i, body))

        elif a_uid:
            tmp_match = track_match[a_uid]
            d['Category'] = tmp_match['category']
            click_track = {
                'aid': did,
                'sent_url': tmp_match['click_url'],
                'd': d,
                'date': now_date,
            }
            zdb.save_list(('promotion_sent',), (click_track,))
            logger.debug('receive one track %s' % (click_track,))

    return target


@json_response
def get_ad_list(request):
#    try:
    respond = urllib2.urlopen(
        'http://partner.appflood.com/json_campaign_list?app_key=5XZtEOsUgAvdeROy')
    respond = respond.read()
    results = simplejson.loads(respond) if respond else {'total_count': 0}
    if results['total_count']:
        _divide_ads(results['items'])
        return 'ok'
    else:
        return 'error'

#    except Exception,e:
#        print e
#        return 'error'


@json_response
def sent_event(request):
    events = zdb.get_list('promotion_sent', {})
    suc_items = []
    suc_keys = []
    err_item = []
    n = 100
    logger.debug('it works')
    if events.count():
        i = 0
        for item in events:
            if i >= n:
                break
            try:
                d = re.sub(r'\s', '', simplejson.dumps(item['d']))
                sent_url = '%s&aid=%s&d=%s' % (
                    item['sent_url'], item['aid'], d)
                logger.debug(sent_url)
                respond = urllib2.urlopen(sent_url)
                result = respond.read()
                logger.debug(result)
                if result == '1':
                    suc_keys.append(item['_id'])
                    suc_items.append(item)
                i += 1
            except Exception, e:
                err_item.append(item)
                logger.info('sent ad %s,except%s' % (item['sent_url'], e))

        zdb.delete_item('promotion_sent', {'_id': {'$in': suc_keys}})
        zdb.save_list(('promotion_sent_log', 'promotion_sent_fail'),
                      (suc_items, err_item))
    return 'success sent %d' % len(suc_items)

#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On Dec 21, 2012
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import sys
import logging
import time
from django.conf import settings
from django.views.decorators.http import require_GET
from django.http import HttpResponseRedirect
from dolphinop.service.views import response_json
from dolphinop.service.errors import parameter_error, internal_server_error
from dolphinop.service.models import advertdb
from dolphinop.service.utils.iptable import get_ip_info

from dolphinop.service.utils.content import BASE_PARAS, RULE_ORIGINIZE, ALL_FLAG, OPERATORS, OTHER, now

logger = logging.getLogger('dolphinop.service')


def adapt_ad(ad, cid, pid):
    url = 'http://' + settings.DOMAIN + \
        '/api/1/advert.json?cid=%s&iid=%s&uid=%d' % (cid, pid, ad['id'])
    result_ad = {
        'title': ad['title'],
        'url': url,
        'weight': ad['weight'],
        'images': ad['images'],
    }
    if 'author' in ad:
        result_ad['author'] = ad['author']
    if 'summary' in ad:
        result_ad['summary'] = ad['summary']
    return result_ad


def get_mnc_by_ip(ip):
    mnc = None
    try:
        isp_map = {
            u'移动': u'00',
            u'联通': u'01',
            u'移动': u'02',
            u'电信': u'03',
        }
        ipinfo = get_ip_info(ip)
        if ipinfo and 'isp' in ipinfo and ipinfo['isp'] in isp_map:
            mnc = isp_map[ipinfo['isp']]
    except Exception, e:
        logger.exception(e)
    return mnc


@require_GET
def show_adverts(request):
    try:
        query = request.GET
        ip = request.META['REMOTE_ADDR']
        args = {
            'pn': query.get('pname') or query.get('pn'),
            'cid': query.get('cid'),
            'pid': query.get('iid'),
            'src': query.get('src'),
            'op': query.get('mnc') or query.get('op') or get_mnc_by_ip(ip),
            'vn': query.get('vn'),
            'iid': query.get('iid'),
            'time_valid': True,
        }
        """
        package = query.get('pname')
        pn = query.get('pn')
        package = package or pn
        cid = query.get('cid')
        pid = query.get('iid')
        source = query.get('src')
        mnc = query.get('mnc')
        operator = query.get('op')
        version = query.get('vn')
        if mnc:
            operator = mnc
        #if not operator:
        #    operator = get_mnc_by_ip(ip)
            #if not operator:
            #    operator = OTHER
        """
        if args['op'] not in OPERATORS:
            args['op'] = OTHER

    except Exception, e:
        logger.warning(e)
        return parameter_error(request, e)
    try:
        result = []
        cond = {}
        cond_rule = RULE_ORIGINIZE
        for key, value in args.items():
            if key in cond_rule and value is not None:
                match = cond_rule[key]
                if not match[1]:
                    cond.update(eval(match[0]))
                else:
                    cond.update(eval(match[0] % (value, value))
                                if match[1] == 2 else eval(match[0] % value))
        """
        cond = {
                'operators': operator,
                'valid_time': {'$lte': now},
                'invalid_time': {'$gte': now},
        }
        if package is not None:
            cond['package'] = package
        if source is not None:
            cond['sources.include'] = {'$in': [source, ALL_FLAG]}
            cond['sources.exclude'] = {'$ne': source}
        if version is not None:
            version = int(version)
            cond['min_version'] = {'$lte': version}
            cond['max_version'] = {'$gte': version}
        """
        cid = args['cid']
        pid = args['pid']
        print cond
        if pid is not None:
            cond['position'] = '%s-%s' % (cid, pid)
            adverts = advertdb.get_adverts(cond)
            for ad in adverts:
                result_ad = adapt_ad(ad, cid, pid)
                result.append(result_ad)
        else:
            cond['position'] = {'$regex': r'%s-\d+' % cid}

            adverts = advertdb.get_adverts(cond)
            ad_dict = {}
            for ad in adverts:
                for posit in ad['position']:
                    ad_pid = posit.split('-')[1]
                    result_ad = adapt_ad(ad, cid, ad_pid)
                    if ad_pid in ad_dict:
                        ad_dict[ad_pid].append(result_ad)
                    else:
                        ad_dict[ad_pid] = [result_ad]
            if ad_dict:
                for ad_pid in ad_dict.keys():
                    result.append(
                        {'iid': int(ad_pid), 'data': ad_dict[ad_pid]})
    except Exception, e:
        logger.error(e)
        return internal_server_error(request, e, sys.exc_info())
    return response_json(result)


@require_GET
def show_advert(request):
    try:
        query = request.GET
        cid = query.get('cid')
        pid = query.get('iid')
        uid = int(query.get('uid'))

    except Exception, e:
        logger.warning(e)
        return parameter_error(request, e)
    try:
        cond = {
            'position': str(cid) + '-' + str(pid),
            'id': uid,
        }

        advert = advertdb.get_advert(cond)
        if advert:
            ip = request.META['REMOTE_ADDR']
            src = query.get('src')
            track_data = {
                'id': uid,
                'cid': cid,
                'pid': pid,
                'ip': ip,
                'src': src,
                'time': time.time(),
            }
            advertdb.save_advert_track(track_data)
        return HttpResponseRedirect(advert['link'])
    except Exception, e:
        logger.error(e)
        return internal_server_error(request, e, sys.exc_info())

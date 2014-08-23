# -*- coding:utf-8 -*-
'''
Copyright (c) 2012 Baina Info Inc. All rights reserved.
@Author : Jun Wang
@Date : 2012-6-14
'''
import urllib2
from datetime import datetime
from django.utils import simplejson
from django.http import HttpResponse, HttpResponseNotFound, \
    HttpResponseServerError
from dolphinopadmin.promotionlink.admin import *

logger = logging.getLogger("dolphinopadmin.content")

_DEV = 'dev'
_LOCAL = 'local'
_CHINA = 'china'
_EC2 = 'ec2'


def response_json(obj):
    content = simplejson.dumps(obj, ensure_ascii=False)
    response = HttpResponse(
        content, content_type='application/json; charset=utf-8')
    '''
    if isinstance(content, unicode):
        response['Content-Length'] = len(content.encode('utf-8'))
    else:
        response['Content-Length'] = len(content)
    '''
    return response


def error404(request):
    return HttpResponseNotFound(""""
Sorry, we can't find what you want...
""")


def error500(request):
    return HttpResponseServerError("""
Sorry, we've encounter an error on the server.<br/> Please leave a feedback <a href="/feedback.htm">here</a>.
""", content_type="text/html; charset=utf-8")


def get_ads(request):
    base_url = "http://ex.mobmore.com/api/data?slot_id="
    slot_ids = ['40181']
    product = Product.objects.get(pid=15)
    for slot_id in slot_ids:
        url = base_url + slot_id
        handle = urllib2.urlopen(url)
        dic_str = handle.readline()
        dic = simplejson.loads(dic_str)
        for promoter in dic['promoters']:
            plink = Plink()
            plink.title = promoter['title']
            plink.url = promoter['url_down']
            plink.url_imp = promoter['url_imp']
            plink.product = product
            plink.platform = promoter['platform']
            plink.min_version = 0
            plink.max_version = 0
            plink.source = 'mobmore'
            plink.sid = dic['sid']
            plink.slot_id = int(slot_id)
            plink.update_time = datetime.now()
            plink.is_upload_dev = False
            plink.is_upload_local = False
            plink.is_upload_china = False
            plink.is_upload_ec2 = False
            prolinks = Plink.objects.filter(title=promoter['title'])
            if len(prolinks) == 0:
                plink.save()
        handle.close()
    return response_json(dic)

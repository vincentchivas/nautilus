# -*- coding:utf-8 -*-
'''
Copyright (c) 2012 Baina Info Inc. All rights reserved.
@Author : Jun Wang
@Date : 2012-5-23
'''
from django.utils import simplejson
from django.http import HttpResponse, HttpResponseNotFound, \
    HttpResponseServerError
from dolphinopadmin.content.admin import *

logger = logging.getLogger("dolphinopadmin.admin")

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


def _upload_online(queryset, server, func_name):
    message = ''
    mongo_pk = {}
    try:
        for item in queryset:
            mongo_data = item.content_dict()
            mongo_pk['id'] = mongo_data['id']
            mongo_pk['platform'] = mongo_data['platform']
            func_name(mongo_pk, mongo_data, server)
        update_selected(server, queryset, 1)
        message += 'Upload %d %s to %s successfully!\n' % (queryset.count(),
                                                           func_name.__name__, server)
    except Exception, e:
        logger.error('%s Exception:%s' % (message, e))


def section_upload(request):
    re = []
    section_list = Android_Section.objects.exclude(layout=1).order_by('order')
    _upload_online(section_list, _LOCAL, update_section)
    _upload_online(section_list, _CHINA, update_section)
    sections = [item.content_dict() for item in section_list]
    re.extend(sections)

    section_list = iPhone_Section.objects.exclude(layout=1).order_by('order')
    _upload_online(section_list, _LOCAL, update_section)
    _upload_online(section_list, _CHINA, update_section)
    sections = [item.content_dict() for item in section_list]
    re.extend(sections)

    section_list = wPhone_Section.objects.exclude(layout=1).order_by('order')
    _upload_online(section_list, _LOCAL, update_section)
    _upload_online(section_list, _CHINA, update_section)
    sections = [item.content_dict() for item in section_list]
    re.extend(sections)
    return response_json(re)


def insert_item(request):
    data = request.GET
    url = data.get('url', '')
    title = data.get('title', '')
    #url_list = data.getlist('url')
    #title_list = data.getlist('title')
    # for url, title in zip(url_list, title_list):
    #    a_item = Android_Item()
    #    a_item.url = url
    #    a_item.title = title
    #    a_item.save()
    a_item = Android_Item()
    a_item.url = url
    a_item.title = title
    a_item.save()

    i_item = iPhone_Item()
    i_item.url = url
    i_item.title = title
    i_item.save()
    return response_json([])

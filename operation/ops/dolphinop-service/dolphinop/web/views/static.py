# Copyright (c) 2011 Baina Info Inc. All rights reserved.
# @author: Chen Qi
# date:2011-11-20
# email:qchen@bainainfo.com

import logging
from django.conf import settings
from django.shortcuts import render_to_response
from django.http import HttpResponse
from dolphinop.service.errors import parameter_error
from dolphinop.decorator import auto_match_locale
from dolphinop.web import models

logger = logging.getLogger('dolphinop.web')

_CLIENT_ARGS = settings.CLIENT_ARGS

_FIELDS_FULL = {
    '_id': 0,
    'html': 1,
}

_FIELDS_LASTMODIFIED = {
    '_id': 0,
    'timestamp': 1
}


def _build_condition(request, page_path):

#    name= page_path.split(".",1)[0]
    name = page_path
    try:
        os = request.GET.get('os', None)
        locale = request.GET.get('l', None)
    except KeyError, e:
        logger.debug('%s %s' % (request.build_absolute_uri(), e))
    if os not in _CLIENT_ARGS['os']:
        return parameter_error(request, 'os')
    cond = {}
    for name, value in zip(('name', 'os', 'locale'), (name, os, locale)):
        if value:
            cond[name] = value
    return cond


@auto_match_locale
def page(request, page_path='defaults'):

    cond = _build_condition(request, page_path)

    if isinstance(cond, HttpResponse):
        return cond
    item = models.get_item(cond, _FIELDS_FULL)
    if item and 'html' in item:
        html = item['html']
        return HttpResponse(html)
    else:
        logger.debug("[page]:item or html Not found in item:cond:%s", cond)
        return render_to_response("404.html")

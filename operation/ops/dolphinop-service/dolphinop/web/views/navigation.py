# -*- coding:utf-8 -*-
import logging
from django.shortcuts import render_to_response
from django.template import RequestContext
from dolphinop.web import models
from dolphinop.web.user_agent import package_request_infos
from dolphinop.decorator import auto_match_locale

logger = logging.getLogger('dolphinop.web')

_OS = {
    'android': 'Android',
    'ipad': 'iPad',
    'iphone': 'iPhone',
    'unknown': 'unknown',
    'pc': 'unknown'
}


@package_request_infos
@auto_match_locale
def navigation(request):
    os = 'iPad'
    locale = 'zh_CN'
    navigation = models.get_navigation(os, locale)

    if not navigation:
        return render_to_response('404.html')

    return render_to_response('navigation/ipad_data.html',
                              {'promotion': navigation['promotions'][0], 'features':
                               navigation['feature_sites'], 'categories':
                                  navigation['categories'], 'ads': navigation['ads']}, context_instance=RequestContext(request))


def appcache(request):
    return render_to_response('navigation/ipad.appcache',
                              mimetype="text/cache-manifest",
                              context_instance=RequestContext(request))

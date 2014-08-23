import logging
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from dolphinop.web import models
from dolphinop.web.user_agent import package_request_infos
from dolphinop.decorator import auto_match_locale

logger = logging.getLogger('dolphinop.web')

TEMPLATES = {
    "iPhone": "/pages/feedback_ios_ok.html",
    "iPad": "/pages/feedback_ios_ok.html",
    "Android": "/pages/feedback_ok.html",
    "default": "/pages/feedback_ok.html"
}
ONLINE = 'com.dolphin.browser.cn'
TUNA = 'com.dolphin.browser.tuna'
WHITE_VERSION = 500
DEFALUT = 'unknown'


@package_request_infos
@auto_match_locale
def feedback(request):
    if request.method == "GET":
        # turn to feedback.html
        try:
            query = request.GET
            os = query.get('os')
            locale = query.get('l')
            package = query.get('pn', DEFALUT)
            source = query.get('src', DEFALUT)
            version = query.get('vn', '0')
            try:
                version = int(version)
            except:
                version = 0
            product = 'other'
            if package == ONLINE:
                product = 'tunny'
            elif package == TUNA:
                product = 'tuna'
                if version >= WHITE_VERSION:
                    product = 'white'

        except KeyError, e:
            logger.debug('%s %s' % (request.build_absolute_uri(), e))
        if os == "iPhone" or os == "iPad":
            # iPhone or iPad
            return render_to_response('feedback_ios.html',
                                      {'os': os, 'locale': locale}, context_instance=RequestContext(request))
        else:
            # Android
            return render_to_response('feedback.html',
                                      {'os': os, 'locale': locale, 'product': product,
                                       'package': package, 'source': source, 'version': version},
                                      context_instance=RequestContext(request))
    else:
        # Save feedback informatoin
        form = request.POST
        try:
            os = form.get('os', '')
            locale = form.get('l', '')
            name = form.get('name', 'dolphin-user')
            package = form.get('pn', DEFALUT)
            source = form.get('src', DEFALUT)
            version = form.get('vn', '0')
            contact_info = form['contact_info']
            feedback_type = form['feedback_type']
            message = form['message']
            product = form.get('product', 'other')
            try:
                version = int(version)
            except:
                version = 0
        except KeyError, e:
            logger.debug('%s %s' % (request.build_absolute_uri(), e))
        models.save_feedback(request.META['REMOTE_ADDR'], name,
                             contact_info, feedback_type, message, os, locale, product, package, source, version)
        template = TEMPLATES[os] if os in TEMPLATES else TEMPLATES["default"]
        return HttpResponseRedirect(template)


def feedback_ok(request, os):
    if os == 'ios':
        return render_to_response('feedback_ios_ok.html', context_instance=RequestContext(request))
    else:
        return render_to_response('feedback_ok.html', context_instance=RequestContext(request))

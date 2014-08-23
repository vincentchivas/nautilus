# Copyright (c) 2011 Baina Info Inc. All rights reserved.
# author:kunli
# date:2011-11-19
# email:kunli@bainainfo.com
import re
import urllib2
import logging
import simplejson
from django.conf import settings
try:
    from django.contrib.gis.geoip import GeoIP
except Exception, e:
    from django.contrib.gis.utils import GeoIP

# FIXME: these info need persist in db and easy to update
import time

logger = logging.getLogger('dolphinop.web')

geoip = GeoIP(path='/usr/local/lib/python2.7/dist-packages/GeoLiteCity.dat')

_SUPPORT_LOCALE = ['zh_CN', 'en_US', 'ja_JP']
_RECOMMEND_LOCALE = {'zh': 'zh_CN', 'en': 'en_US', 'ja': 'ja_JP'}
_DEFAULT_LOCALE = settings.DEFAULT_LANGUAGE
_LOCALE_REG = re.compile('(\w+)[-_](\w+)')


def match_location(func):

    def get_country(*args, **kwargs):
        request = args[0]
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        if ip != '0.0.0.0':
            try:
                content_dict = geoip.city(ip)
                if not content_dict:
                    content = urllib2.urlopen(
                        'http://www.telize.com/geoip/%s?callback=getgeoip' % ip, timeout=5).read()
                    content_filter = str(content[9:-3])
                    content_dict = simplejson.loads(content_filter)

                if content_dict:
                    kwargs.update({'country': content_dict['country_code3']})
            except Exception, e:
                logger.error(e)

        return func(*args, **kwargs)
    return get_country


def auto_match_locale(func):
    """
    Auto select best match locale support by webzine if locale in query string
    """
    def auto_match(*args, **kwargs):
        request = args[0]
        locale = request.GET.get('l', None)
        if locale:
            query_dict = request.GET.copy()
            locale = locale.replace('-', '_')
            match = _LOCALE_REG.search(locale)
            if match:
                language = match.group(1)
                geo = match.group(2)
                standard_locale = '_'.join([language, geo.upper()])
                if standard_locale in _SUPPORT_LOCALE:
                    query_dict['l'] = standard_locale
                elif language in _RECOMMEND_LOCALE:
                    query_dict['l'] = _RECOMMEND_LOCALE[language]
                else:
                    query_dict['l'] = _DEFAULT_LOCALE
            request.GET = query_dict
        return func(*args, **kwargs)
    return auto_match


def perf_logging(func):
    """
    Record the performance of each method call.

    Also catches unhandled exceptions in method call and response a 500 error.
    """
    def pref_logged(*args, **kwargs):
        argnames = func.func_code.co_varnames[:func.func_code.co_argcount]
        fname = func.func_name
        req = args[0]
        msg = '%s %s -> %s(%s)' % (req.method, req.META['PATH_INFO'], fname, ','.join('%s=%s' %
                                                                                      entry for entry in zip(argnames[1:], args[1:]) + kwargs.items() + req.GET.items()))
        try:
            startTime = time()
            retVal = func(*args, **kwargs)
            endTime = time()
            pref_logger.debug('%s <- %s ms.' %
                              (msg, 1000 * (endTime - startTime)))
        except Exception, e:
            # maybe it is not necessary to log exec time when exception occur
            """
            endTime = time()
            logger.error('%s error in %s ms.' % (msg, endTime - startTime), exc_info=1)
            """
            return errors.server_error(e)
        return retVal
    return pref_logged

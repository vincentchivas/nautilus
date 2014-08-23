import logging
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'dolphinop.settings'
from django.conf import settings
from uwsgidecorators import timer
from dolphinop.spider.hotwords import update_hotwords, update_search, update_news
from dolphinop.spider.weather import update_cities_weather
from dolphinop.spider.pm import update_cities_pm
from dolphinop.utils import get_ip_address

logger = logging.getLogger('dolphinop.service')

CRON_SERVER = ['china']
SERVER_IP = get_ip_address()


@timer(60, target='spooler')
def cron_news(sinnum):
    try:
        if settings.SERVER in CRON_SERVER and settings.DIFF_IP not in SERVER_IP:
            logger.info('cron news start')
            update_news()
            logger.info('cron news end')
    except Exception, e:
        logger.exception(e)


@timer(300, target='spooler')
def cron_search(sinnum):
    try:
        if settings.SERVER in CRON_SERVER and settings.DIFF_IP not in SERVER_IP:
            logger.info('cron search start')
            update_hotwords()
            update_search()
            logger.info('cron search end')
    except Exception, e:
        logger.exception(e)


@timer(7200, target='spooler')
def cron_weather(sinnum):
    try:
        if settings.SERVER in CRON_SERVER and settings.DIFF_IP in SERVER_IP:
            logger.info('cron aqi  weather start')
            update_cities_weather()
            # update_cities_aqi()
            logger.info('cron aqi weather end')
    except Exception, e:
        logger.exception(e)


@timer(3600, target='spooler')
def cron_pm2d5(sinnum):
    try:
        if settings.SERVER in CRON_SERVER and settings.DIFF_IP in SERVER_IP:
            logger.info('cron pm2d5 start')
            update_cities_pm()
            logger.info('cron pm2d5 end')
    except Exception, e:
        logger.exception(e)

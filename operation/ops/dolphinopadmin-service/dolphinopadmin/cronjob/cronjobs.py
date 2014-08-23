import logging
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'dolphinopadmin.settings'
from django.conf import settings
from uwsgidecorators import timer
from dolphinopadmin.feedback.views import sync_feedbacks

logger = logging.getLogger('dolphinopadmin.admin')

CRON_SERVER = ['local', 'admin']


@timer(300, target='spooler')
def cron_feedback(sinnum):
    try:
        logger.info('cron feedback start')
        if settings.SERVER in CRON_SERVER:
            for server in settings.ENV_CONFIGURATION:
                sync_feedbacks(server)
        logger.info('cron feedback end')
    except Exception, e:
        logger.exception(e)

if __name__ == '__main__':
    try:
        cron_feedback(1)
        print 'done'
    except Exception, e:
        print e

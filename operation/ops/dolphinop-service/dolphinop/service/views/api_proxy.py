from dolphinop.service.errors import resource_not_exist
from dolphinop.service.utils.common_op import get_logger
from dolphinop.service.views import sms
from dolphinop.service.views import websitesnav
logger = get_logger('service')
def proxy(request, ser1, ser2):
    try:
        matchs = {
            'sms': [
                'switch',
                'matches',
                'feeds'
            ],
            'websitesnav': [
                'fetch',
            ]
        }
        if ser1 in matchs:
            if ser2 in matchs[ser1]:
                return eval('%s.%s(request)' % (ser1, ser2))

    except Exception, e:
        print e
        logger.exception(e)
    return resource_not_exist(request, ser1)

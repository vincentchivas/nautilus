from dolphinop.service.models import feedbackdb_en
from dolphinop.service.views import json_response
import datetime


@json_response
def save_feedback(request):
    request_get = request.GET
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    feedback_item = {
        'remote_address': ip,
        'contact_info': request_get.get('ci', ''),
        'message': request_get.get('fi', ''),
        'locale': 'en_US',
        'time': datetime.datetime.utcnow(),
        'sync': False
    }

    feedbackdb_en.save_feedback(feedback_item)

    return 'ok'

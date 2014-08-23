from django.utils import simplejson
from django.http import HttpResponse, HttpResponseNotFound, \
    HttpResponseServerError

DEFAULT_SOURCE = 'ofw'
ALL_FLAG = 'all_condition'
OTHER = 'other_condition'
OPERATORS = ['00', '01', '02', '03']
ALL_WEIGHT = 1
MATCH_WEIGHT = 100


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

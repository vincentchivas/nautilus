import os
import sys
import time
from dolphinop.db.base import MongodbStorage
from dolphinop.service.utils.common_op import get_logger, get_params, json_response, now, \
    parse_rule
from dolphinop.service.errors import internal_server_error, resource_not_modified
from django.http import HttpResponse as http
from django.views.decorators.http import require_POST
from dolphinop.service.utils.content import ALL_FLAG, BASE_PARAS, RULE_ORIGINIZE

LOGGER = get_logger('service')
SMS_DB = MongodbStorage()
setattr(SMS_DB, 'table', 'sms_listen')
SAVE_PATH = '/var/app/data/dolphinop-service/sms'


def _filter_fields(sections, fields):
    result = {}
    for section in sections:
        for key, value in section.items():
            if key in fields:
                result[key] = value
        return result


@json_response
def switch(request):
    try:
        self_fields = ('collect', 'pop', 'complete_close', 'interval')
        request_paras = get_params(request, 'get', BASE_PARAS)
        if isinstance(request_paras, http):
            return request_paras
        conn = {}
        for key, value in request_paras.items():
            if value is not None:
                match = RULE_ORIGINIZE[key]
                if match[1] == 1:
                    conn.update(eval(match[0] % value))
                else:
                    conn.update(eval(match[0] % (value, value)))
        results = SMS_DB.get_item(conn, {'_id': 0})

        results = parse_rule(results, ['src', 'lc'], None)

        if len(results) == 0:
            return resource_not_modified(request, 'msm')
        else:
            if self_fields:
                return _filter_fields(results, self_fields)
            return results[0]

    except Exception, e:
        LOGGER.exception(e)
        return internal_server_error(request, e, sys.exc_info())


@json_response
def matches(request):
    try:
        self_fields = ('keywords', 'mt', 'numbers')
        request_paras = get_params(request, 'get', BASE_PARAS)
        if isinstance(request_paras, http):
            return request_paras

        conn = {}
        for key, value in request_paras.items():
            if value:
                match = RULE_ORIGINIZE[key]
                if match[1] == 1:
                    conn.update(eval(match[0] % value))
                else:
                    conn.update(eval(match[0] % (value, value)))

        results = SMS_DB.get_item(conn, {'_id': 0})
        results = parse_rule(results, ['src', 'lc'], None)

        if len(results) == 0:
            return resource_not_modified(request, 'msm')
        else:
            if self_fields:
                return _filter_fields(results, self_fields)
            return results[0]

    except Exception, e:
        LOGGER.exception(e)
        return internal_server_error(request, e, sys.exc_info())


def _upload_file(files):
    if files:
        file_name = str(files)
        file_name = os.path.splitext(file_name)
        save_path = '%s/%s_%s%s' % (SAVE_PATH,
                                    file_name[0], int(time.time()), file_name[1])
        file_size = files.size
        destination = open(save_path, 'w+')
        for chunk in files.chunks():
            destination.write(chunk)
        destination.close()
        return (True, {'path': save_path, 'size': file_size})

    return (False,)


@require_POST
@json_response
def feeds(request):
    try:
        request_paras = get_params(request, 'post', BASE_PARAS)
        if isinstance(request_paras, http):
            return request_paras
        conn = {}
        for key, value in request_paras.items():
            if value:
                conn.update(eval("{'%s':'%s'}" % (key, value)))

        tmp = _upload_file(request.FILES['feeds'])
        if tmp[0]:
            conn.update({'file': tmp[1], 'date': str(now())})
            SMS_DB.upsert_item(conn, **{'table': 'sms_feeds'})
            return 1
        else:
            return 0

    except Exception, e:
        LOGGER.exception(e)
        return internal_server_error(request, e, sys.exc_info())

import sys
import time
import logging
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from dolphinop.service.utils import get_parameter_GET
from dolphinop.service.views import response_json
from dolphinop.service.utils.common_op import dup_by_key, normalize_result, rule_parse
from dolphinop.service.errors import parameter_error, internal_server_error, resource_not_modified
from dolphinop.service.models import adpdb

logger = logging.getLogger('dolphinop.service')


def _get_blocklist_rawdata(args, request):
    cond = {
        '_rule.packages': {'$in': [args['package_name']]},
        'last_modified': {'$gt': args['modify_time']}
    }
    sections = adpdb.get_update(cond)
    logger.info(sections)
    return resource_not_modified(request, 'adblocklist') if not len(sections) else response_json(sections[0])


def get_blocklist(request):
    args = {}
    args['package_name'] = get_parameter_GET(request, 'pn')
    args['modify_time'] = get_parameter_GET(
        request, 'mt', default=0, convert_func=int)

    for q in (args['package_name'], args['modify_time']):
        if isinstance(q, HttpResponse):
            return q
    return _get_blocklist_rawdata(args, request)

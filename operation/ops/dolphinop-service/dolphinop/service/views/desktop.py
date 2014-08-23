'''
Created on Feb 22, 2013

@author: fli
'''
import logging
from django.views.decorators.http import require_GET
from django.http import HttpResponse as http
from dolphinop.db.base import MongodbStorage
from dolphinop.service.views import response_json, ALL_FLAG, OTHER, OPERATORS, ALL_WEIGHT, MATCH_WEIGHT
from dolphinop.service.utils.content import  RULE_ORIGINIZE, DESKTOP_PARAS
from dolphinop.service.utils.common_op import  get_params, get_cond, filter_rule
from dolphinop.service.errors import parameter_error, resource_not_modified

logger = logging.getLogger('dolphinop.service')
DESKTOP_DB = MongodbStorage()
setattr(DESKTOP_DB, 'table', 'desktops')
DISPLAY_FIELDS = {
    '_id': 0,
    'data': 1,
    'sources': 1,
    'locales': 1,
    '_rule': 1,
}

@require_GET
def get_desktop(request):
    args = get_params(request, 'get', DESKTOP_PARAS)
    if isinstance(args, http):
        return args
    fields = ('pn', 'vn', 'op', 'src')
    if args['op'] not in OPERATORS:
        args['op'] = OTHER
    cond = get_cond(args, RULE_ORIGINIZE, fields)
    desktop_infos = DESKTOP_DB.get_item(cond, DISPLAY_FIELDS)
    if not desktop_infos:
        return resource_not_modified(request, 'desktop')
    desktop_infos = filter_rule(desktop_infos, {'sources':args['src'], 'locales':args['locale'], 'operators':args['op']}, {'min_version':True})
    if len(desktop_infos):
        return response_json(desktop_infos['data'])
    return resource_not_modified(request, 'desktop')

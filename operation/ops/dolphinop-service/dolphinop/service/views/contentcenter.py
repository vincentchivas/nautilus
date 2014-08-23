'''
Created on Feb 9, 2012

@author: fli
'''
import sys
import logging
from django.views.decorators.http import require_GET
from dolphinop.service.views import response_json
from dolphinop.service.utils import get_optional_parameter
from dolphinop.service.errors import parameter_error, internal_server_error, resource_not_modified
from dolphinop.service.models import contentdb
from dolphinop.utils import perf_logging

logger = logging.getLogger('dolphinop.service')

DEFAULT_PACKAGE = 'all:all'


@require_GET
@perf_logging
def sections(request):
    modified_time, error = get_optional_parameter(
        request, 'mt', default=None, formatter=long)
    if error:
        return error
    package_name = request.GET.get('pn', DEFAULT_PACKAGE)
    source = request.GET.get('src', 'ofw')
    try:
        section_infos = contentdb.get_section_by_package(
            package_name, source, modified_time, 'official')
    except Exception, e:
        logger.debug(e)
        return internal_server_error(request, e, sys.exc_info())
    if not section_infos:
        return resource_not_modified(request, 'sections', package_name=package_name, modified_time=modified_time)
    try:
        for item in section_infos:
            groups = item['groups']
            for group in groups:
                if "api_version" in group and group['api_version'] == 2:
                    item['groups'].remove(group)
    except Exception, e:
        logger.error(e)
        return internal_server_error(request, e, sys.exc_info())
    return response_json(section_infos)


@require_GET
@perf_logging
def sections2(request):
    modified_time, error = get_optional_parameter(
        request, 'mt', default=None, formatter=long)
    if error:
        return error
    package_name = request.GET.get('pn', DEFAULT_PACKAGE)
    source = request.GET.get('src', 'ofw')
    try:
        section_infos = contentdb.get_section_by_package(
            package_name, source, modified_time, 'official')
    except Exception, e:
        logger.error(e)
        return internal_server_error(request, e, sys.exc_info())
    if not section_infos:
        return resource_not_modified(request, 'sections', package_name=package_name, modified_time=modified_time)
    return response_json(section_infos)


@require_GET
def sections_test(request):
    modified_time, error = get_optional_parameter(
        request, 'mt', default=None, formatter=long)
    if error:
        return error
    package_name = request.GET.get('pn', DEFAULT_PACKAGE)
    source = request.GET.get('src', 'ofw')
    try:
        section_infos = contentdb.get_section_by_package(
            package_name, source, modified_time, 'test')
    except Exception, e:
        logger.error(e)
        return internal_server_error(request, e, sys.exc_info())
    if not section_infos:
        return resource_not_modified(request, 'sections', package_name=package_name, modified_time=modified_time)
    return response_json(section_infos)


@require_GET
def section2(request):
    '''
    Get section by layout id.
    '''
    modified_time, error = get_optional_parameter(
        request, 'mt', default=0, formatter=long)
    if error:
        return error
    layout, error = get_optional_parameter(request, 'id', default=None,
                                           formatter=long)
    try:
        layouts = request.GET.get('ids')
        layouts = layouts.split(',')
        layouts = map(int, layouts)
    except Exception, e:
        logger.warning(e)
        return parameter_error(request, 'layout id')

    package_name = request.GET.get('pn', DEFAULT_PACKAGE)
    source = request.GET.get('src', 'ofw')
    try:
        section_infos = []
        for layout in layouts:
            section = contentdb.get_section_by_layout(
                layout, package_name, source, modified_time, 'official')
            if section:
                section_infos.append(section)

    except Exception, e:
        logger.error(e)
        return internal_server_error(request, e, sys.exc_info())
    if not section_infos:
        return resource_not_modified(request, 'section')
    return response_json(section_infos)


@require_GET
def novels(request):
    package_name = request.GET.get('pn', DEFAULT_PACKAGE)
    source = request.GET.get('src', 'ofw')
    request_format = request.GET.get('format', 'html')
    title = request.GET.get('title', None)
    try:
        novel_info = contentdb.get_novels(package_name, source, title)
    except Exception, e:
        logger.debug(e)
        return internal_server_error(request, e, sys.exc_info())
    if request_format == 'json':
        return response_json(novel_info)
    return response_json(novel_info)

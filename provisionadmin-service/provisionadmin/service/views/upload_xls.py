# -*- coding: utf-8 -*-

import time
import os
import xlrd
import logging


from django.http import HttpResponse
from provisionadmin.model.i18n import LocalizationPicture
from provisionadmin.utils.json import json_response_ok, json_response_error
from provisionadmin.utils.respcode import DATA_ERROR
from provisionadmin.settings import STATIC_ROOT, CUS_TEMPLATE_DIR

logger = logging.getLogger('xls')


def upload_xls_file(request):
    '''
    try:
    '''
    if request.method == "GET":
        return HttpResponse(file(
            os.path.join(CUS_TEMPLATE_DIR, "upload_xls.html")).read())
    cur_time = int(time.time())
    appname = request.POST.get("appname", "mobi.mgeek.TunnyBrowser")
    xlsfile = request.FILES['xmlfile']
    # check file validation
    if xlsfile.name.endswith('.xls') or xlsfile.name.endswith('.xlsx'):
        xlsfilepath = os.path.join(STATIC_ROOT, "xml_%s.xls" % cur_time)
        xlsoutputfile = open(xlsfilepath, "wb")
        for chunk in xlsfile.chunks():
            xlsoutputfile.write(chunk)
        xlsoutputfile.close()
        xlsfiledir = os.path.splitext(xlsfilepath)[0]
        os.mkdir(xlsfiledir)

        ADAPTER_MAP_PATH = os.path.join(STATIC_ROOT, xlsfilepath)
        resource = load_resource_from_xls(ADAPTER_MAP_PATH)
        for resource_item in resource:
            LocalizationPicture.store_picture_info(appname, resource_item)
        return json_response_ok({})
    else:
        return json_response_error(
            DATA_ERROR, msg='upload file format error[%s]' % (xlsfile.name))


def load_resource_from_xls(xls_path):
    resource_list = []
    data = xlrd.open_workbook(xls_path)
    for sheet_name in data.sheet_names():
        table = data.sheet_by_name(sheet_name)
        nrows = table.nrows
        for row_index in range(nrows):
            resource_map = {}
            if row_index == 0:
                continue
            row_data = table.row_values(row_index)
            resource_map["picture_id"] = row_data[0]
            resource_map["name"] = row_data[1]
            resource_map["description"] = row_data[2]
            resource_list.append(resource_map)
    return resource_list

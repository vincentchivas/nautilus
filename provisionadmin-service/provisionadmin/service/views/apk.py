# -*- coding: utf-8 -*-

import time
import os
import subprocess
# import traceback
import logging
from provisionadmin.utils.json import json_response_ok, json_response_error
from provisionadmin.utils.respcode import DATA_ERROR
from django.http import HttpResponse, HttpResponseNotFound
from django.core.servers.basehttp import FileWrapper
from provisionadmin.decorator import exception_handler
from provisionadmin.settings import STATIC_ROOT, CUS_TEMPLATE_DIR
from provisionadmin.service.utils.adapter import init_adapter
from provisionadmin.service.utils.diff import diff_xml
from provisionadmin.service.utils.organize_values import merge_xml

logger = logging.getLogger('apk')


def upload(request):
    '''
    try:
    '''
    if request.method == "GET":
        return HttpResponse(file(
            os.path.join(CUS_TEMPLATE_DIR, "upload.html")).read())
    cur_time = int(time.time())
    platform = request.POST.get("platform", "Android")
    category = request.POST.get("category", "Branch")
    apkfile = request.FILES['apkfile']
    xmlfile = request.FILES['xmlfile']
    # check file validation
    if not apkfile.name.endswith('.apk') or not xmlfile.name.endswith('.zip'):
        return json_response_error(
            DATA_ERROR, msg='upload file format error[%s %s]' % (
                apkfile.name, xmlfile.name))
    if platform == "IOS":
        return json_response_error(DATA_ERROR, msg="data error")
    apkfilepath = os.path.join(STATIC_ROOT, "apk_%s.apk" % cur_time)
    xmlfilepath = os.path.join(STATIC_ROOT, "xml_%s.zip" % cur_time)
    apkoutputfile = open(apkfilepath, "wb")
    for chunk in apkfile.chunks():
        apkoutputfile.write(chunk)
    apkoutputfile.close()
    xmloutputfile = open(xmlfilepath, "wb")
    for chunk in xmlfile.chunks():
        xmloutputfile.write(chunk)
    xmloutputfile.close()
    apkfiledir = os.path.splitext(apkfilepath)[0]
    xmlfiledir = os.path.splitext(xmlfilepath)[0]
    os.mkdir(apkfiledir)
    os.mkdir(xmlfiledir)

    # firstly, de-compile apk file
    logger.info("start to de-compile %s", apkfilepath)
    subprocess.call(
        "apktool d -s -f %s %s" % (apkfilepath, apkfiledir), shell=True)

    # secondly, un-compress xml zip
    logger.info("start to un-compress the xml files %s", xmlfilepath)
    subprocess.call(
        "cd %s && unzip %s" % (xmlfiledir, xmlfilepath), shell=True)

    # thirdly, call init adapter
    if platform == "Android":
        package_name, version_name = init_adapter(
            platform, category, xmlfiledir, apkfiledir)
    else:
        return json_response_error(DATA_ERROR, msg="data error")

    package_path = os.path.join(STATIC_ROOT, package_name)
    if not os.path.exists(package_path):
        os.mkdir(package_path)
    version_path = os.path.join(package_path, version_name)
    if not os.path.exists(version_path):
        os.mkdir(version_path)

    # mv origin file to version path
    subprocess.call(
        "mv %s %s/" % (apkfilepath, version_path), shell=True)
    subprocess.call(
        "mv %s %s/" % (xmlfilepath, version_path), shell=True)

    # fourthly, rename xmlfiledir and apkfiledir
    raw_format_apkfiledir = os.path.join(version_path, "raw_apk_data")
    logger.info('start to mv apkdir to %s', raw_format_apkfiledir)
    if os.path.exists(raw_format_apkfiledir):
        subprocess.call(
            "rm -rf %s" % raw_format_apkfiledir, shell=True)
    subprocess.call(
        "mv %s %s" % (apkfiledir, raw_format_apkfiledir), shell=True)
    raw_format_xmlfiledir = os.path.join(version_path, "raw_xml_data")
    logger.info('start to mv xmldir to %s', raw_format_xmlfiledir)
    if os.path.exists(raw_format_xmlfiledir):
        subprocess.call(
            "rm -rf %s" % raw_format_xmlfiledir, shell=True)
    subprocess.call(
        "mv %s %s" % (xmlfiledir, raw_format_xmlfiledir), shell=True)

    # fithly, cp xmldir and apkdir
    format_apkfiledir = os.path.join(version_path, "apk_data")
    logger.info('start to cp apkdir to %s', format_apkfiledir)
    if os.path.exists(format_apkfiledir):
        subprocess.call(
            "rm -rf %s" % format_apkfiledir, shell=True)
    subprocess.call(
        "cp -r %s %s" % (raw_format_apkfiledir, format_apkfiledir),
        shell=True)
    format_xmlfiledir = os.path.join(version_path, "xml_data")
    logger.info('start to cp xmldir to %s', format_xmlfiledir)
    if os.path.exists(format_xmlfiledir):
        subprocess.call(
            "rm -rf %s" % format_xmlfiledir, shell=True)
    os.mkdir(format_xmlfiledir)
    format_xmlfiledir = os.path.join(format_xmlfiledir, "res")
    os.mkdir(format_xmlfiledir)
    subprocess.call(
        "cp -r %s/* %s" % (raw_format_xmlfiledir, format_xmlfiledir),
        shell=True)

    # sixthly, run diff logic to get miss xml to miss_xmlfiledir
    miss_xmlfiledir = os.path.join(version_path, 'miss_xml_data')
    logger.info('start to diff xml file to %s', miss_xmlfiledir)
    if os.path.exists(miss_xmlfiledir):
        subprocess.call(
            "rm -rf %s" % miss_xmlfiledir, shell=True)
    os.mkdir(miss_xmlfiledir)
    miss_xmlfiledir = os.path.join(miss_xmlfiledir, 'res-missing')
    os.mkdir(miss_xmlfiledir)
    diff_xml(raw_format_xmlfiledir, miss_xmlfiledir)

    # seventhly, cp miss xml to xml_file dir
    new_res_filedir = os.path.join(miss_xmlfiledir, "values*")
    subprocess.call(
        "cp -r %s %s" % (new_res_filedir, format_xmlfiledir), shell=True)
    new_xml_filedir = os.path.join(version_path, "xml_data")
    merge_xml(new_xml_filedir)
    return json_response_ok({})


file_info_mapping = {
    "apk": {
        "content_type": "application/vnd.android.package-archive",
        "disposition": True,
    },
    "qrcode": {
        "content_type": "image/jpeg",
        "disposition": False,
    },
}


@exception_handler()
def download(request):
    if request.method == "GET" and 'file' in request.GET and \
            'type' in request.GET:
        file_path = [STATIC_ROOT]
        for arg in ('appname', 'appversion', 'locale'):
            p = request.GET.get(arg)
            if p:
                file_path.append(p)
        file_path.append(request.GET['file'])
        requested_file = os.path.join(*file_path)
        if not os.path.exists(requested_file):
            raise IOError("requested file %s not found" % request.GET['file'])
        file_info = file_info_mapping[request.GET['type']]
        response = HttpResponse(
            FileWrapper(file(requested_file)),
            content_type=file_info['content_type'])
        if file_info['disposition']:
            response["Content-Disposition"] = \
                "attachment; filename=%s" % request.GET['file']
        response['Content-Length'] = os.path.getsize(requested_file)
        return response
    else:
        return HttpResponseNotFound('<h1>Not Found File</h1>')

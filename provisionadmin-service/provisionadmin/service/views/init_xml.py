
# -*- coding: utf-8 -*-
"""
@author: yqyu
@date: 2014-07-15
@description: get xml file and init xml file in database
"""

import logging
import os
import subprocess

from django.conf import settings

from provisionadmin.model.i18n import LocalizationApps
from provisionadmin.model.user import User
from provisionadmin.decorator import check_session, exception_handler
from provisionadmin.service.utils.adapter import init_adpter_Ex
from provisionadmin.utils.json import json_response_error, json_response_ok
from provisionadmin.service.utils.organize_values import merge_xml
from provisionadmin.utils.respcode import METHOD_ERROR
from provisionadmin.utils.util_mail import send_message

_LOGGER = logging.getLogger("init_xml_file")

STATIC_ROOT = settings.STATIC_ROOT
TEMPLATE_ROOT = settings.CUS_TEMPLATE_DIR


@exception_handler()
@check_session
def init_xml_file(request):
    """
    Get xml file and init xml file in database
    Parameters:
        -None
    Return:
        -1. get xml file success
        {
            "status": 0,
            "data":{
                ...
            }
         }
        -2. get xml file failed
        {
            "status": 0,
            "data":{
                ...
            }
         }
        -3. error http method
        {
            "status": 11,
            "data":{
                ...
            }
         }
    """
    if request.method == 'GET':
        _LOGGER.info("start to update_apps")
        data = LocalizationApps.update_apps(appname=None, appversion=None)
        ret_data = {"status": ""}
        if data:
            appname = data.get("appname")
            appversion = data.get("appversion")
            md5 = data.get("md5")
            # firstly,start to download xml file
            _LOGGER.info(
                "start to download %s_%s_%s xml file",
                (appname, appversion, md5))
            xml_file_path = LocalizationApps.get_xml_file(
                appname, appversion, md5)
            xmlfiledir = os.path.splitext(xml_file_path)[0]
            if not os.path.exists(xmlfiledir):
                os.mkdir(xmlfiledir)
            # secondly,unzip xml file
            _LOGGER.info(
                "start to unzip %s_%s xml file", (appname, appversion))
            if os.path.exists(xml_file_path):
                subprocess.call(
                    "cd %s && unzip %s" % (xmlfiledir, xml_file_path),
                    shell=True)

            # thirdly, call init adapter
            temp_xmlfiledir = os.path.join(xmlfiledir, "res")
            appname, appversion = init_adpter_Ex(
                appname, appversion, temp_xmlfiledir)

            package_path = os.path.join(STATIC_ROOT, appname)
            version_path = os.path.join(package_path, appversion)

            # fourthly, rename xmlfiledir
            raw_format_xmlfiledir = os.path.join(version_path, "raw_xml_data")
            _LOGGER.info('start to mv xmldir to %s', raw_format_xmlfiledir)
            if os.path.exists(raw_format_xmlfiledir):
                subprocess.call(
                    "rm -rf %s" % raw_format_xmlfiledir, shell=True)
            subprocess.call(
                "mv %s %s" % (xmlfiledir, raw_format_xmlfiledir), shell=True)

            # fithly, cp xmldir
            format_xmlfiledir = os.path.join(version_path, "xml_%s" % md5)
            res_xmlfiledir = os.path.join(raw_format_xmlfiledir, "res")
            _LOGGER.info('start to cp xmldir to %s', format_xmlfiledir)
            if os.path.exists(format_xmlfiledir):
                subprocess.call(
                    "rm -rf %s" % format_xmlfiledir, shell=True)
            os.mkdir(format_xmlfiledir)
            subprocess.call(
                "cp -r %s %s" % (res_xmlfiledir, format_xmlfiledir),
                shell=True)

            # sixthly, run diff logic to get miss xml to miss_xmlfiledir
            miss_xmlfiledir = os.path.join(version_path, 'miss_xml_%s' % md5)
            res_miss_xmlfiledir = os.path.join(
                raw_format_xmlfiledir, "res-missing")
            _LOGGER.info('start to cp diff xml file to %s', miss_xmlfiledir)
            if os.path.exists(miss_xmlfiledir):
                subprocess.call(
                    "rm -rf %s" % miss_xmlfiledir, shell=True)
            os.mkdir(miss_xmlfiledir)
            subprocess.call(
                "cp -r %s %s" % (res_miss_xmlfiledir, miss_xmlfiledir),
                shell=True)

            # seventhly, cp miss xml to xml_file dir
            new_res_filedir = os.path.join(res_miss_xmlfiledir, "values*")
            new_xml_filedir = os.path.join(format_xmlfiledir, "res")
            subprocess.call(
                "cp -r %s %s" % (new_res_filedir, new_xml_filedir), shell=True)
            merge_xml(format_xmlfiledir)

            # send email
            _send_email(appname, appversion)
            ret_data["status"] = "finished"
            return json_response_ok(data=ret_data)
        elif data is None:
            msg = "Failed to get the data"
            ret_data["status"] = "failed"
            return json_response_ok(data=ret_data, msg=msg)
        else:
            msg = "the xml file is the new version"
            ret_data["status"] = "latest"
            return json_response_ok(data=ret_data, msg=msg)
    else:
        return json_response_error(METHOD_ERROR, msg="http method wrong")


def _send_email(appname, appversion):
    """
    Set e-mail
    Parameters:
        -appname: package name,
        -appversion: package version,
    Return:
        -None
    """
    subject = u"Translation Task: 【%s %s】" % (appname, appversion)
    mail_to = User.get_all_country_managers()
    mail_to = ["yqyu@bainainfo.com"]
    mail_cc = ['nqi@bainainfo.com']
    template = os.path.join(TEMPLATE_ROOT, "create_task.html")
    name_version = appname + " V" + appversion
    send_message(
        subject, template, mail_to, mail_cc, False, None, name_version)

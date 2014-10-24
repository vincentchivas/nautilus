# -*- coding: utf-8 -*-
"""
@author: yqyu
@date: 2014-10-22
@description: Get Check the information of user failed to build
"""

import os
import simplejson as json

from django.conf import settings
from provisionadmin.utils.json import json_response_ok, json_response_error
from provisionadmin.utils.respcode import PARAM_REQUIRED, METHOD_ERROR, \
    DATA_ERROR
from provisionadmin.decorator import check_session, exception_handler
from provisionadmin.model.i18n import LocalizationTask, LocalizationConfig
from provisionadmin.model.user import User
from provisionadmin.utils.util_mail import send_message


TEMPLATE_ROOT = settings.CUS_TEMPLATE_DIR


@exception_handler()
@check_session
def lock_task(request, user):
    """
    admin can lock the data or unlock
    Parameters:
        -platform: package platform:Android or IOS,
        -appname: package name,
        -category: package category:Trunk or Branch,
        -appversion: package version,
        -locale: the country code,
        -operation:lock or unlock,
    Return:
        -1. lock success or unlock success
        {
            "status": 0,
            "data":{
                ...
            }
        }
        -2. error http method
        {
            "status": 11,
            "data":{
                ...
            }
        }
    """
    if request.method == 'POST':
        task_info = request.raw_post_data
        task_info = json.loads(task_info)
        required_list = (
            'platform', 'appname', 'category', 'appversion',
            'locale', 'operation')
        for required_para in required_list:
            para_data = task_info.get(required_para)
            if not para_data:
                return json_response_error(
                    PARAM_REQUIRED,
                    msg="parameter '%s' invalid" % required_para)
        LocalizationTask.lock_task(task_info)
        return json_response_ok({})
    else:
        return json_response_error(METHOD_ERROR, msg="http method wrong")


@exception_handler()
@check_session
def check_task(request, user):
    """
    country pm check task
    Parameters:
        -platform: package platform:Android or IOS,
        -appname: package name,
        -category: package category:Trunk or Branch,
        -appversion: package version,
        -locale: the country code,
        -operation:lock or unlock,
    Return:
        -1. lock success or unlock success
        {
            "status": 0,
            "data":{
                ...
            }
        }
        -2. error http method
        {
            "status": 11,
            "data":{
                ...
            }
        }
    """
    if request.method == 'POST':
        uid = user.get("_id")
        department = user.get("department")
        role = user.get("group_id")[0]
        task_info = request.raw_post_data
        task_info = json.loads(task_info)
        required_list = (
            'platform', 'appname', 'category', 'appversion', 'locale')
        for required_para in required_list:
            para_data = task_info.get(required_para)
            if not para_data:
                return json_response_error(
                    PARAM_REQUIRED,
                    msg="parameter '%s' invalid" % required_para)
        task_data = LocalizationTask.check_task_by_cpm(task_info, uid, role)
        if not task_data:
            return json_response_error(
                DATA_ERROR, msg="The task in not check finished")
        else:
            _send_email_to_admin(task_info, task_data, department)
        return json_response_ok({})
    else:
        return json_response_error(METHOD_ERROR, msg="http method wrong")


def _send_email_to_admin(task_info, task_data, department):
    """
    Sene e-mail to translator
    Parameters:
        -appname: package name,
        -appversion: package version,
        -locale: Country code,
        -display_locale: The name of the locale displayed on the page
    Return:
        -None
    """
    appname = task_info.get("appname")
    appversion = task_info.get("appversion")
    locale = task_info.get("locale")
    app_info = LocalizationConfig.get_locale_info(
        appname, appversion, locale)
    locale_language = app_info.get("language")
    display_locale = "%s(%s)" % (locale_language, locale)
    name_version = appname + " V" + appversion

    left_count = task_data["strings"]["untranslated"]

    mail_to = User.get_charge_info(department)[1]
    mail_to = ["yqyu@bainainfo.com"]
    mail_cc = ['yqyu@bainainfo.com']
    # mail_cc.append('nqi@bainainfo.com')
    if left_count:
        unpass_subject = u"Translation was not pass 【%s %s】" % (
            appname, appversion)
        unpass_template = os.path.join(TEMPLATE_ROOT, "finish_task.html")
        send_message(
            unpass_subject, unpass_template, mail_to, mail_cc, False, None,
            name_version, display_locale, left_count)
    else:
        subject = u"Translation was done 【%s %s】" % (appname, appversion)
        pass_template = os.path.join(TEMPLATE_ROOT, "finish_task.html")
        send_message(
            subject, pass_template, mail_to, mail_cc, False, None,
            name_version, display_locale)
        template = os.path.join(TEMPLATE_ROOT, "finish_task.html")
        send_message(
            subject, template, mail_to, mail_cc, False, None,
            name_version, display_locale)

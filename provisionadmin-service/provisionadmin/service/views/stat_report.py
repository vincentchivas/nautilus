# -*- coding: utf-8 -*-
# import datetime
from django.http import HttpResponse
from provisionadmin.model.report import Report, BelugaData
from provisionadmin.model.i18n import ReportConfig
from provisionadmin.db import user
# from django.shortcuts import render_to_response
from provisionadmin.decorator import check_session, exception_handler
import simplejson
import os
from provisionadmin.utils.respcode import DB_ERROR, \
    METHOD_ERROR, DATA_ERROR, PARAM_REQUIRED
from provisionadmin.utils.json import json_response_error, json_response_ok
from datetime import datetime, timedelta
import random

YESTERDAY = datetime.now() - timedelta(days=1)


@exception_handler()
# @check_session
def report_locale(req):
    if req.method == "GET":
        USED_COUNTRY = ReportConfig.get_needed_locales()
        ret = {}
        begin_date = req.GET.get("start", None)
        # we set default value yesterday
        if begin_date:
            begin_date = datetime.strptime(begin_date, "%Y-%m-%d")
        else:
            begin_date = YESTERDAY
        end_date = req.GET.get("end", None)
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        else:
            end_date = YESTERDAY
        day_span = (end_date - begin_date).days + 1

        report = Report.new()
        locale_data = report.fetch_some_days_data(begin_date, day_span)
        if not locale_data:
            return json_response_error(DATA_ERROR, msg="can not fetch data")
        # filter some not cared country
        local_keys = locale_data.keys()
        for local_name in local_keys:
            if local_name not in USED_COUNTRY:
                del locale_data[local_name]
        # calc the avg time
        for locale, locale_detail in locale_data.items():
            locale_detail["avg_time"] = round(locale_detail["total_time"] / locale_detail["count"], 3)
            del locale_detail["total_time"]
        
        # add beluga data
        beluga = BelugaData.new()
        beluga_data = beluga.get_some_days_data(begin_date, day_span)
        ret["items"] = []
        batch = req.GET.get("batch", None)
        if not batch:
            batch_list = ["first", "second"]
        elif batch == "0":
            batch_list = ["first"]
        elif batch == "1":
            batch_list = ["second"]
        else:
            return json_response_error(PARAM_REQUIRED, msg="the wrong param for batch")
        for classify in batch_list:
            CLASSIFY_LOCALE_DICT = ReportConfig.get_classify_locales(
                classify=classify)
            classify_data = {}
            for key in CLASSIFY_LOCALE_DICT.keys():
                if key in locale_data.keys():
                    classify_data[CLASSIFY_LOCALE_DICT[key]] = locale_data[key]
                else:
                    classify_data[CLASSIFY_LOCALE_DICT[key]] = {"count": 0, "avg_time": 0.000}
            for country, value in beluga_data.items():
                if country in classify_data.keys():
                    classify_data[country]["wifi_rate"] = round(float(value["wifi_success"]) / value["wifi_total"], 2)
                    classify_data[country]["mobile_rate"] = round(float(value["mobile_success"]) / value["mobile_total"], 2)
            ret["items"].append(classify_data)
        return json_response_ok(ret)
    else:
        return json_response_error(METHOD_ERROR, msg="http method wrong")

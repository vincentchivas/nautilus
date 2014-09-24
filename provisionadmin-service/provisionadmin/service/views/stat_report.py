# -*- coding: utf-8 -*-
# import datetime
from django.http import HttpResponse
from provisionadmin.model.report import Report, BelugaData
from provisionadmin.model.i18n import ReportConfig
from provisionadmin.db import user
from provisionadmin.decorator import check_session, exception_handler
from provisionadmin.utils.respcode import DB_ERROR, \
    METHOD_ERROR, DATA_ERROR, PARAM_REQUIRED
from provisionadmin.utils.json import json_response_error, json_response_ok
from datetime import datetime, timedelta
import logging

YESTERDAY = datetime.now() - timedelta(days=1)
logger = logging.getLogger("view")


@exception_handler()
# @check_session
def report_locale(req):
    '''
    get data for stability report

    GET -- get stability data

    Request URL: admin/report/provision_analysis

    HTTP Method: GET

    Parameters:
        - start: start date for report
        - end: end date for report
        - batch: the batch of countries

    Return:
    {
        "status": 0,
        "msg": "",
        "data": {
        }
    }

    Error:
        - PARAM_REQUIRED
        - DATA_ERROR
        - DB_ERROR
    '''
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
            # now we have two batches
            ret["items"] = [{} for i in range(2)]
            logger.warning("we have no data for %s from %s" % (begin_date, end_date))
            return json_response_ok(ret)
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
        beluga_data = beluga.get_some_days_data(begin_date, end_date)
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
            classify_data = _combine_data(locale_data, beluga_data, classify)
            ret["items"].append(classify_data)
        return json_response_ok(ret)
    else:
        return json_response_error(METHOD_ERROR, msg="http method wrong")


@exception_handler()
def get_detail_data(req):
    '''
    get detail data for a specified country and date

    GET -- get detail data

    Request URL: admin/report/detail_analysis

    HTTP Method: GET

    Parameters:
        - start: start date for report
        - end: end date for report
        - batch: the batch of countries

    Return:
    {
        "status": 0,
        "msg": "",
        "data": {
        }
    }

    Error:
        - PARAM_REQUIRED
        - DATA_ERROR
        - DB_ERROR
    '''
    if req.method == "GET":
        required_params = ("start", "end")
        for item in required_params:
            if item not in req.GET:
                return json_response_error(PARAM_REQUIRED, msg="need param start and end")

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
        # is_all_versions = True if version == "all" else False
        batch = req.GET.get("batch", None)
        if not batch:
            batch_list = ["first", "second"]
        elif batch == "0":
            batch_list = ["first"]
        elif batch == "1":
            batch_list = ["second"]
        else:
            return json_response_error(PARAM_ERROR, msg="the wrong param for batch")

        # organize the data
        ret = {}
        ret["items"] = []
        report = Report.new()
        beluga = BelugaData.new()

        for _ in range(day_span):
            tmp_day = begin_date
            one_day_data = []
            report_data = report.fetch_one_day_data(tmp_day)
            # calc the avg time
            for locale, locale_detail in report_data.items():
                locale_detail["avg_time"] = round(locale_detail["total_time"] / locale_detail["count"], 3)
                del locale_detail["total_time"]
                
            beluga_data = beluga.get_detail_data_for_beluga(tmp_day)
            for classify in batch_list:
                classify_data = _combine_data(report_data, beluga_data, classify)
                one_day_data.append(classify_data)
            begin_date += timedelta(days=1)
            ret["items"].append(one_day_data)
        return json_response_ok(ret)
    else:
        return json_response_error(METHOD_ERROR, msg="http method wrong")


def _combine_data(report_data, beluga_data, classify):
    '''
    combine data from beluga and logserver
    '''
    CLASSIFY_LOCALE_DICT = ReportConfig.get_classify_locales(
        classify=classify)
    classify_data = {}
    for key, country in CLASSIFY_LOCALE_DICT.items():
        if key in report_data.keys():
            classify_data[country] = report_data[key]
        else:
            classify_data[country] = {
                "count": 0, "avg_time": 0.000}

        if country in beluga_data.keys():
            classify_data[country]["wifi_rate"] = round(
                float(beluga_data[country]["wifi_success"]) / beluga_data[country]["wifi_total"], 4)
            classify_data[country]["mobile_rate"] = round(
                float(beluga_data[country]["mobile_success"]) / beluga_data[country]["mobile_total"], 4)
        else:
            classify_data[country]["wifi_rate"] = 0.00
            classify_data[country]["mobile_rate"] = 0.00
    return classify_data


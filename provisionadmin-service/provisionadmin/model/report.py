import logging
import os
from provisionadmin.settings import DB_SETTINGS
from datetime import datetime, timedelta
import time
import logging
import simplejson

from provisionadmin.db.mysqldb import MySql_Conn

logger = logging.getLogger("model")


class Report(object):

    @classmethod
    def new(cls):
        instance = cls()
        instance._mysql_conn = MySql_Conn.new(
            DB_SETTINGS['provision_stat']['host'],
            DB_SETTINGS['provision_stat'][
                'username'],
            DB_SETTINGS['provision_stat'][
                'password'],
            DB_SETTINGS[
                'provision_stat']['dbname'],
            DB_SETTINGS['provision_stat']['port'])
        return instance

    def get_date_str(self, date):
        return date.strftime("%Y%m%d")

    def fetch_one_day_data(self, specify_date):
        USED_API_NAME = ("/api/1/preset.json", "/api/2/provision.json")
        datestr = self.get_date_str(specify_date)
        table_name = "provision_api_stat_%s" % datestr
        select_sql_str = "select api_name, locale from %s" % table_name
        ret_mysql = self._mysql_conn.query_sql(select_sql_str)
        ret = {}
        if not ret_mysql or not len(ret_mysql):
            logger.error("There is no data for date %s" % datestr)
            raise IOError, ("There is no data for date %s" % datestr)
            return ret
        for api_info in ret_mysql:
            api_name = api_info[0]
            if api_name not in USED_API_NAME:
                continue
            api_locale_info = api_info[1]
            # convert str into dict
            ret[api_name] = simplejson.loads(api_locale_info)
        return ret

    def fetch_some_days_data(self, begin_date, day_span):

        def convert_data_to_locale(api_map):
            locale_map = {}
            if not api_map:
                return locale_map
            for api_name, api_locale_info in api_map.items():
                for locale_name, locale_info in api_locale_info.items():
                    if not locale_name in locale_map:
                        tmp_data = {}
                        locale_map[locale_name] = tmp_data
                        tmp_data["count"] = locale_info["count"]
                        tmp_data["total_time"] = locale_info["total_time"]
                    else:
                        tmp_data = locale_map[locale_name]
                        tmp_data["count"] += locale_info["count"]
                        tmp_data["total_time"] += locale_info["total_time"]
            return locale_map

        tmp_day = begin_date
        ret = {}
        for _ in range(day_span):
            tmp_day_str = self.get_date_str(tmp_day)
            day_data = convert_data_to_locale(self.fetch_one_day_data(tmp_day))
            for key, value in day_data.items():
                if key not in ret:
                    ret[key] = value
                else:
                    ret[key]["count"] += value["count"]
                    ret[key]["total_time"] += value["total_time"]
            tmp_day += timedelta(days=1)
        return ret


class BelugaData(object):

    @classmethod
    def new(cls):
        instance = cls()
        instance._mysql_conn = MySql_Conn.new(
            DB_SETTINGS['beluga_data']['host'],
            DB_SETTINGS['beluga_data']['username'],
            DB_SETTINGS['beluga_data']['password'],
            DB_SETTINGS['beluga_data']['dbname'],
            DB_SETTINGS['beluga_data']['port'])
        return instance

    def get_date_str(self, date):
        return date.strftime("%Y-%m-%d")

    def get_some_days_data(self, beg_date, day_span):
        beg_datestr = self.get_date_str(beg_date)
        end_date = beg_date + timedelta(days=day_span)
        end_datestr = self.get_date_str(end_date)
        query_sql = 'select network,location,successful_uv,total_uv from preload_succeed_view where date between "%s" and "%s"' % (
            beg_datestr, end_datestr)
        print query_sql
        ret_mysql = self._mysql_conn.query_sql(query_sql)
        if not ret_mysql:
            raise IOError, ("we can not get data from Beluga")
        ret = {}
        for one_data in ret_mysql:
            location = one_data[1]
            # modify UAE name
            if "United Arab Emirates" == location:
                location = "UAE"
            network = one_data[0]
            if network not in ("TYPE_WIFI", "TYPE_MOBILE"):
                continue
            if location not in ret:
                tmp_dict = {"wifi_success": 0, "wifi_total":
                            0, "mobile_success": 0, "mobile_total": 0}
            else:
                tmp_dict = ret[location]
            if network == "TYPE_WIFI":
                tmp_dict["wifi_success"] += int(one_data[2])
                tmp_dict["wifi_total"] += int(one_data[3])
            if network == "TYPE_MOBILE":
                tmp_dict["mobile_success"] += int(one_data[2])
                tmp_dict["mobile_total"] += int(one_data[3])
            ret[location] = tmp_dict
        return ret

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

    def convert_data_to_locale(self, api_map):
        locale_map = {}
        if not api_map:
            return locale_map
        for api_name, api_locale_info in api_map.items():
            for locale_name, locale_info in api_locale_info.items():
                locale_name = locale_name[-2:]
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

    def fetch_one_day_data(self, specify_date):
        USED_API_NAME = ("/api/2/provision.json",)
        datestr = self.get_date_str(specify_date)
        table_name = "provision_api_stat_%s" % datestr
        select_sql_str = "select api_name, locale from %s" % table_name
        ret_mysql = self._mysql_conn.query_sql(select_sql_str)
        ret = {}
        if not ret_mysql or not len(ret_mysql):
            logger.error("There is no data for date %s" % datestr)
            return ret
        for api_info in ret_mysql:
            api_name = api_info[0]
            if api_name not in USED_API_NAME:
                continue
            api_locale_info = api_info[1]
            # convert str into dict
            ret[api_name] = simplejson.loads(api_locale_info)
        return self.convert_data_to_locale(ret)

    def fetch_some_days_data(self, begin_date, day_span):
        tmp_day = begin_date
        ret = {}
        for _ in range(day_span):
            tmp_day_str = self.get_date_str(tmp_day)
            day_data = self.fetch_one_day_data(tmp_day)
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

    def get_some_days_data(self, beg_date, end_date):
        beg_datestr = self.get_date_str(beg_date)
        end_datestr = self.get_date_str(end_date)
        total_sql = "select location, network, sum(uv) from preload_data_view where date between '%s' and '%s' group by location,network" % (
            beg_datestr, end_datestr)
        total_mysql = self._mysql_conn.query_sql(total_sql)
        wifi_total_dict = {}
        mobile_total_dict = {}
        for data in total_mysql:
            lc = data[0]
            net = data[1]
            if "United Arab Emirates" == lc:
                lc = "UAE"
            if net == "TYPE_WIFI":
                wifi_total_dict[lc] = int(data[2])
            elif net == "TYPE_MOBILE":
                mobile_total_dict[lc] = int(data[2])
            else:
                continue

        query_sql = "select location,network,sum(uv) from preload_data_view where date between '%s' and '%s'" % (
            beg_datestr, end_datestr) + " and (label='successful' or label='failed_noconfig' or label like '%" + "failed_4%' or label='failed_304') group by location,network"
        ret_mysql = self._mysql_conn.query_sql(query_sql)
        if not ret_mysql:
            return {}

        ret = {}
        for one_data in ret_mysql:
            location = one_data[0]
            # modify UAE name
            if "United Arab Emirates" == location:
                location = "UAE"
            network = one_data[1]
            if network not in ("TYPE_WIFI", "TYPE_MOBILE"):
                continue
            if location not in ret:
                tmp_dict = {"wifi_success": 0, "wifi_total":
                            0, "mobile_success": 0, "mobile_total": 0}
            else:
                tmp_dict = ret[location]
            if network == "TYPE_WIFI":
                tmp_dict["wifi_success"] += int(one_data[2])
                tmp_dict["wifi_total"] += wifi_total_dict[location]
            if network == "TYPE_MOBILE":
                tmp_dict["mobile_success"] += int(one_data[2])
                tmp_dict["mobile_total"] += mobile_total_dict[location]
            ret[location] = tmp_dict
        return ret

    def get_detail_data_for_beluga(self, date):
        datestr = self.get_date_str(date)
        ret = {}
        # calc the total for each location
        total_sql = "select location, network, sum(uv) from preload_data_view where date = '%s' \
                     group by location,network" % datestr
        total_mysql = self._mysql_conn.query_sql(total_sql)
        wifi_total_dict = {}
        mobile_total_dict = {}
        for data in total_mysql:
            lc = data[0]
            net = data[1]
            if "United Arab Emirates" == lc:
                lc = "UAE"
            if net == "TYPE_WIFI":
                wifi_total_dict[lc] = int(data[2])
            elif net == "TYPE_MOBILE":
                mobile_total_dict[lc] = int(data[2])
            else:
                continue

        sql_str = "select location,network,sum(uv) from preload_data_view where date='%s'" % datestr + \
            " and (label='successful' or label='failed_noconfig' or label like '%" + \
            "failed_4%' or label='failed_304') group by location,network"
        print sql_str
        ret_mysql = self._mysql_conn.query_sql(sql_str)

        for data in ret_mysql:
            network = data[1]
            if network not in ("TYPE_WIFI", "TYPE_MOBILE"):
                continue
            location = data[0]
            # modify UAE name
            if "United Arab Emirates" == location:
                location = "UAE"
            success_count = int(data[2])
            if location not in ret:
                tmp_dict = {"wifi_success": 0, "wifi_total":
                            0, "mobile_success": 0, "mobile_total": 0}
            else:
                tmp_dict = ret[location]
            if network == "TYPE_WIFI":
                tmp_dict["wifi_success"] += success_count
                tmp_dict["wifi_total"] += wifi_total_dict[location]
            if network == "TYPE_MOBILE":
                tmp_dict["mobile_success"] += success_count
                tmp_dict["mobile_total"] += mobile_total_dict[location]
            ret[location] = tmp_dict
        return ret

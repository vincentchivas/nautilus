#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import smtplib
import email
import os
import logging
os.environ['DJANGO_SETTINGS_MODULE'] = 'dolphinopadmin.settings'
from datetime import date, datetime
from pyExcelerator import Workbook
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pymongo.connection import Connection
from django.conf import settings
try:
    from uwsgidecorators import cron
except:
    pass

from dolphinopadmin.advert.models import Cooperation, PositionCategory, PositionItem

logger = logging.getLogger("dolphinopadmin.admin")

CRON_SERVER = ['admin']
_connections = {}


def connect(host, port=None):
    '''
    Connect to the database.
    '''
    assert host, 'host of the database server may not be null.'
    global _connections
    key = (host, port or 27017)
    conn = None
    if key in _connections:
        conn = _connections[key]
    else:
        conn = Connection(host, port, slave_okay=True)
        _connections[key] = conn
    return conn

# TODO change db ip to youself db ip
server = settings.ENV_CONFIGURATION
china_db = server.get('china')
if(china_db):
    _con = connect(china_db['host'], china_db.get('port', 27017))
    _db = _con[china_db.get('db', 'dolphinop')]
else:
    _con = connect('115.29.171.191', 27017)
    _db = _con['dolphinop']

total = 0
DAY = 86400

START = 20130107
PACKAGE = 'com.dolphin.browser.tuna'
VERSION = 1


def get_date_timestamp(n=-1):
    today = date.today()
    timestamp = int(time.mktime(today.timetuple()))
    timestamp += n * DAY
    day = datetime.fromtimestamp(timestamp).strftime('%Y/%m/%d')
    return timestamp, timestamp + DAY, day


def get_raw_data(cond):
    colls = _db.advert_track.find(cond, fields={'_id': 0})
    return [i for i in colls]


def generate_daily_data(n=-1):
    start, end, cul_date = get_date_timestamp(n)
    cond = {'time': {'$gte': start, '$lte': end}}
    raw_data = get_raw_data(cond)
    sta_dict = {}
    uv_dict = {}
    result_dict = {}
    for item in raw_data:
        key = "%s,%s,%s" % (item['cid'], item['pid'], item['id'])
        if key in sta_dict:
            sta_dict[key]['click'] += 1
            ip = item['ip']
            if ip not in uv_dict[key]:
                uv_dict[key][ip] = True
                sta_dict[key]['uv'] += 1
        else:
            sta_dict[key] = {'click': 1, 'uv': 1}
            uv_dict[key] = {item['ip']: True}

    result_dict['date'] = cul_date
    result_dict['day'] = int(cul_date.replace('/', ''))
    result_dict['data'] = sta_dict
    result_dict['count'] = len(raw_data)

    _db.advert_report.update({'date': cul_date}, result_dict, upsert=True)



def get_report_data():
    colls = _db.advert_report.find(
        {}, fields={'_id': 0, 'day': 0}).sort([('day', 1)])
    return [i for i in colls]


def generate_report():
    report_data = get_report_data()
    excel_data = []
    for item in report_data:
        sta = item['data']
        tmp_dict = {}
        for keys in sta:
            cid, pid, aid = keys.split(',')
            key = '%040d%040d%040d' % (int(cid), int(pid), int(aid))
            tmp_dict[key] = {"cid": int(cid), "pid": int(pid), "aid": int(
                aid), "click": sta[keys]['click'], "uv": sta[keys]['uv']}
        key_list = tmp_dict.keys()
        key_list.sort()
        for key in key_list:
            dic = tmp_dict[key]
            try:
                name = title = url = publisher = 'deleted'
                coop = Cooperation.objects.get(id=dic['aid'])
                name = coop.name
                title = coop.title
                url = coop.url
                publisher = coop.publisher.company
                opt = [0, 0, 0, 0]
                if coop.cmcc:
                    opt[0] = 1
                if coop.unicom:
                    opt[1] = 1
                if coop.telecom:
                    opt[2] = 1
                if coop.other_operator:
                    opt[3] = 1
            except Exception:
                pass
            try:
                cat_name = 'deleted'
                cat = PositionCategory.objects.get(cid=dic['cid'])
                cat_name = cat.name
            except Exception:
                pass
            try:
                pos_name = 'deleted'
                pos = PositionItem.objects.get(pid=dic['pid'])
                pos_name = pos.name
            except Exception:
                pass
            tup = (
                item['date'], cat_name, pos_name, dic['aid'], name, title, url,
                publisher, opt[0], opt[1], opt[2], opt[3], dic['click'], dic['uv'])
            excel_data.append(tup)
            #print item['date'], cat_name, pos_name, dic['aid'], name, title, url, publisher, opt[0], opt[1], opt[2], opt[3], dic['click'], dic['uv']
    return excel_data


def generate_excel():
    excel_data = generate_report()
    w = Workbook()
    ws = w.add_sheet('sheet')
    ws.write(0, 0, u'date')
    ws.write(0, 1, u'production')
    ws.write(0, 2, u'location')
    ws.write(0, 3, u'id')
    ws.write(0, 4, u'name')
    ws.write(0, 5, u'title')
    ws.write(0, 6, u'url')
    ws.write(0, 7, u'publisher')
    ws.write(0, 8, u'移动')
    ws.write(0, 9, u'联通')
    ws.write(0, 10, u'电信')
    ws.write(0, 11, u'其它')
    ws.write(0, 12, u'click')
    ws.write(0, 13, u'uv')
    for i in range(len(excel_data)):
        for j in range(len(excel_data[i])):
            ws.write(i + 1, j, excel_data[i][j])
        i += 1
    w.save('/tmp/advert_report.xls')


def send_email(address, subject, content, file_name=None):
    user = 'conch.monitor@gmail.com'
    passwd = 'bainaP@55word'
    to = ';'.join(address)
    msg = MIMEMultipart('alternative')
    msg['To'] = to
    msg['From'] = 'Advert Track<' + user + '>'
    msg['Subject'] = subject
    part = MIMEText(content, 'html', 'utf-8')
    msg.attach(part)
    if file_name is not None:
        contype = 'application/ostet-stream'
        maintype, subtype = contype.split('/', 1)

        data = open(file_name, 'rb')
        file_msg = email.MIMEBase.MIMEBase(maintype, subtype)
        file_msg.set_payload(data.read())
        data.close()
        email.Encoders.encode_base64(file_msg)

        basename = os.path.basename(file_name)
        file_msg.add_header('Content-Disposition',
                            'attachment', filename=basename)
        msg.attach(file_msg)

    print 'send email 1'
    s = smtplib.SMTP('smtp.gmail.com', 587)
    print 'send email 2'
    s.starttls()
    print 'send email 3'
    s.ehlo()
    print 'send email 4'
    s.login(user, passwd)
    print 'send email 5'
    s.sendmail(user, address, msg.as_string())
    print 'send email 6'
    s.quit()
    print 'send email 7'


def report():
    generate_excel()

#    email_list = ['jwang@bainainfo.com']
    # email_list = ['yfhe@bainainfo.com','zhyu@bainainfo.com','hzhang@bainainfo.com','lxfeng@bainainfo.com',
    #        'ktliu@bainainfo.com','hlan@bainainfo.com']
    #send_email(email_list, u'广告点击量track报表', u'<html>advert track<html>', '/tmp/advert_report.xls')


@cron(10, 1, -1, -1, -1)
def cron_report(num):
    try:
        if settings.SERVER in CRON_SERVER:
            logger.info('start to orginize advert report datas')
            generate_daily_data()
            logger.info('create advert report start!')
            report()
            logger.info('create advert report successfully')
    except Exception, e:
        logger.exception(e)

if __name__ == '__main__':
#    for i in range(-15, -14):
#        generate_daily_data(i)
#    generate_daily_data()
    report()

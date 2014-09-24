# -*- coding: utf-8 -*-
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'provisionadmin.settings'
from provisionadmin.model.i18n import LocalizationInfo, MailConfig
from provisionadmin.utils.util_mail import send_message
import datetime


def trans_need():
    latest_xml = LocalizationInfo.get_lastest_info()
    appname = latest_xml.get('appname')
    appversion = latest_xml.get('appversion')
    combine = appname + ' V' + appversion
    threeday = datetime.date.today() + datetime.timedelta(days=5)
    subject = u"Translation needs 【" + combine + u"】"
    cur_dir = os.getcwd()
    pre_dir = cur_dir.split('/')
    pre_dir.pop(-1)
    pre_str = '/'.join(pre_dir)
    template = '/'.join((pre_str, 'templates/trans_send.html'))
    mail_to, mail_cc = MailConfig.get_mailto_list()
    mail_cc.append('nqi@bainainfo.com')
    mail_cc.append('shjmi@bainainfo.com')
    mail_cc.append('lyliu@bainainfo.com')
    mail_cc.append('ghyang@bainainfo.com')
    send_message(
        subject, template, mail_to, mail_cc, False, None, combine,
        str(threeday))


if __name__ == '__main__':
    try:
        result = trans_need()
        print result
    except Exception, e:
        print e

# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from provisionadmin.utils.json import json_response_error, json_response_ok
from provisionadmin.utils.respcode import METHOD_ERROR
from provisionadmin.utils.util_mail import send_message
# from provisionadmin.decorator import check_session, exception
from provisionadmin.settings import CUS_TEMPLATE_DIR
import simplejson


def trans_comment(req):
    if req.method == 'POST':
        temp_strs = req.raw_post_data
        temp_dict = simplejson.loads(temp_strs)
        score = temp_dict.get('score')
        comment = temp_dict.get('comment')
        subject = 'I18NStudio Feedback'
        template = '/'.join((CUS_TEMPLATE_DIR, 'feedback.html'))
        mail_to = ["nqi@bainainfo.com"]
        mail_cc = ["bhuang@bainainfo.com"]
        send_message(
            subject, template, mail_to, mail_cc, False, None, score, comment)
        return json_response_ok({}, msg='submit success')
    else:
        return json_response_error(METHOD_ERROR, msg='http method error')

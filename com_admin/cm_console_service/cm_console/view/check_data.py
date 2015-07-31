# -*- coding: utf-8 -*-
import logging
from cm_console.model.common import classing_model


_LOGGER = logging.getLogger(__name__)


class ios_console(object):

    appname = 'ios_console'

    def __init__(self, check_success, msg):
        self.check_success = check_success
        self.msg = msg

    def themefolder_check(self, save_dict):
        size = save_dict.get('size')
        isfree = save_dict.get('isfree')
        themes = save_dict.get('theme')
        theme_ids = [t.get('id') for t in themes]
        Theme = classing_model('theme')
        theme_infos = Theme.find(
            self.appname, cond={'id': {'$in': theme_ids}},
            fields={'_id': 0}, toarray=True)
        for theme_info in theme_infos:
            theme_size = theme_info.get('size')
            theme_free = theme_info.get('isfree')
            if not size == theme_size or not isfree == theme_free:
                self.check_success = False
                self.msg = 'theme %s in folder is not matched size or paid\
                    type' % theme_info.get('title')
                break
        return self.check_success, self.msg


def check_need_params(modelname, save_dict):
    ModelClass = classing_model(modelname)
    fields = ModelClass.fields_check
    check_success = True
    msg = 'check need param value'
    for fld in fields:
        paras = fld.split('&')
        (param_key, param_option, param_type, default_value) = tuple(
            paras) + (None, ) * (4 - len(paras))
        if param_option == 'need' and not param_type == 'bool':
            # need key must has a value, but except bool type
            if not save_dict.get(param_key):
                check_success = False
                msg = '%s should not be empty' % param_key
                break
    return check_success, msg


def build_unqiue_cond(modelname, save_dict):
    ModelClass = classing_model(modelname)
    cond = {}
    unique = ModelClass.unique

    if len(unique) > 1:
        # unique should be list type
        # like ['a', ('b','c')] ---->
        # {"$or": [{"a":"xx"}, "$and":[{"b":"yy"}, {"c": "zz"}]]}
        or_cond = []
        for u in unique:
            if not isinstance(u, str):
                and_cond = []
                for ui in u:
                    if save_dict.get(ui):
                        and_cond.append({ui: save_dict[ui]})
            else:
                if save_dict.get(u):
                    or_cond.append({u: save_dict[u]})
    else:
        one = unique[0]
        if not isinstance(one, str) and not isinstance(one, unicode):
            and_cond = []
            for ui in one:
                if save_dict.get(ui):
                    and_cond.append({ui: save_dict[ui]})
        else:
            cond[one] = save_dict[one]
    return cond


def check_data_unique(appname, modelname, save_dict, item_id=None):
    check_success = True
    msg = 'check unique param value'
    ModelClass = classing_model(modelname)

    if not getattr(ModelClass, 'unique', None):
        return check_success, msg

    cond = build_unqiue_cond(modelname, save_dict)
    if not item_id:
    # insert before check unique
        item = ModelClass.find_one(appname, cond)
        if item:
            check_success = False
            msg = "check unique fail"
    else:
        item_old = ModelClass.find_one(appname, {'id': item_id})
        item_find = ModelClass.find_one(appname, cond)
        if item_find and not item_find == item_old:
            check_success = False
            msg = "check unique fail"
    return check_success, msg


def check_save_dict(appname, modelname, save_dict, item_id=None):
    '''
     main enter for save dict check,
     all the check data functions define here
    '''
    check_success = True
    msg = "check save data"

    (check_success, msg) = check_need_params(modelname, save_dict)
    if not check_success:
        return False, msg

    (check_success, msg) = check_data_unique(
        appname, modelname, save_dict, item_id)
    if not check_success:
        return False, msg

    app_obj = None
    try:
        app_obj = eval(appname)(check_success=check_success, msg=msg)
    except NameError:
        msg = 'none app config, no need to check'
        return check_success, msg
    func_name = modelname + "_check"
    if hasattr(app_obj, func_name):
        (check_success, msg) = getattr(app_obj, func_name)(save_dict)
    return check_success, msg

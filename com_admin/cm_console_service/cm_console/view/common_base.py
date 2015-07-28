 # -*- coding: utf-8 -*-
# import time
import re
import time
import types
import logging
from operator import itemgetter

from cm_console.model.common import classing_model

from cm_console.utils.status import NameFactory
from cm_console.related.icon import derefered_icon

from armory.marine.exception import ParamError
from armory.marine.respcode import (
    PARAM_ERROR, OK, DATA_DELETE_COMFIRM, DATA_RELETED_BY_OTHER)


_LOGGER = logging.getLogger(__name__)
_ONE_DAY = 86400.0
_TOP_MODELS = ["themepush"]


def _get_ids(appname, child_ids, child_model, parent_model):
    '''
     通过子model的id获取父model的id
    '''
    parent_ids = []
    cond = {}
    Parent_Model = classing_model(parent_model)
    for child_id in child_ids:
        cond = NameFactory.combine_cond(child_model, child_id)
        parents = Parent_Model.find(
            appname, cond, fields={'_id': 0}, toarray=True)
        if parents:
            parent_ids = [p.get('id') for p in parents]
    return list(set(parent_ids))


def ref_topmodel(appname, model_id, model_name, object_link=[]):
    '''
     notice: pass in object links, give back the preset ids
     if len(object) is 1, get it easy
     patch: in push admin, some model has modify pattern,
     such as push speeddial, speeddial_modify
    '''
    topmodel = object_link[-1]
    TopModel = classing_model(topmodel)
    topmodel_list = []
    length = len(object_link)
    cond = {}
    topmodel_ids = []
    if length == 1:
        cond = NameFactory.combine_cond(model_name, model_id)
        topmodel_list = TopModel.find(
            appname, cond, fields={'_id': 0}, toarray=True)
        if topmodel_list:
            topmodel_ids = [t.get('id') for t in topmodel_list]
    else:
        index = 0
        start_model = model_name
        next_ids = []
        next_ids.append(model_id)
        while index < length:
            next_ids = _get_ids(
                appname, next_ids, start_model, object_link[index])
            start_model = object_link[index]
            index = index + 1
        topmodel_ids = next_ids
    return topmodel_ids


def get_topmodel_ids(appname, model_id, modelname):
    '''
    passed in the model id, and will return a dict of refered infos,
    it is passed through attr object_link.
    '''
    Model_Name = classing_model(modelname)
    res_dict = {}
    if hasattr(Model_Name, "object_links"):
        ref_dict = Model_Name.object_links
        for ref in ref_dict:
            object_link = ref_dict[ref]
            topmodel = object_link[-1]
            top_ids = ref_topmodel(appname, model_id, modelname, object_link)
            res_dict.setdefault(topmodel, []).extend(top_ids)
    return res_dict


def _get_ruleids(appname, search_word, field='lcpn'):
    rule_ids = []
    Rule = classing_model("aosruledata")
    cond = {}
    if field == 'lcpn':
        cond_list = []
        Locale = classing_model("aoslocale")
        Package = classing_model("aospackage")
        cond_locale = {
            'title': {'$regex': re.escape(search_word), '$options': '$i'}}
        locale_list = Locale.find(
            appname, cond_locale, fields={'_id': 1}, toarray=True)

        cond_package = {
            'package_name': {
                '$regex': re.escape(search_word), '$options': '$i'}}
        package_list = Package.find(
            appname, cond_package, fields={'_id': 1}, toarray=True)

        if locale_list:
            locale_ids = [p.get('_id') for p in locale_list]
            cond_list.append({"locale": {'$in': locale_ids}})
        if package_list:
            package_ids = [p.get('_id') for p in package_list]
            cond_list.append({"package": {'$in': package_ids}})
        if cond_list:
            cond['$or'] = cond_list
        else:
            return rule_ids
    elif field == 'rule':
        cond = {
            'title': {'$regex': re.escape(search_word), '$options': '$i'}}
    else:
        return rule_ids
    rule_list = Rule.find(
        appname, cond, fields={'_id': 1}, toarray=True)
    if rule_list:
        rule_ids = [r.get('_id') for r in rule_list]
    return rule_ids


def _search_cond(appname, query_dict, search_fields):
    '''
    notice:when a request comes,combination of the search_fields and the
    request parameter values, return a condition query to mongodb
    '''
    cond = {}
    regex_cond_list = []
    date_cond = {}
    for key in search_fields.keys():
        # 当给searchKeyword时候，能全局搜索
        if query_dict.get("searchKeyword"):
            regex_cond = {}
            keyword = query_dict.get("searchKeyword")
            if search_fields.get(key)["data_type"] == "int":
                try:
                    regex_cond[key] = int(keyword)
                except:
                    pass
            if search_fields.get(key)["data_type"] == "string":
                if keyword.isalpha():
                    regex_cond[key] = {
                        "$regex": re.escape(keyword), "$options": "$i"}
                else:
                    regex_cond[key] = {"$regex": re.escape(keyword)}
            if search_fields.get(key)["data_type"] == "ref_rule":
                rule_ids = _get_ruleids(appname, keyword, key)
                if rule_ids:
                    regex_cond['aosruledata.id'] = {'$in': rule_ids}
            if regex_cond:
                regex_cond_list.append(regex_cond)
        if query_dict.get('start') and query_dict.get('end'):
            start = time.mktime(time.strptime(query_dict['start'], '%Y-%m-%d'))
            end = time.mktime(
                time.strptime(query_dict['end'], '%Y-%m-%d')) + _ONE_DAY
            if search_fields.get(key)['type'] == 'date':
                date_cond[key] = {'$gte': start, '$lte': end}
    if regex_cond_list:
        cond["$or"] = regex_cond_list
        _LOGGER.info(cond)
    if date_cond:
        cond.update(date_cond)
    return cond


def _check_refinfo(appname, item_id, modelname):
    ref_info = get_topmodel_ids(appname, item_id, modelname)
    if ref_info:
        for ref in ref_info:
            if ref in _TOP_MODELS and ref_info[ref]:
                return True
    else:
        return False


def _unrefered_parents(appname, parent_model, child_model, model_id, confirm):
    return_data = {}
    Parent_Model = classing_model(parent_model)
    pattern = child_model + ".id"   # id field in parent model
    parent_items = Parent_Model.find(
        appname, {pattern: model_id}, fields={"_id": 0}, toarray=True)
    if parent_items:
        for pitem in parent_items:
            upt_val = None
            # 父model存在多个子model引用：[{"id":1},{"id":2}]
            child_info = pitem.get(child_model)
            if isinstance(child_info, types.ListType):
                for id_dict in child_info:
                    if id_dict.get("id") == model_id:
                        if confirm:
                            child_info.remove(id_dict)
                            upt_val = child_info
                        else:
                            return_data.update({'status': DATA_DELETE_COMFIRM})
                            return return_data
            if isinstance(child_info, types.DictType) and child_info:
                # 父model对只引用单条model：{"id":1}
                return_data.update({'status': DATA_RELETED_BY_OTHER})
                return return_data
            Parent_Model.update(
                appname, {"id": pitem["id"]}, {child_model: upt_val})
    else:
        _LOGGER.info("parent %s has no %s id", parent_model, child_model)


class CommonBase(object):

    @classmethod
    def dec_icon(cls, appname, modelname, model_dict, model_id):
        icon_fields = ['icon', 'logo']
        for icon_field in icon_fields:
            icon_dict = model_dict.get(icon_field)
            if icon_dict:
                icon_id = icon_dict.get('id')
                derefered_icon(
                    appname, modelname, icon_id, model_id, icon_field)

    @classmethod
    def delete_base(cls, appname, model_name, item_id, confirm=False):
        '''
        notice:关联删除，当资源被引用的时候返回DATA_DELETE_COMFIRM,
        确认完后如果资源可以被删除，返回1005，不可删除返回1004
        return_data format below:
            {
            'status': 0,
            'model': {'id':1, 'a':'a', 'b':'b',...}
            }
            {
            'status': 10,  # parameter error
            'model': {'id':1, 'a':'a', 'b':'b',...}
            }
            {
            'status': 1004, # can not be deleted,
            'model': {'id':1, 'a':'a', 'b':'b',...}
            }
            {
            'status': 1005, # can be deleted, but need confirm
            'model': {'id':1, 'a':'a', 'b':'b',...}
            }
        '''
        return_data = {}  # track the data deleted for user log
        Model_Name = classing_model(model_name)  # get model class
        relation = Model_Name.relation
        parent_list = relation.get("parent")
        # get the passed in model content and check it legally
        model = Model_Name.find_one(appname, cond={"id": item_id})
        return_data['model'] = model
        if not model:
            _LOGGER.error("model %s id %s is not exist", model_name, item_id)
            return_data.update({'status': PARAM_ERROR})
            return return_data
        # before enter into delete flow, shoud check weather it is refered by
        # the top model not can not been unrefered, used configuration 'links'
        if _check_refinfo(appname, item_id, model_name):
            return_data.update({'status': DATA_RELETED_BY_OTHER})
            return return_data
        # deal with model's parent model, unrefered with the parent model
        if parent_list:
            for parent in parent_list:
                # delete reference from parent tables
                ret_dict = _unrefered_parents(
                    appname, parent, model_name, item_id, confirm)
                if ret_dict:
                    return_data.update(ret_dict)
                    return return_data
        else:
            _LOGGER.info("%s has no parent model", model_name)
        # unrefered the icon to the model
        cls.dec_icon(appname, model_name, model, item_id)
        Model_Name.remove(appname, {"id": item_id})
        return_data.update({'status': OK})
        return return_data

    @classmethod
    def list_base(cls, appname, model_name, query_dict):
        '''
        notice: get the list data of one model
        '''
        return_data = {}
        Model_Name = classing_model(model_name)
        cond = {}
        list_api = Model_Name.list_api
        if list_api.get("search_fields"):
            search_fields = list_api["search_fields"]
            cond = _search_cond(appname, query_dict, search_fields)
        fields = list_api["fields"]
        fields["_id"] = 0
        sort_field = query_dict['sort_field']
        sort_way = query_dict['sort_way']
        pageindex = query_dict['pageindex']
        pagesize = query_dict['pagesize']
        results = Model_Name.find(
            appname, cond, fields=fields).sort(
            sort_field, sort_way).skip(
            pageindex * pagesize).limit(pagesize)
        total = Model_Name.find(appname, cond).count()
        return_data["results"] = results
        return_data["total"] = total
        return return_data

    @classmethod
    def viewdetail(cls, appname, model_name, model_dict):
        '''
        输入model name，如果该model包含子model，将按照order字段
        将子model排序
        '''
        children = {}
        Model_Class = classing_model(str(model_name))
        if Model_Class.relation:
            children = Model_Class.relation.get("children")
            # if model has several children, eg: predata has searcherfolder,
            # bookmark bookmarkfolder
        if children:
            for key in children:
                Child_Model = classing_model(str(key))
                shortinfo_list = model_dict.get(key)
                if not shortinfo_list:
                    continue
                new_children_list = []
                for shortinfo in shortinfo_list:
                    child_id = shortinfo["id"]
                    child_detail = Child_Model.find_one(
                        appname, {"id": child_id}, fields={"_id": 0})
                    if child_detail:
                        for short in shortinfo:
                            child_detail[short] = shortinfo[short]
                        new_children_list.append(child_detail)
                new_children_list = sorted(
                    new_children_list, key=itemgetter("order"))
                model_dict[key] = new_children_list
        if hasattr(Model_Class, "one2one"):
            # if model refere to other model,eg:speeddial with icon
            single_refs = Model_Class.one2one
            for single in single_refs:
                if model_dict.get(single):
                    single_dict = model_dict.get(single)
                    id_val = single_dict.get('id')
                    cond = {}
                    cond['$or'] = [{'id': id_val}, {'_id': id_val}]
                    modelname = NameFactory.fetch_name(single)
                    Single = classing_model(modelname)
                    item = Single.find_one(appname, cond)
                    if item:
                        single_dict['title'] = item.get('title')
                        model_dict[single] = single_dict
        return model_dict

    @classmethod
    def fetch_lcpn(cls, appname, rule_dict):
        '''
        ref locale and package when item loads
        '''
        res_dict = {}
        Ruledata = classing_model("aosruledata")
        Locale = classing_model("aoslocale")
        Package = classing_model("aospackage")
        ruledata = Ruledata.find_one(appname, {"_id": rule_dict.get('id')})
        cond_locale = {'_id': {'$in': ruledata.get('locale')}}
        locale_list = Locale.find(
            appname, cond_locale, fields={'_id': 0, 'title': 1}, toarray=True)
        if locale_list:
            locales = [p.get('title') for p in locale_list]
            res_dict['locale'] = ','.join(locales)
        cond_package = {'_id': {'$in': ruledata.get('package')}}
        package_list = Package.find(
            appname, cond_package,
            fields={'_id': 0, 'package_name': 1}, toarray=True)
        if package_list:
            packages = [p.get('package_name') for p in package_list]
            res_dict['package'] = ','.join(packages)
        return res_dict

    @classmethod
    def clean_data(cls, modelname, req_dict):
        '''
        notice:the temp_dict pass in, check order field and id field and put it
        into a new children_list;
        now the list req only {'id': 1, 'order':2} for default
        '''
        Model_Class = classing_model(modelname)
        if hasattr(Model_Class, "one2one"):
            one_refs = Model_Class.one2one
            for key in one_refs:
                ori_ref = req_dict.get(key)
                if ori_ref:
                    req_dict[key] = {'id': ori_ref.get('id')}
        children = Model_Class.relation.get("children")
        if not children:
            return req_dict
        for child in children:
            reqlist = req_dict.get(child)
            if reqlist:
                saved_list = []
                for child_info in reqlist:
                    child_dict = {}
                    child_dict['id'] = child_info.get('id')
                    try:
                        child_dict['order'] = int(child_info.get('order', 0))
                    except:
                        raise ParamError('order format error')
                    saved_list.append(child_dict)
                req_dict[child] = saved_list
        return req_dict

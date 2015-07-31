# coding: utf-8
import logging
from cm_console.model.common import classing_model
from cm_console.related.icon import fetch_icon_url
from cm_console.utils.status import PackageType, Image

_LOCAL = "local"
All_FLAG = "all_condition"
_ANDROID = "android"
_PLATFORM = {1: 'android', 2: 'ios', 3: 'pc'}
_LOGGER = logging.getLogger(__name__)


class UploadBase(object):

    def __init__(self, check_success, msg, pack_type, res_dict):
        self.check_success = check_success
        self.msg = msg
        self.pack_type = pack_type
        self.res_dict = res_dict


class ios_console(UploadBase):

    appname = 'ios_console'

    def __init__(self, check_success, msg, pack_type, res_dict):
        UploadBase.__init__(self, check_success, msg, pack_type, res_dict)

    def localize_titles(self, locale_titles):
        ThemeLocale = classing_model('themelocale')
        locale_dict = {}
        if locale_titles:
            lt_ids = [lt.get('id') for lt in locale_titles]
            title_infos = ThemeLocale.find(
                self.appname, cond={'id': {'$in': lt_ids}},
                fields={'_id': 0}, toarray=True)
            for title in title_infos:
                locale_dict[title.get('locale')] = title.get('name')
        return locale_dict

    def get_theme(
            self, theme_ids, server=_LOCAL, isfree=True, size=Image.Iph4_5s):
        '''
        get theme by theme ids and paid
        '''
        theme_list = []
        Theme = classing_model('theme')
        theme_infos = Theme.find(
            self.appname,
            cond={'id': {'$in': theme_ids}, 'isfree': isfree, 'size': size},
            fields={'_id': 0}, toarray=True)
        if not theme_infos:
            return theme_list
        for theme_id in theme_ids:
            for theme_info in theme_infos:
                if theme_id == theme_info.get('id'):
                    icon_url = fetch_icon_url(
                        self.appname, theme_info.get('icon'), server)
                    banner_url = fetch_icon_url(
                        self.appname, theme_info.get('logo'), server)
                    locale_titles = theme_info.get('themelocale')
                    theme_dict = {
                        'type': 'theme',
                        'themeId': theme_id,
                        'name': theme_info.get('name'),
                        'titles': self.localize_titles(locale_titles),
                        'downloadUrl': banner_url,
                        'thumbnailUrl': icon_url,
                        'price': theme_info.get('prize', ''),
                        'productId': theme_info.get('paidID', '')}
                    theme_list.append(theme_dict)
        return theme_list

    def get_themefolder(self, folder_ids, server, isfree, size=Image.Iph4_5s):
        folder_list = []
        if not folder_ids:
            return folder_list
        ThemeFolder = classing_model('themefolder')
        folders = ThemeFolder.find(
            self.appname,
            cond={'id': {'$in': folder_ids}, 'isfree': isfree, 'size': size},
            fields={'_id': 0}, toarray=True)
        if not folders:
            return folder_list
        for folder_id in folder_ids:
            for folder in folders:
                if folder_id == folder.get('id'):
                    themes = sorted(
                        folder.get('theme'), key=lambda x: x['order'])
                    theme_ids = [t.get('id') for t in themes]
                    theme_infos = self.get_theme(
                        theme_ids, server=server, isfree=isfree, size=size)
                    icon_url = fetch_icon_url(
                        self.appname, folder.get('icon'), server)
                    locale_titles = folder.get('themelocale')
                    folder_dict = {
                        'type': 'folder',
                        'folderId': folder.get('id'),
                        'name': folder.get('name'),
                        'titles': self.localize_titles(locale_titles),
                        'thumbnailUrl': icon_url,
                        'themes': theme_infos}
                    folder_list.append(folder_dict)
        return folder_list

    def themepush_msg(self, modelname, item, server):
        if not item.get('theme'):
            self.check_success = False
            self.msg = "no theme data found"
            return self.check_success, self.msg, self.res_dict, self.pack_type
        theme_ids = sorted(item.get('theme'), key=lambda x: x['order'])
        theme_ids = [t.get('id') for t in theme_ids]
        folder_ids = []
        if item.get('themefolder'):
            folder_ids = sorted(
                item.get('themefolder'), key=lambda x: x['order'])
            folder_ids = [f.get('id') for f in folder_ids]
        sizes = (Image.Iph4_5s, Image.Iph6_, Image.Ipad,)
        for isfree in (True, False):
            for size in sizes:
                key_name = "%s-%s" % (size, isfree)
                self.res_dict[key_name] = {
                    'free': isfree,
                    'size': size,
                    'theme': self.get_theme(
                        theme_ids, server, isfree, size),
                    'themefolder': self.get_themefolder(
                        folder_ids, server, isfree, size)}
        return self.check_success, self.msg, self.res_dict, self.pack_type


def package_ruledata(appname, ruleid):
    Ruledata = classing_model("aosruledata")
    Source = classing_model("aossource")
    Locale = classing_model("aoslocale")
    Operator = classing_model("aosoperator")
    Package = classing_model("aospackage")
    rule = Ruledata.find_one(appname, {"_id": ruleid})
    locale_ids = rule.get("locale")
    operator_ids = rule.get("operator")
    package_ids = rule.get("package")
    source_ids = rule.get("source")
    rule_dict = {}

    locale_list = []
    if locale_ids == [] or locale_ids == [0]:
        locale_list.append({'title': All_FLAG})
    else:
        cond = {'_id': {'$in': locale_ids}}
        locale_list = Locale.find(
            appname, cond, fields={'_id': 0, 'title': 1}, toarray=True)
    locale_dict = {}
    locale_dict['include'] = [l.get('title') for l in locale_list]
    locale_dict['exclude'] = []
    rule_dict['locales'] = locale_dict

    operator_list = []
    if operator_ids == [] or operator_ids == [0]:
        operator_list.append(All_FLAG)
    else:
        cond = {'_id': {'$in': operator_ids}}
        temp_list = Operator.find(
            appname, cond, fields={'_id': 0, 'code': 1}, toarray=True)
        for operators in temp_list:
            code_str = operators.get('code')
            operator_list.extend(code_str.split(','))
    rule_dict['operators'] = operator_list

    package_list = []
    if package_ids:
        cond = {'_id': {'$in': package_ids}}
        package_list = Package.find(
            appname, cond, fields={'_id': 0, 'package_name': 1}, toarray=True)
        package_list = [p.get('package_name') for p in package_list]
    rule_dict['packages'] = package_list

    source_list = []
    if source_ids == [] or source_ids == [0]:
        source_list.append({'title': All_FLAG})
    else:
        cond = {'_id': {'$in': source_ids}}
        source_list = Source.find(
            appname, cond, fields={'_id': 0, 'title': 1}, toarray=True)
    source_dict = {}
    source_dict['include'] = [s.get('title') for s in source_list]
    source_dict['exclude'] = []
    rule_dict['sources'] = source_dict

    rule_dict["min_version"] = rule.get("min_version")
    rule_dict["max_version"] = rule.get("max_version")
    rule_dict['min_sdk'] = rule.get('min_value')
    rule_dict['max_sdk'] = rule.get('max_value')
    rule_dict['min_mark'] = rule.get('gray_start')
    rule_dict['max_mark'] = rule.get('gray_scale') + rule.get('gray_start')
    rule_dict["os"] = _PLATFORM[rule.get('platform')]
    return rule_dict


def package_data(appname, modelname, item, server):
    '''
     main enter for package data
    '''
    check_success = True
    msg = "upload app %s for model %s" % (appname, modelname)
    pack_type = PackageType.Common

    rule_dict = item.get('aosruledata')
    rule_id = rule_dict.get('id')
    item_id = item.get('id')

    package_dict = {}
    package_dict['id'] = item_id
    package_dict['_sync_key'] = {'id': item_id}
    package_dict['_rule'] = package_ruledata(appname, rule_id)

    res_dict = {}
    func_name = modelname + "_msg"
    try:
        app_obj = eval(appname)(check_success, msg, pack_type, res_dict)
        (check_success, msg, res_dict, pack_type) = getattr(
            app_obj, func_name)(modelname, item, server)
        package_dict['_meta'] = res_dict
        package_dict['pack_type'] = pack_type
    except Exception as e:
        check_success = False
        msg = 'initial upload function error'
        _LOGGER.error(e)
    return check_success, msg, package_dict

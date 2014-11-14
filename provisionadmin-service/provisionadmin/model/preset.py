# coding: utf-8
import logging
from provisionadmin.model.base import ModelBase
from provisionadmin.settings import MODELS
from provisionadmin.model import SESSION_DICT


_LOGGER = logging.getLogger("model")


@classmethod
def get_rules(cls, conn):
    items = []
    print SESSION_DICT
    if not SESSION_DICT:
        return []
    try:
        Session = SESSION_DICT.get(conn)
        sess = Session()
        str_rules = "select id,name,min_version,max_version,min_sdk,max_sdk,\
            gray_level,gray_level_start from configure_rule"
        rules = sess.execute(str_rules)
        for rule in rules:
            rule_dict = {}
            rule_dict["id"] = rule[0]
            rule_dict["name"] = rule[1]
            rule_dict["min_version"] = rule[2]
            rule_dict["max_version"] = rule[3]
            rule_dict["min_sdk"] = rule[4]
            rule_dict["max_sdk"] = rule[5]
            locale_list = []
            source_list = []
            package_list = []
            rule_id = rule[0]
            res_rules = "select distinct b.locale,d.name as loc_name,\
                d.location,f.code as operator_code,f.operator,h.uid as \
                package_name,h.name as package_alias,j.source from \
                configure_rule_locales a, \
                configure_locale b,configure_rule_locations c,\
                configure_location d, configure_rule_operators e,\
                configure_operator f, configure_rule_packages g, \
                configure_package h,configure_rule_sources i,  \
                configure_source j where a.locale_id=b.id and \
                c.location_id=d.id and e.operator_id=f.id and \
                g.package_id=h.id and i.source_id=j.id and \
                a.rule_id=%d and c.rule_id=%d and e.rule_id=%d\
                and g.rule_id=%d and i.rule_id=%d" % tuple([rule_id] * 5)
            resources = sess.execute(res_rules)
            for res in resources:
                _LOGGER.info(res)
                locale_list.append(res[0])
                source_list.append(res[6])
                package_list.append(res[7])
            rule_dict["local"] = list(set(locale_list))
            rule_dict["sources"] = list(set(source_list))
            rule_dict["package"] = list(set(package_list))
            items.append(rule_dict)
    except:
        _LOGGER.info("get_rules connect db failed")
    finally:
        sess.close()
    return items


def classing_model(model_name):
    '''
    type method can be used as a metaclass funtion, when a string "model_name"
    came, it can be return the class
    '''
    if MODELS.get(model_name):
        ATTRS = MODELS.get(model_name)
        if model_name== "bookmarkfolder":
            ATTRS["get_rules"] = get_rules
        return type(model_name, (ModelBase,), ATTRS)
    else:
        return None

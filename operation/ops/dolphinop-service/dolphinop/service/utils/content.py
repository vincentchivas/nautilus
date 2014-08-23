# coder yfhe
import datetime
DEFAULT_SOURCE = 'ofw'
ALL_FLAG = 'all_condition'
OTHER = 'other_condition'
OPERATORS = ['00', '01', '02', '03']
now = datetime.datetime.utcnow
ALL_WEIGHT = 1
MATCH_WEIGHT = 100

BASE_PARAS = [
    'pn&option',
    'src&option',
    'vn&option&1&int',
    'op&option',
    'lc&option',
    'lo&option',
    'mt&option&0&int',
]

SKIN_PARAS = [
    'pn&BeNone',
    #'id&need&None&int',
    #'lc&need',
    'src&option&ofw&str',
    'cv&option&1&int',
    'type&option&skin&str',
    'page&option&1&int',
    'size&option&30&int',
    'mt&option&0&int',
    #'promote&option&True&bool',
]

DESKTOP_PARAS = {
    'pn&BeNone',
    'locale&BeNone',
    'vn&option&0&int',
    'src&option&ofw&str',
    'op&option&other_condition&str',

}

SPLASH_PARAS  = {
    'pn&BeNone',
    'ver&BeNone',
    'vn&BeNone',
    'src&option&ofw&str',
    'net&BeNone',
    'x&BeNone',
    'y&BeNone',
    'w&BeNone',
    'h&BeNone',
    't&option&0&int',
    'mt&option&0&int',
}

RULE_ORIGINIZE = {
    'pn': ['{"_rule.packages":"%s"}', 1],
    'vn': ['{"_rule.min_version":{"$lte":%s},"_rule.max_version":{"$gte":%s}}', 2],
    'op': ['{"_rule.operators":{"$in":["%s",ALL_FLAG]}}', 1],
    'src': ['{"_rule.sources.include":{"$in":["%s",ALL_FLAG]},"_rule.sources.exclude":{"$ne":"%s"}}', 2],
    'lc': ['{"_rule.locales.include":{"$in":["%s",ALL_FLAG]},"_rule.locales.exclude":{"$ne":"%s"}}', 2],
    'lo': ['{"_rule.locations.include":{"$in":["%s",ALL_FLAG]},"_rule.locations.exclude":{"$ne":"%s"}}', 2],
    'time_valid': ['{"_rule.start_time": {"$lte": now()}, "_rule.end_time": {"$gte": now()}}', 0],
    'mt': ['{"mt":{"$gt":%d}}', 1]
}

SKIN_ORIGINIZE = {
    'cv': ["{'c_version': %d}", 1],
    'type': ["{'theme_type':'%s'}", 1],
    'promote': ["{'promote': %s}", 1],
    'uid': ["{'uid': '%s'}", 1],
    'id': ["{'id':%d}", 1],
}

OTHER_ORIGINIZE = {
    'mt': ['{"last_modified":{"$gt":%d}}', 1],
    #'lc': ['{"_rule.locales:', 2],
}

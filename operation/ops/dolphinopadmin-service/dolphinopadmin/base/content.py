#! -*- coding:utf-8 -*-
from django.utils.translation import ugettext_lazy as _

LOCAL = 'local'

CHINA = 'china'

EC2 = 'ec2'

_ONLINE = ['local', 'china', 'ec2']

#PLATFORMS = ["AndroidCN", "AndroidEN", "IosCN", 'IosEN']
PLATFORMS = {
    "AndroidCN": "AosCn",
    "AndroidEN": "AosEn",
    "IosCN": "IosCn",
    "IosEN": "IosEn"
}

ALL_FLAG = 'all_condition'

OTHER = 'other_condition'

PUSH_METHOD = (
    (0, 'modify'),
    (1, 'add'),
    (2, 'delete')
)

LAYOUT_CHOICES = {
    'CategoryAdmin': {
        'layout': {
            "AndroidCN": (
                (1, unicode(_("Webpage"))),
                (2, unicode(_("Novels"))),
                (3, unicode(_("News"))),
                (4, unicode(_("Shopping"))),
                (5, unicode(_("Pictures")))
            ),
            # ((1, u'网页'),
            # (2, u'小说'),
            # (3, u'新闻'),
            # (4, u'购物'),
            # (5, u'图片'),
            # ),
            "AndroidEN": (
                (101, unicode(_("Common Search"))),
                (102, unicode(_("Vertical Search"))),
            ),
            # ((101, u'普通搜索'),
            # (102, u'垂直搜索'),
            # ),
            "IosCN": (
                (201, unicode(_("Common Search"))),
            ),
            # ((201, u'普通搜索'),
            # ),
            "IosEN": (
                (301, unicode(_("Common Search"))),
            )
            # ((301, u'普通搜索'),
            # ),
        },
    },
}

# hotapps new
_TIME_ZONE = 0
BOOLEAN_CHOICES = (
    (1, u'yes'),
    (0, u'no'),
)

FEATURE_TYPE_CHOICES = (
    (u'App', u'App'),
    (u'Category', u'Category'),
)
TYPE_CHOICES = (
    (u'App', u'App'),
    (u'Game', u'Game'),
)

PRICE_CHOICES = (
    (u'Free', u'Free'),
    (u'Limit', u'Limit'),
    (u'Charge', u'Charge'),
    (U'Discount', u'Discount'),
)

# push
PROMOTE_CHOICES = (
    (-1, u'manual'),
    (0, u'none'),
    (1, u'new'),
    (2, u'hot'),
)

TYPE_CHOICES = (
    (u'skin', u'skin'),
    (u'wallpaper', u'wallpaper'),
    (u'font', u'font'),
    (u'activity', u'activity'),
)

TAG_CHOICES = (
    (u'new', unicode(_('New'))),
    (u'hot', unicode(_('Hot'))),
    (u'promotion', unicode(_('Recommend'))),
    ('unknown', unicode(_('Unkown'))),
)

BANNER_TYPES_CHOICES = (
    (0, u'go to detail'),
    (1, u'go to subject'),
)

# websitesnav
NAV_FUNCTION = [
    ("navigation", unicode(_("Navigate"))),
    ("shortcut", unicode(_("Shortcut"))),
    ("hotsearch", unicode(_("HotSearch")))
]  # 针对不同功能衍生出不同的子items

# hotapps platforms
HOTAPPS_PLATFORMS = [
    ("iPad_CN", unicode(_("iPadCn"))),
    ("iPad_EN", unicode(_("iPadEn"))),
    ("iPhone_CN", unicode(_("iPhoneCn"))),
    ("iPhone_EN", unicode(_("iPhoneEn")))
]


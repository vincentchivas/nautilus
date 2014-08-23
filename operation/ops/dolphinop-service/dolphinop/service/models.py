from django.conf import settings
from dolphinop.db import config, desktopdb, weathers, updatedb, iptabledb, webappsdb, topsitedb, \
    skindb, addondb, advertdb, builtindb, contentdb, plinkdb, splashdb, searchdb, subnagdb, \
    treasuredb, navigatedb, notificationdb, gamemodedb, feedbackdb_en, zdb, adpdb

from dolphinop.db.preset import config as config_preset, \
    get_preset, get_presets

DB = settings.DOLPHINOP_DB


config_preset(**DB)

config(desktopdb, **DB)
config(weathers, **DB)
config(updatedb, **DB)
config(iptabledb, **DB)
config(webappsdb, **DB)
config(topsitedb, **DB)
config(skindb, **DB)
config(addondb, **DB)
config(advertdb, **DB)
config(builtindb, **DB)
config(contentdb, **DB)
config(plinkdb, **DB)
config(splashdb, **DB)
config(searchdb, **DB)
config(subnagdb, **DB)
config(treasuredb, **DB)
config(navigatedb, **DB)
config(notificationdb, **DB)
config(gamemodedb, **DB)
config(feedbackdb_en, **DB)
config(zdb, **DB)
config(adpdb, **DB)

# Copyright (c) 2011 Baina Info Inc. All rights reserved.
# @author: Chen Qi
# Modified date:2011-11-22
# email:qchen@bainainfo.com

from django.conf import settings
from dolphinop.db import config, feedbacks, gamemodedb
from dolphinop.db.feedbacks import save_feedback
from dolphinop.db.navigations import config as config_navigation, get_navigation
from dolphinop.db.hotapps import config as config_hotapps, get_featured_apps, get_top_featured, \
    get_trend_apps, get_categories, get_category_apps, get_application_details, get_advertisements,\
    get_daily_recommend_app, get_applications, get_home_page, get_trend_apps_new, get_category_apps_new,\
    get_application_details_new, set_lovecount, get_categories_new, get_top_featured_new, \
    get_relevant_apps

from dolphinop.db.addonstore import config as config_addonstore, get_category,\
    get_category_apps_ranking, get_category_apps_webapp,\
    get_feature_apps, get_hoting_apps, get_subject, get_subject_apps, \
    get_application_detail, get_relevant_addons, get_webapps, get_search

from dolphinop.db import gamecenter

conf = settings.DOLPHINOP_DB
config(feedbacks, **conf)
config(gamemodedb, **conf)

for config_method in (config_navigation, config_hotapps, config_addonstore, gamecenter.config):
    config_method(**conf)

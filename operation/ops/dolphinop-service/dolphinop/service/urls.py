from django.conf.urls.defaults import patterns, include

API_V1 = patterns('dolphinop.service.views',
                  (r'^builtins\.json$', 'builtins.builtins'),
                  (r'^sections$', 'contentcenter.sections'),
                  (r'^novels\.html$', 'contentcenter.novels'),
                  (r'^preset\.json$', 'preset.show_preset'),
                  (r'^recommend\.json$', 'recommend.show_recommends'),
                  (r'^navigate\.json$', 'navigate.show_navigate'),
                  (r'^treasure\.json$', 'treasure.show_treasure'),
                  (r'^skins\.json$', 'skin.show_skins'),
                  (r'^skin/detail\.json$', 'skin.show_skin_detail'),
                  (r'^skin/promote\.json$', 'skin.show_promote_skins'),

                  (r'^skins2\.json$', 'skin2.show_skins'),
                  (r'^skin2/detail\.json$', 'skin2.show_skin_detail'),
                  (r'^skin2/promote\.json$', 'skin2.show_promote_skins'),
                  (r'^skin2/bannerlist\.json$', 'skin2.get_banner_list'),
                  (r'^skin2/subjectlist\.json$', 'skin2.get_subjects'),
                  (r'^skin2/subject\.json$', 'skin2.get_subject'),

                  (r'^adverts\.json$', 'advert.show_adverts'),
                  (r'^advert\.json$', 'advert.show_advert'),
                  (r'^search/cats\.json$', 'search.show_cats'),
                  (r'^search/hotwords\.json$', 'search.show_hotwords'),
                  (r'^search/tracks\.json$', 'search.show_tracks'),
                  (r'^desktop\.json$', 'desktop.get_desktop'),
                  (r'^webapps/cats\.json$', 'webapps.show_cats'),
                  (r'^webapps/subjects\.json$', 'webapps.show_subjects'),
                  (r'^webapps/apps\.json$', 'webapps.show_apps'),
                  (r'^topsite\.json$', 'topsite.show_topsites'),
                  (r'^webapp/notification\.json$',
                   'notification.show_notifications'),
                  (r'^modes\.json$', 'mode.show_modes'),
                  (r'^push/message\.json$', 'push.push_messages'),
                  )


API_V2 = patterns('dolphinop.service.views',
                  (r'^sections$', 'contentcenter.sections2'),
                  (r'^section\.json$', 'contentcenter.section2'),
                  (r'^sections_test$', 'contentcenter.sections_test'),
                  (r'^updateservice\.json$', 'updateservice.show_update2'),
                  (r'^treasure\.json$', 'treasure.show_treasure2'),
                  (r'^search/cats\.json$', 'search.show_cats2'),
                  (r'^push/message\.json$', 'push.push_messages2'),
                  )


API_V3 = patterns('dolphinop.service.views',
                  (r'^search/cats\.json$', 'search.show_cats3'),
                  (r'^updateservice\.json$', 'updateservice.show_update3'),
                  )


API_V4 = patterns('dolphinop.service.views',
                  (r'^updateservice\.json$', 'updateservice.show_update4'),
                  )


SERVICE_V1 = patterns('dolphinop.service.views',
                      (r'^weathers\.json$', 'weathers.get_weather'),
                      )

PROMOTION = patterns('dolphinop.service.views',
                     (r'^active\.json$', 'z.active_track'),
                     (r'^track\.json$', 'z.track'),
                     (r'^test_get$', 'z.get_ad_list'),
                     (r'^edit_get\.json', 'z.edit_get'),
                     (r'^edit_sent\.json', 'z.edit_sent'),
                     (r'^sent_track\.json', 'z.sent_event'),
                     )

urlpatterns = patterns('dolphinop.service.views',
                       (r'^5/(\w+)/(\w+)\.json', 'api_proxy.proxy'),
                       (r'^feedback_en.json', 'feedback_en.save_feedback'),
                       (r'^promotion/', include(PROMOTION)),
                       (r'^1/', include(API_V1)),
                       (r'^2/', include(API_V2)),
                       (r'^3/', include(API_V3)),
                       (r'^4/', include(API_V4)),
                       (r'^addons\.json$', 'addon.show_addons'),
                       (r'^securityapps\.json$', 'securityapps.show_apps'),
                       (r'^promolink\.json$',
                        'promotionlink.show_promotionlinks'),
                       (r'^updateservice\.json$', 'updateservice.show_update'),
                       (r'^splash\.json$', 'splashscreen.show_splashscreens'),
                       (r'^subnag\.json$', 'subnavigation.show_subnavigation'),
                       (r'adblock\.json$', 'adblock.get_blocklist'),
                       )


SERVICEPATTERNS = patterns('dolphinop.service.views',
                           (r'^1/', include(SERVICE_V1)),
                           )

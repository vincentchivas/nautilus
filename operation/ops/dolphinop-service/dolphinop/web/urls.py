# Copyright (c) 2011 Baina Info Inc. All rights reserved. @author: Chen Qi
# date:2011-11-20 email:qchen@bainainfo.com

from django.conf.urls.defaults import patterns, include
# Uncomment the next two lines to enable the admin: from django.contrib
# import admin admin.autodiscover()

hotapps = patterns('dolphinop.web.views',
                   (r'^index\.html$', 'hotapps.hotapps'),
                   (r'^featured\.html$', 'hotapps.show_featured'),
                   (r'^trend\.html$', 'hotapps.show_trend'),
                   (r'^cateapps\.html$', 'hotapps.show_category_apps'),
                   (r'^categories\.html$', 'hotapps.show_categories'),
                   (r'^topfeatured\.html$', 'hotapps.show_top_featured'),
                   (r'^details\.html$', 'hotapps.show_details'),
                   (r'^typeapps\.html$', 'hotapps.show_type_apps'),
                   (r'^ads\.html$', 'hotapps.show_ads'),
                   (r'^lovecount$', 'hotapps.get_lovecount'),
                   (r'^relevant\.html$', 'hotapps.show_relevant_apps'),
                   (r'^appbox.appcache$', 'hotapps.appcache'),
                   )
addonstore = patterns('dolphinop.web.views',
                      (r'^index\.html$', 'addonstore.hotapps'),
                      #(r'^category\.html$', 'addonstore.show_category') ,
                      #(r'^cateapps\.html$', 'addonstore.show_category_apps') ,
                      #(r'^feature\.html?$', 'addonstore.show_feature'),
                      (r'^hoting\.html$', 'addonstore.show_hoting'),
                      #(r'^subject\.html$', 'addonstore.show_subject') ,
                      #(r'^subjectapps\.html$', 'addonstore.show_subject_apps') ,
                      #(r'^webapp\.html$', 'addonstore.show_webapp') ,
                      (r'^detail\.html$', 'addonstore.show_detail'),
                      (r'^relevant\.html$', 'addonstore.show_relevant_apps'),
                      (r'^search$', 'addonstore.search'),
                      (r'^addons.appcache$', 'addonstore.appcache'),
                      )

advert = patterns('dolphinop.service.views',
                  (r'^index\.html', 'z.check_adver'),
                  )
urlpatterns = patterns('dolphinop.web.views',
                       (r'^papaya/', include(advert)),
                       (r'^hotapps/', include(hotapps)),
                       (r'^addons/', include(addonstore)),
                       (r'^static/navigation\.html$', 'navigation.navigation'),
                       (r'^feedback\.html?$', 'feedback.feedback'),
                       (r'^feedback(_(?P<os>[^/]+))?_ok\.html?$',
                        'feedback.feedback_ok'),
                       (r'^navigation.html?$', 'navigation.navigation'),
                       (r'^ipad.appcache$', 'navigation.appcache'),
                       (r'^gamemode\.html', 'gamemode.show_game'),
                       )

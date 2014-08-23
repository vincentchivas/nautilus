# -*- coding:utf-8 -*-
'''
Copyright (c) 2012 Baina Info Inc. All rights reserved.
@Author : Jun Wang
@Date : 2012-5-23
'''
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('dolphinopadmin.content',
                       # Examples:
                       # url(r'^$', 'dolphinopadmin.views.home', name='home'),

                       # Uncomment the admin/doc line below to enable admin
                       # documentation:
                       (r'^upload$', 'views.section_upload'),
                       (r'^insert$', 'views.insert_item'),
                       )

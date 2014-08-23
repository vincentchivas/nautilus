from django.conf.urls.defaults import include, patterns
from dolphinop.service.urls import SERVICEPATTERNS
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
                       (r'^api/', include('dolphinop.service.urls')),
                       (r'^content/', include('dolphinop.content.urls')),
                       (r'^service/', include(SERVICEPATTERNS)),
                       (r'^pages/', include('dolphinop.web.urls')),
                       )

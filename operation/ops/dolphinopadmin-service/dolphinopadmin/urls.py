from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from dolphinopadmin.utils.sites import custom_site
admin.autodiscover()

apis = patterns('',
                (r'^content/', include('dolphinopadmin.content.urls')),
                (r'^update/', include('dolphinopadmin.updateservice.urls')),
                )

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'dolphinopadmin.views.home', name='home'),

                       # Uncomment the admin/doc line below to enable admin documentation:
                       #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       # Uncomment the next line to enable the admin:
                       url(r'^i18n/', include('django.conf.urls.i18n')),
                       url(r'^admin/', include(custom_site.urls),
                           name='dolphin service Web Console'),
                       url(r'^admin_tools/', include('admin_tools.urls')),
                       url(r'^admin/api/', include(apis)),
                       )
urlpatterns += staticfiles_urlpatterns()

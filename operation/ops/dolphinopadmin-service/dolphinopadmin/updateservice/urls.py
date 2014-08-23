from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('dolphinopadmin.updateservice.views',
                       url(r'^upload$', 'file_upload')
                       )

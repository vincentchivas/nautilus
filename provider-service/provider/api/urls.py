from django.conf.urls.defaults import patterns  # , include
from django.views import static

urlpatterns = patterns(
    'provider.api',
    (r'^submit', 'provider.submit_build'),
    (r'^downxml', 'provider.download_xml'),
    (r'^latestxml', 'provider.get_latest_xml'),
    (r'^task', 'provider.submit_task'),
    (r'^status', 'provider.get_build_status'),
    (r'^download/(?P<path>.*)', static.serve,
     {'document_root': '/var/app/data/provider-service/'}
     ),
)

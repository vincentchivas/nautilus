from django.conf.urls.defaults import patterns, include


api_v1 = patterns('dolphinop.content.views',
                  (r'code/update_check\.json$', 'static_file.update_check'),
                  (r'card/data\.json$', 'card.get_data'),
                  (r'page/data\.json$', 'page_data.get_list_data'),
                  (r'page/category\.json$', 'page_data.get_sub_categorys'),
                  )

urlpatterns = patterns('dolphinop.content.views',
                       (r'1/', include(api_v1)),
                       )

from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
    url(r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<slug>[-\w]+)/$', object_detail, name='blog_detail'),

    # url(r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/$',
    #     archive_day,
    #     kwargs = dict(queryset=Post.objects.public(), month_format='%b', date_field='publish'),
    #     name='blog_archive_day'),

    url(r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/$', archive_month, name='blog_archive_month'),

    url(r'^(?P<year>\d{4})/$', archive_year, {}, name='blog_archive_year'),

    url(r'^categories/(?P<slug>[-\w]+)/$',
        category_detail,
        name='blog_category_detail'),

    url (r'^categories/$',
        category_list,
        name='blog_category_list'),

    url (r'^search/$',
        search,
        name='blog_search'),

    url('^tagged/(?P<tag>[^/]+)/$',tag_view, name   = 'blog_tagged_list', ),
    url(r'^page/(?P<page>\w)/$',
        post_list,
        name='blog_index_paginated'),
        
    url(r'^latest$',post_latest,name="blog_latest"),

    url(r'^$',
        post_list,
        kwargs = dict(paginate_by=BLOG_PAGINATE_BY),
        name='blog_index'),
)


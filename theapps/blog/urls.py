from django.conf.urls.defaults import *
from django.views.generic.date_based import archive_year,archive_month,archive_day
from views import *
from models import Category, Post


post_dict = {
    'queryset': Post.published.all(),
    #'template_object_name': 'entry',
}

urlpatterns = patterns('',
    url(r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<slug>[-\w]+)/$',
        post_detail,
        kwargs = dict(post_dict, slug_field='slug', month_format='%b', date_field='publish'),
        name='blog_detail'),

    url(r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/$',
        archive_day,
        kwargs = dict(post_dict, month_format='%b', date_field='publish'),
        name='blog_archive_day'),

    url(r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/$',
        archive_month,
        kwargs = dict(post_dict, month_format='%b', date_field='publish'),
        name='blog_archive_month'),

    url(r'^(?P<year>\d{4})/$',
        archive_year,
        kwargs = dict(post_dict, date_field='publish'),
        name='blog_archive_year'),

    url(r'^categories/(?P<slug>[-\w]+)/$',
        category_detail,
        name='blog_category_detail'),

    url (r'^categories/$',
        category_list,
        name='blog_category_list'),

    url (r'^search/$',
        search,
        name='blog_search'),

    url(r'^page/(?P<page>\w)/$',
        post_list,
        name='blog_index_paginated'),
        
    url(r'^latest$',post_latest,name="blog_latest"),

    url(r'^$',
        post_list,
        kwargs = dict(post_dict, paginate_by=BLOG_PAGINATE_BY),
        name='blog_index'),
)

try:
    from theapps.tagging.views import tagged_object_list
    def tag_view(request, tag):
        queryset = Post.published.all()
        return tagged_object_list(request, queryset, tag, paginate_by=BLOG_PAGINATE_BY,
                template_name="blog/post_tagged.html"
			    )#related_tags=True)
    urlpatterns += patterns('',
        url('^tagged/(?P<tag>[^/]+)/$',tag_view,
            #view   = tagged_object_list,
            #kwargs = dict(post_dict, paginate_by=BLOG_PAGINATE_BY, model=Post, template_name="blog/post_tagged.html"),
            name   = 'blog_tagged_list',
        )
    )
except ImportError:
    pass
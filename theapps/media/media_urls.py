from django.conf.urls.defaults import *

from views import * 

urlpatterns = patterns('',
    url(r'^$', hello),
    url(r'^blank$', blank),
    url(r'^crossdomain.xml$', crossdomain),
    url(r'^static/images/(?P<area>\w+)/$', static_area, {'top':'images'}),
    url(r'^(?P<top>\d+)/(?P<middle>\d+)/(?P<iptime>\w+)$', entity),
    url(r'^(?P<top>\d+)/(?P<middle>\d+)/(?P<iptime>\w+)/$', entity),
    url(r'^(?P<top>\d+)/(?P<middle>\d+)/(?P<iptime>\w+)/query.js$', entity, { 'format':'js' }),
    url(r'^icons/(?P<status>[^/]+)/(?P<variant>\w+)/(?P<base>\w+)-(?P<width>\d+)x(?P<height>\d+)\.(?P<extension>\w+)', status_thumb),
    url(r'^static/images/(?P<area>\w+)/(?P<name>\w+)/(?P<variant>\w+)/(?P<base>\w+)-(?P<width>\d+)x(?P<height>\d+)\.(?P<extension>\w+)', static_thumb, {'top':'images'}),
    url(r'^(?P<top>\d+)/(?P<middle>\d+)/(?P<iptime>\w+)/(?P<sub>\w+)/(?P<variant>\w+)/(?P<base>\w+)-(?P<width>\d+)x(?P<height>\d+)\.(?P<extension>\w+)', thumb),
    url(r'^assets/(?P<top>\d+)/(?P<middle>\d+)/(?P<iptime>\w+)/(?P<sub>\w+)/(?P<variant>\w+)/(?P<base>\w+)-(?P<width>\d+)x(?P<height>\d+)\.(?P<extension>\w+)', thumb),
)
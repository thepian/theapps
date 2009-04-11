from django.http import HttpResponse, Http404
from django.template import loader, RequestContext
from django.shortcuts import render_to_response
from django.core import urlresolvers
from django.utils.encoding import smart_str
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.conf import settings

def sitemap_page(request, sitemaps, section=None, template_name="sitemaps/sitemap.html"):
    maps, urls = [], []
    if section is not None:
        if section not in sitemaps:
            raise Http404("No sitemap available for section: %r" % section)
        maps.append(sitemaps[section])
    else:
        maps = sitemaps.values()
    page = request.GET.get("p", 1)

    for site in maps:
        try:
            if callable(site):
                urls.extend(site().get_urls(page,request))
            else:
                urls.extend(site.get_urls(page,request))
        except EmptyPage:
            raise Http404("Page %s empty" % page)
        except PageNotAnInteger:
            raise Http404("No page '%s'" % page)

    context = {'urlset': urls}
    return render_to_response(template_name, context, context_instance = RequestContext(request))
    
def index(request, sitemaps, template_name="sitemaps/index.xml"):
    sites = []
    protocol = request.is_secure() and 'https' or 'http'
    for section, site in sitemaps.items():
        if callable(site):
            pages = site().paginator.num_pages
        else:
            pages = site.paginator.num_pages
        sitemap_url = urlresolvers.reverse('theapps.sitemaps.views.sitemap', kwargs={'section': section})
        sites.append('%s://%s%s' % (protocol, request.site.domain, sitemap_url))
        if pages > 1:
            for page in range(2, pages+1):
                sites.append('%s://%s%s?p=%s' % (protocol, request.site.domain, sitemap_url, page))
    xml = loader.render_to_string(template_name, {'sitemaps': sites})
    return HttpResponse(xml, mimetype='application/xml')

def sitemap(request, sitemaps, section=None, template_name="sitemaps/sitemap.xml"):
    maps, urls = [], []
    if section is not None:
        if section not in sitemaps:
            raise Http404("No sitemap available for section: %r" % section)
        maps.append(sitemaps[section])
    else:
        maps = sitemaps.values()
    page = request.GET.get("p", 1)

    for site in maps:
        try:
            if callable(site):
                urls.extend(site().get_urls(page,request))
            else:
                urls.extend(site.get_urls(page,request))
        except EmptyPage:
            raise Http404("Page %s empty" % page)
        except PageNotAnInteger:
            raise Http404("No page '%s'" % page)

    xml = smart_str(loader.render_to_string(template_name, {'urlset': urls}))
    return HttpResponse(xml, mimetype='application/xml')


def robots_txt(request, template_name='sitemaps/robots.txt', 
        mimetype='text/plain', status_code=200):
    """
    Returns a generated robots.txt file with correct mimetype (text/plain),
    status code (200 or 404), sitemap url (automatically) and crawl delay 
    (if settings.ROBOTS_CRAWL_DELAY is given).
    
    http://www.javascriptkit.com/howto/robots.shtml
    http://www.google.com/support/webmasters/
    """
    assert 'HTTP_HOST' in request.META

    protocol = request.is_secure() and 'https' or 'http'
    try:
        sitemap_url = urlresolvers.reverse('sitemap.xml')
    except urlresolvers.NoReverseMatch:
        try:
            sitemap_url = urlresolvers.reverse('theapps.sitemaps.views.index')
        except urlresolvers.NoReverseMatch:
            try:
                sitemap_url = urlresolvers.reverse('theapps.sitemaps.views.sitemap')
            except urlresolvers.NoReverseMatch:
                sitemap_url = None
    use_sitemap = getattr(settings, 'ROBOTS_USE_SITEMAP', True)
    if sitemap_url is not None and use_sitemap:
        sitemap_url = "%s://%s%s" % (protocol, request.site.domain, sitemap_url)
        
    rules = []
    resolver = urlresolvers.get_resolver(None)
    #TODO check request.site.root_domain as well
    for url in resolver.url_patterns:
        if hasattr(url,"allow") and url.allow:
            #print request.site.cluster, url.allow.sites
            if len(url.allow.sites) == 0 or request.site.cluster in url.allow.sites:
                rules.extend(url.allow.get_expanded(url.regex.pattern))  
        if hasattr(url,"disallow") and url.disallow:
            #print request.site.cluster, url.disallow.sites
            if len(url.disallow.sites) == 0 or request.site.cluster in url.disallow.sites:
                rules.extend(url.disallow.get_expanded(url.regex.pattern))  
        
    if not len(rules):
        status_code = 404
    t = loader.get_template(template_name)
    c = RequestContext(request, {
        'rules': rules,
        'sitemap_url': sitemap_url,
        'crawl_delay': getattr(settings, 'ROBOTS_CRAWL_DELAY', False)
    })
    return HttpResponse(t.render(c), status=status_code, mimetype=mimetype)


#     pattern = models.CharField(_('pattern'), max_length=255, 
# help_text=_("Case-sensitive. A missing trailing slash does also match to files which start with the name of the pattern, e.g., '/admin' matches /admin.html too. Some major search engines allow an asterisk (*) as a wildcard and a dollar sign ($) to match the end of the URL, e.g., '/*.jpg$'."))

#robot = models.CharField(_('robot'), max_length=255, 
#help_text=_("This should be a user agent string like 'Googlebot'. Enter an asterisk (*) for all user agents. For a full list look at the <a target=_blank href='http://www.robotstxt.org/wc/active/html/index.html'>database of Web Robots</a>."))
#allowed = models.ManyToManyField(Url, blank=True, validator_list=[validators.RequiredIfOtherFieldNotGiven('disallowed')], related_name="allowed", help_text=_("These are URLs which are allowed to be accessed by web robots."))
#disallowed = models.ManyToManyField(Url, blank=True, validator_list=[validators.RequiredIfOtherFieldNotGiven('allowed')], related_name="disallowed", help_text=_("These are URLs which are not allowed to be accessed by web robots."))
#sites = models.ManyToManyField(Site)
#crawl_delay = FloatField(_('crawl delay'), blank=True, null=True, max_digits=3, decimal_places=1, 
#help_text=("From 0.1 to 99.0. This field is supported by some search engines and defines the delay between successive crawler accesses in seconds. If the crawler rate is a problem for your server, you can set the delay up to 5 or 10 or a comfortable value for your server, but it's suggested to start with small values (0.5-1), and increase as needed to an acceptable value for your server. Larger delay values add more delay between successive crawl accesses and decrease the maximum crawl rate to your web server."))

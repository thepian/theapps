import sys
from cStringIO import StringIO
from time import time,sleep, gmtime

from django.conf import settings
from django import http
from django.core.mail import mail_admins

from thepian.tickets import Affinity, IdentityAccess
from userdata import UserData

from theapps.supervisor.sites import Site

def new_affinity(meta,old_affinity=None):
    ip4 = meta.get('HTTP_X_FORWARDED_FOR') or meta.get('HTTP_X_REAL_IP') or meta.get('REMOTE_ADDR') or '127.0.0.1'
    
    affinity = Affinity(meta,ip4=ip4)
    if old_affinity:
        affinity.replaced = True
        affinity.old = old_affinity
    else:
        affinity.replaced = False
    return affinity

class DeviceMiddleware(object):
    """
    Ensures that the devices has an affinity cookie
    """
    def process_request(self, request):
        encoded = request.COOKIES.get(settings.AFFINITY_COOKIE_NAME)
        if encoded:
            affinity = Affinity(request.META,encoded=encoded)
            affinity.replaced = False
            check, check_result, check_pass = affinity.extract_check()
            if not check_pass:
                affinity = new_affinity(request.META,affinity)
        else:
            affinity = new_affinity(request.META)
            
        request.affinity = affinity
        # HTTP_USER_AGENT
        
        encoded = request.COOKIES.get(settings.AFFINITY_ACCESS_COOKIE_NAME)
        if encoded:
            access = IdentityAccess(request.META,identity=affinity,encoded=encoded)
        else:
            #TODO check database?
            access = IdentityAccess(request.META,identity=affinity)
        request.affinity_access = access 
        
        return None

    def process_response(self, request, response):
        if hasattr(request,'affinity'):
            affinity = request.affinity
            if affinity.generated:
                # The browser was given a new affinity
                response.set_cookie(settings.AFFINITY_COOKIE_NAME, affinity.encoded, expires = affinity.cookie_expiry, domain = affinity.cookie_domain)
                #print 'setting ', affinity.encoded, affinity.cookie_domain
            if affinity.replaced:
                # Invalid affinity was skipped
                pass
                #print 'new affinity'
                #TODO record referer domain and path
                
        if hasattr(request,'affinity_access'):
            access = request.affinity_access
            if access.generated or access.changed:
                #TODO HttpOnly flag
                response.set_cookie(settings.AFFINITY_ACCESS_COOKIE_NAME, access.encoded, expires = access.cookie_expiry, domain = access.cookie_domain) #, HttpOnly=True)
        return response

site_patched = False

def patch_site():
    from django.contrib.sites import models
    def init(self,request):
        if hasattr(request,'site'):
            site = request.site
        else:
            site = Site.objects.get_default_site()
        self.domain = site.domain
        self.name = site.name
    models.RequestSite.__init__ = init
    global site_patched
    site_patched = True

class SiteMiddleware(object):
    def process_request(self,request):
        request.is_ajax = request.META.get('HTTP_X_REQUESTED_WITH', None) == 'XMLHttpRequest'
        host = request.META.get('HTTP_HOST',settings.DOMAINS[0])
        request.site = Site.objects.get_site(host)
        if not site_patched:
            patch_site()
        #if not hasattr(request.site,"robot_rules"):
        #    request.site.robot_rules = get_rules_for_site(request.site)
        if hasattr(settings,'URLCONFS'):
            subdomain = request.META['HTTP_HOST'].split('.')[0]
            #TODO proper get subdomain defaulting to www
            if subdomain in settings.URLCONFS:
                request.urlconf = settings.URLCONFS[subdomain]
        request.start_time = time()
        return None
        
    def process_response(self, request, response):
        if hasattr(request,'start_time'):
            response['X-TimeSpent'] = str(time() - request.start_time)
        return response

class UserDataMiddleware(object):
    def process_response(self,request,response):
        old_userdata = UserData(affinity=request.affinity,encoded=request.COOKIES.get(settings.USERDATA_COOKIE_NAME, None))
        new_userdata = UserData(affinity=request.affinity,user=request.user)
        if True:
            max_age = None
            expires = None
            response.set_cookie(settings.USERDATA_COOKIE_NAME,
                    new_userdata.encoded, max_age=max_age,
                    expires=expires, domain=None,
                    path=settings.USERDATA_COOKIE_PATH,
                    secure=settings.USERDATA_COOKIE_SECURE or None)
        
        return response
        """
        encode userdata, set cookie if changes or old is None
        """
        
class ProfilerMiddleware(object):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        if request.META['REMOTE_ADDR'] in settings.INTERNAL_IPS and 'prof' in request.GET:
            import cProfile
            self.profiler = cProfile.Profile()
            return self.profiler.runcall(callback, request, *callback_args, **callback_kwargs)

    def process_response(self, request, response):
        if request.META['REMOTE_ADDR'] in settings.INTERNAL_IPS and 'prof' in request.GET:
            self.profiler.create_stats()
            out = StringIO()
            old_stdout, sys.stdout = sys.stdout, out
            self.profiler.print_stats(1)
            sys.stdout = old_stdout
            response.content = '<pre>%s</pre>' % out.getvalue()
        return response
    

# Temporary, from http://code.djangoproject.com/attachment/ticket/6094/6094.2008-02-01.diff
from django.core.urlresolvers import RegexURLResolver
def resolver(request):
    """
    Returns a RegexURLResolver for the request's urlconf.

    If the request does not have a urlconf object, then the default of
    settings.ROOT_URLCONF is used.
    """
    from django.conf import settings
    urlconf = getattr(request, "urlconf", settings.ROOT_URLCONF)
    return RegexURLResolver(r'^/', urlconf)



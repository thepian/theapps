import sys
from cStringIO import StringIO
from time import time,sleep, gmtime

from django.conf import settings
from django import http
from django.core.mail import mail_admins
from django.core.exceptions import SuspiciousOperation
from django.dispatch import Signal
from userdata import UserData

from theapps.supervisor.sites import Site
from theapps.supervisor.cookie import CookieSigner

try:
    # Use affinity classes from the configured module
    from django.importlib import import_module
    mod = import_module(settings.AFFINITY_MODULE)
    Affinity, AffinityAccess, get_secret = mod.Affinity, mod.AffinityAccess, mod.get_secret
except ImportError:    
    from theapps.supervisor.affinity import Affinity, AffinityAccess, get_secret

def to_cookie_domain(http_host):
    s = http_host.split(".")
    if s[0] in ['media','www']: #TODO improve test to work off configuration
        del s[0]
    return ".".join(s)

affinity_generated_signal = Signal(providing_args=["request","response"])
affinity_replaced_signal = Signal(providing_args=["request","response"])
affinity_access_generated_signal = Signal(providing_args=["request","response"])
affinity_access_replaced_signal = Signal(providing_args=["request","response"])

class DeviceMiddleware(object):
    """
    Ensures that the devices has an affinity cookie
    
    affinity.generated  First visit
    affinity.replaced   Cookie rejected, affinity replaced
    affinity.changed    Cookie changed, and will be set in response
    """
    affinity_signer = CookieSigner(settings.AFFINITY_COOKIE_NAME,constructor=Affinity,get_secret=get_secret)
    access_signer = CookieSigner(settings.AFFINITY_ACCESS_COOKIE_NAME,constructor=AffinityAccess,get_secret=get_secret,message_envelope="%(key)s:%(value)s:%(identity)s")
    
    def process_request(self, request):
        try:
            request.affinity = self.affinity_signer.input(request.COOKIES)
        except SuspiciousOperation:
            request.affinity = Affinity(meta=request.META)
            request.affinity.replaced = True              
            request.affinity.generated = False              
        else:
            request.affinity = Affinity(meta=request.META)
            request.affinity.replaced = False              
            
        try:
            request.affinity_access = self.affinity_signer.input(request.COOKIES,additional={'identity':request.affinity})
        except SuspiciousOperation:
            request.affinity_access = AffinityAccess(meta=request.META,identity=request.affinity)
            request.affinity_access.replaced = True              
            request.affinity_access.generated = False              
        else:
            request.affinity_access = AffinityAccess(meta=request.META)
            request.affinity_access.replaced = False             

        return None

    def process_response(self, request, response):
        cookie_domain = to_cookie_domain(request.META.get('HTTP_HOST',settings.DOMAINS[0]))
        if request.affinity.changed:
            if request.affinity.generated:
                affinity_generated_signal.send(self,request=request,response=response)
            if request.affinity.replaced:
                affinity_replaced_signal.send(self,request=request,response=response)
            self.affinity_signer.output(response,request.affinity,expires=settings.AFFINITY_EXPIRY,domain=cookie_domain)
            
        if request.affinity_access.changed:
            if request.affinity_access.generated:
                affinity_access_generated_signal.send(self,request=request,response=response)
            if request.affinity_access.replaced:
                affinity_access_replaced_signal.send(self,request=request,response=response)
            #TODO HttpOnly flag
            self.access_signer.output(response,request.affinity_access,expires=settings.AFFINITY_EXPIRY,domain=cookie_domain,additional={'identity':request.affinity})
        
        return response
        
site_patched = False

def patch_site():
    """Override the Django RequestSite constructor with a function that gets the site from the request"""
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



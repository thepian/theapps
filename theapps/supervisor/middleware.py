import sys
from cStringIO import StringIO
from time import time,sleep, gmtime

from django.conf import settings
from django import http
from django.core.mail import mail_admins

from thepian.tickets import Affinity, IdentityAccess
from thepian.conf import structure
from userdata import UserData

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
            site = structure.machine.get_default_site()
        self.domain = site.domain
        self.name = site.name
    models.RequestSite.__init__ = init
    global site_patched
    site_patched = True

class SiteMiddleware(object):
    def process_request(self,request):
        request.is_ajax = request.META.get('HTTP_X_REQUESTED_WITH', None) == 'XMLHttpRequest'
        host = request.META.get('HTTP_HOST',structure.machine.DOMAINS[0])
        request.site = structure.machine.get_site(host)
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


class StandardExceptionMiddleware(object):
    """
    based on http://www.djangosnippets.org/snippets/638/
    """
    def process_exception(self, request, exception):
        # Get the exception info now, in case another exception is thrown later.
        if isinstance(exception, http.Http404):
            return self.handle_404(request, exception)
        else:
            return self.handle_500(request, exception)


    def handle_404(self, request, exception):
        if settings.DEBUG:
            import debug
            return debug.technical_404_response(request, exception)
        else:
            callback, param_dict = resolver(request).resolve404()
            return callback(request, **param_dict)


    def handle_500(self, request, exception):
        from django.core.cache import cache
        
        exc_info = sys.exc_info()
        if settings.DEBUG:
            k = '500:'+ request.affinity.encoded
            r = self.debug_500_response(request, exception, exc_info)
            cache.set(k,r,2000)
            return r
        else:
            self.log_exception(request, exception, exc_info)
            return self.production_500_response(request, exception, exc_info)


    def debug_500_response(self, request, exception, exc_info):
        from django.views import debug
        return debug.technical_500_response(request, *exc_info)


    def production_500_response(self, request, exception, exc_info):
        '''Return an HttpResponse that displays a friendly error message.'''
        callback, param_dict = resolver(request).resolve500()
        return callback(request, **param_dict)


    def exception_email(self, request, exc_info):
        subject = 'Error (%s IP): %s' % ((request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS and 'internal' or 'EXTERNAL'), request.path)
        try:
            request_repr = repr(request)
        except:
            request_repr = "Request repr() unavailable"
        message = "%s\n\n%s" % (_get_traceback(exc_info), request_repr)
        return subject, message


    def log_exception(self, request, exception, exc_info):
        subject, message = self.exception_email(request, exc_info)
        mail_admins(subject, message, fail_silently=True)



def _get_traceback(self, exc_info=None):
    """Helper function to return the traceback as a string"""
    import traceback
    return '\n'.join(traceback.format_exception(*(exc_info or sys.exc_info())))
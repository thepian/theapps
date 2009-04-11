try:
    from functools import update_wrapper
except ImportError:
    from django.utils.functional import update_wrapper # 2.3 2.4 support
    
from django.http import HttpResponseRedirect
from django.utils.http import urlquote

def check_http_access(request,level,domain=None,path=None):
    """
    Regular function used to check if the device/user have the access credentials required
    Returns true if access is granted
    """
    if isinstance(level,basestring):
        level = (level,)
    return _check_http_access(request.affinity_access,request.user_access,level,domain or request.site.domain,path or request.path)

def _check_http_access(affinity_access,user_access,level,domain,path):
    for lvl in level:
        if affinity_access.check_access(lvl,"http",domain,path):
            return True
    return False
    
    
REDIRECT_FIELD_NAME = "next"

def http_access_required(function=None, level="normal", domain=None, path=None, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that the browser or user has the level of access to the path
    """
    if isinstance(level,basestring):
        level = (level,)
    def decorate(view_func):
        return _CheckAccess(view_func,level=level, domain=domain, path=path, login_url=login_url, redirect_field_name=redirect_field_name)

    if function:
        return decorate(function)
    return decorate


class _CheckAccess(object):
    def __init__(self,view_func, level=("normal",), domain=None, path=None, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
        if not login_url:
            from django.conf import settings
            login_url = settings.LOGIN_URL
        self.view_func = view_func
        self.level = level
        self.domain = domain
        self.path = path
        self.login_url = login_url
        self.redirect_field_name = redirect_field_name
        update_wrapper(self,view_func)
        
    def __get__(self, obj, cls=None):
        view_func = self.view_func.__get__(obj,cls)
        return _CheckAccess(view_func, self.login_url, self.redirect_field_name)
        
    def __call__(self,request, *args, **kwargs):
        if _check_http_access(request.affinity_access,request.user_access,self.level,self.domain or request.site.domain,self.path or request.path):
            return self.view_func(request, *args, **kwargs)
        path = urlquote(request.path)
        return HttpResponseRedirect('%s?%s=%s' % (self.login_url, self.redirect_field_name, path))

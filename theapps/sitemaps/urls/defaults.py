from django.core.urlresolvers import RegexURLPattern, RegexURLResolver
from django.core.exceptions import ImproperlyConfigured

from theapps.sitemaps.robots import RobotRule

__all__ = ['handler404', 'handler500', 'include', 'patterns', 'url', 'allow', 'disallow', 'hide']

handler404 = 'django.views.defaults.page_not_found'
handler500 = 'django.views.defaults.server_error'

include = lambda urlconf_module: [urlconf_module]

class RegexURLPattern2(RegexURLPattern):
    def __init__(self, regex, callback, default_args=None, name=None, breadcrumb=None, allow=None, disallow=None, hide=None):
        super(RegexURLPattern2,self).__init__(regex, callback, default_args, name)
        self.breadcrumb = breadcrumb
        self.allow = allow
        if self.allow:
            assert RobotRule.objects.iscompatible(self.allow), "Robot rules in urlconf must be compatible with RobotRule"
        self.disallow = disallow
        if self.disallow:
            assert RobotRule.objects.iscompatible(self.disallow), "Robot rules in urlconf must be compatible with RobotRule"
        self.hide = hide
        if self.hide:
            assert RobotRule.objects.iscompatible(self.hide), "Robot rules in urlconf must be compatible with RobotRule"
            

def patterns(prefix, *args):
    pattern_list = []
    for t in args:
        if isinstance(t, (list, tuple)):
            t = url(prefix=prefix, *t)
        elif isinstance(t, RegexURLPattern):
            t.add_prefix(prefix)
        pattern_list.append(t)
    return pattern_list

def url(regex, view, kwargs=None, name=None, prefix='', breadcrumb=None, allow=None, disallow=None, hide=None):
    if type(view) == list:
        # For include(...) processing.
        return RegexURLResolver(regex, view[0], kwargs)
    else:
        if isinstance(view, basestring):
            if not view:
                raise ImproperlyConfigured('Empty URL pattern view name not permitted (for pattern %r)' % regex)
            if prefix:
                view = prefix + '.' + view
        return RegexURLPattern2(regex, view, kwargs, name, breadcrumb, allow, disallow, hide)

def allow(*robot,**options):
    sites = options.get('sites',())
    if isinstance(sites,basestring): # not hasattr(sites, '__iter__'):
        sites = (sites,)
    return RobotRule(robot,sites,allow=True)
    
def disallow(*robot,**options):
    sites = options.get('sites',())
    if isinstance(sites,basestring): # not hasattr(sites, '__iter__'):
        sites = (sites,)
    return RobotRule(robot,sites,disallow=True)
    
def hide(*robot,**options):
    sites = options.get('sites',())
    if isinstance(sites,basestring): # not hasattr(sites, '__iter__'):
        sites = (sites,)
    return RobotRule(robot,sites)
    

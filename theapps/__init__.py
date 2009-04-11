__author__ = "Henrik Vendelbo"
__copyright__ = "Copyright 2008, Henrik Vendelbo"
__license__ = """
This file is part of Thepian Applications.
Thepian Applications is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
Thepian Applications is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with Thepian Applications.  If not, see <http://www.gnu.org/licenses/>.
"""
__version__ = "0.1"
__email__ = "hvendelbo.dev@googlemail.com"

def get_version():
    return __version__
    
    
def amend_default_settings(defaults):
    from django.conf import settings
    for nm in dir(defaults):
        if nm == nm.upper() and not hasattr(settings,nm):
            setattr(settings,nm,getattr(defaults,nm))
    
def tweak_django():
    tweak_django_conf()
    tweak_django_auth()
    add_live_or_dev()
    
def tweak_django_conf():
    from django import conf
    
    class Settings(conf.Settings):
        def __init__(self, settings_module):
            super(Settings,self).__init__(settings_module)
            self.amend_app_defaults()
            
        def amend_app_defaults(self):
            import imp
            for app in self.INSTALLED_APPS:
                try:
                    f,p,d = imp.find_module("%s.default_settings" % app)
                    print p
                except ImportError:
                    pass
                    
        def nilzh(self):
            #for app in self.INSTALLED_APPS:
            #    try:
            #        mod = __import__(app, {}, {}, [''])
            #        print 'imported',app
            #    except ImportError, e:
            #        raise ImportError("Django Application: %s cannot be imported, %s" % (app,e.message))
                    
            for app in self.INSTALLED_APPS:
                try:
                    defaults = __import__("%s.default_settings" % app, {}, {}, [''])
                    for setting in dir(defaults):
                        if setting == setting.upper() and not hasattr(self,setting):
                            print 'adding default ',app+'.'+setting
                            setattr(self,setting,getattr(defaults,setting))
                except ImportError:
                    pass
                
    # patching the Settings class
    #conf.Settings = Settings
            
    
def tweak_django_auth():
    pass
    
def add_live_or_dev():
    from django.conf import settings
    if getattr(settings,'DEVELOPING',False):
        try:
            from devonly import inject_devonly
            inject_devonly(settings)
        except ImportError:
            pass
    else:
        try:
            from liveonly import inject_liveonly
            inject_liveonly(settings)
        except ImportError:
            pass
    
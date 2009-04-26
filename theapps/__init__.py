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

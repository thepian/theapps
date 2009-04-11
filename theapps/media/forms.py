import re
import urlparse
from django.forms import RegexField, URLField, ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_unicode, smart_str

from django import forms

class UploadFileForm(forms.Form):
    iframe_name = "upload_frame"
    blank_url = "/blank"
    
    file  = forms.FileField()
    
    def __unicode__(self):
        xtra = u'<iframe name="%s" src="%s" width="100" height="18" marginheight="0" marginwidth="0" frameborder="0" scrolling="no"></iframe>' % (
            self.iframe_name,
            self.blank_url,
            )
        return self._html_output(u'<p>%(label)s %(field)s%(help_text)s</p>' + xtra, u'%s', '</p>', u' %s', True)

try:
    from django.conf import settings
    URL_VALIDATOR_USER_AGENT = settings.URL_VALIDATOR_USER_AGENT
except ImportError:
    # It's OK if Django settings aren't configured.
    URL_VALIDATOR_USER_AGENT = 'Django (http://www.djangoproject.com/)'

url_re = re.compile(
    r'^(?:http|https|asset)://' # http:// or https:// or asset://
    r'(?:(?:[A-Z0-9-]+\.)+[A-Z]{2,6}|' #domain...
    r'localhost|' #localhost...
    r'static|'
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
    r'(?::\d+)?' # optional port
    r'(?:/?|/\S+)$', re.IGNORECASE)

class MediaURLFormField(RegexField):
    default_error_messages = {
        'invalid': _(u'Enter a valid URL.'),
        'invalid_link': _(u'This URL appears to be a broken link.'),
    }

    def __init__(self, max_length=None, min_length=None, verify_exists=False,
            validator_user_agent=URL_VALIDATOR_USER_AGENT, *args, **kwargs):
        super(MediaURLFormField, self).__init__(url_re, max_length, min_length, *args,
                                       **kwargs)
        self.verify_exists = verify_exists
        self.user_agent = validator_user_agent

    def clean(self, value):
        # If no URL scheme given, assume http://
        if value and '://' not in value:
            value = u'http://%s' % value
        # If no URL path given, assume /
        if value and not urlparse.urlsplit(value)[2]:
            value += '/'
        value = super(MediaURLFormField, self).clean(value)
        if value == u'':
            return value
        if self.verify_exists and value.startswith(u'http'):
            import urllib2
            headers = {
                "Accept": "text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5",
                "Accept-Language": "en-us,en;q=0.5",
                "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
                "Connection": "close",
                "User-Agent": self.user_agent,
            }
            try:
                req = urllib2.Request(value, None, headers)
                u = urllib2.urlopen(req)
            except ValueError:
                raise ValidationError(self.error_messages['invalid'])
            except: # urllib2.URLError, httplib.InvalidURL, etc.
                raise ValidationError(self.error_messages['invalid_link'])
        return value


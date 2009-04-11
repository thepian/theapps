from django import forms
from django.forms.widgets import flatatt
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

from thepian.tickets import IdentityPath

class MediaAssetInput(forms.TextInput):
    
    def __init__(self, attrs=None, area=None):
        super(MediaAssetInput,self).__init__(attrs=attrs)
        if area:
            self.path = IdentityPath("static",area)
            
    def render(self, name, value, attrs=None):
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '': 
            final_attrs['value'] = force_unicode(value) # Only add the 'value' attribute if a value is non-empty.
        return mark_safe(u'<input%s /><ul></ul>' % flatatt(final_attrs))



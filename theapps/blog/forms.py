"""
Tagging components for Django's ``newforms`` form library.
"""
from django import forms
from django.utils.translation import ugettext as _
from django.conf import settings

from models import Tag
from theapps.publish.tagging import parse_tag_input

class AdminTagForm(forms.ModelForm):
    class Meta:
        model = Tag

    def clean_name(self):
        value = self.cleaned_data['name']
        tag_names = parse_tag_input(value)
        if len(tag_names) > 1:
            raise forms.ValidationError(_('Multiple tags were given.'))
        elif len(tag_names[0]) > settings.MAX_TAG_LENGTH:
            raise forms.ValidationError(
                _('A tag may be no more than %s characters long.') %
                    settings.MAX_TAG_LENGTH)
        return value

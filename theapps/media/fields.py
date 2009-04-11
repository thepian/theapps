from django.db import models
from django import forms

from forms import MediaURLFormField

# TODO http://www.davidcramer.net/code/420/improved-uuidfield-in-django.html#comment-20729

class MediaURLField(models.CharField):
    def __init__(self, verbose_name=None, name=None, verify_exists=True, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 200)
        self.verify_exists = verify_exists
        models.CharField.__init__(self, verbose_name, name, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'form_class': MediaURLFormField, 'verify_exists': self.verify_exists}
        defaults.update(kwargs)
        return super(MediaURLField, self).formfield(**defaults)





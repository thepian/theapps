from django.db import models
from managers import *
from django.utils.translation import ugettext as _

class TagBase(models.Model):
    """
    Base for implementing a model specific tag model.
    Concrete class must supply 'object' field
    """
    name = models.CharField(_('name'), max_length=50)
    #TODO uniqueness constraint on name within object context

    objects = ModelTagManager()

    class Meta:
        abstract = True
        ordering = ('name',)
        verbose_name = _('tag')
        verbose_name_plural = _('tags')
        # Remember to set db_table

    def __unicode__(self):
        return u'%s [%s]' % (self.object, self.tag)

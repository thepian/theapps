import sys
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models import permalink
from django.contrib.auth.models import User
from django.db.models import signals

from theapps.supervisor.fields import IdentityField
from theapps.media.fields import MediaURLField

from datetime import datetime
from managers import *
from theapps.publish.fields import TagField
from theapps.publish.models import TagBase

class Tag(TagBase):
    object      = models.ForeignKey(Post)
    
    class Meta:
        db_table = 'blog_tag'

class Category(models.Model):
    """Category model."""
    title       = models.CharField(_('title'), max_length=100)
    slug        = models.SlugField(_('slug'), unique=True)

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        db_table = 'blog_categories'
        ordering = ('title',)

    def __unicode__(self):
        return u'%s' % self.title

    @permalink
    def get_absolute_url(self):
        return ('blog_category_detail', None, {'slug': self.slug})

class Author(models.Model):
    id = IdentityField(_("identifier"),primary_key=True,auto_generate=True)
    name = models.CharField(_("public name"),max_length=50)
    
    objects = AuthorManager()
        
    def __repr__(self):
        return self.name or 'un-named'
        
    def __unicode__(self):
        return self.name or '-unknown-'
    
MARKUP_CHOICES = (
    ('markdown', 'Markdown'),
    ('rest',     'reStructuredText'),
    ('textile',  'Textile'),
    ('raw',      _('Raw text')),
)

DEFAULT_MARKUP_LANG = "textile" #"markdown"

POST_TEMPLATE_CHOICES = (
    ('blog/post_detail.html', 'Standard Template'),
    ('blog/post_detail2.html', 'Alternate Template'),
)
DEFAULT_POST_TEMPLATE = "blog/post_detail.html"

class Post(models.Model):
    """Blog Post model."""
    STATUS_CHOICES = (
        (1, _('Draft')),
        (2, _('Public')),
    )
    title           = models.CharField(_('title'), max_length=200)
    slug            = models.SlugField(_('slug'), unique_for_month='publish',
                help_text=_('Automatically built from the title. A slug is a short '
                'label generally used in URLs.'),    
    )
    author          = models.ForeignKey(Author)
    body_source = models.TextField(_('body'))
    body = models.TextField(
        _('body in HTML'),
        blank=True,
        editable=False,
    )
    tease_source = models.TextField(_('tease'))
    tease = models.TextField(
        _('tease in HTML'),
        blank=True,
        editable=False,
    )
    markup = models.CharField(
        _('markup language'),
        default=DEFAULT_MARKUP_LANG,
        max_length=8,
        choices=MARKUP_CHOICES,
        help_text=_('Uses "Raw text" if you want enter directly in HTML (or '
                    'apply markup in other place).'),
    )
    status          = models.IntegerField(_('status'), choices=STATUS_CHOICES, default=2)
    allow_comments  = models.BooleanField(_('allow comments'), default=True)
    publish         = models.DateTimeField(_('publish'))
    created         = models.DateTimeField(_('created'), auto_now_add=True)
    modified        = models.DateTimeField(_('modified'), auto_now=True)
    category        = models.ForeignKey(Category, blank=True, null=True)
    tags            = TagField(Tag=Tag)
    template_name   = models.CharField(_('template name'), default=DEFAULT_POST_TEMPLATE, max_length=50, choices=POST_TEMPLATE_CHOICES)
    ext_image_url   = models.URLField(_('external url'), blank=True, null=True)
    illustration    = MediaURLField(_('illustration'), blank=True)
    
    #objects         = models.Manager()
    objects        = BlogManager()

    class Meta:
        verbose_name = _('post')
        verbose_name_plural = _('posts')
        db_table  = 'blog_posts'
        ordering  = ('-publish',)
        get_latest_by = 'publish'

    def __unicode__(self):
        return u'%s' % self.title

    @permalink
    def get_absolute_url(self):
        return ('blog_detail', None, {
            'year': self.publish.year,
            'month': self.publish.strftime('%b').lower(),
            'slug': self.slug
        })
        
    def in_future(self):
        return self.pub_date > datetime.now()
        
    def get_mini_tease(self):
        if len(self.tease_source) < 60:
            return self.tease_source
        return self.tease_source[:60] + "..." #TODO word/sentence break
    get_mini_tease.short_description = "Tease"
    
    def get_monetize_tags(self):
        return [u"slug(%s)" % self.slug] + [u"tag(%s)" % t for t in self.tags.split()]
    monetize_tags = property(get_monetize_tags)
    

def markuping(markup, value):
    """
    Transform plain text markup syntaxes to HTML with filters in
    django.contrib.markup.templatetags.

    *Required arguments:*

        * ``markup``: 'markdown', 'rest' or 'texttile'. For any other string
                    value is returned without modifications.
        * ``value``: plain text input

    """
    if markup == 'markdown':
        from markdown import markdown
        return markdown(value)
    elif markup == 'rest':
        from django.contrib.markup.templatetags.markup import restructuredtext
        return restructuredtext(value)
    elif markup == 'textile':
        from django.contrib.markup.templatetags.markup import textile
        return textile(value)
    else:
        return value            # raw
                
# Pre Save processing

def post_pre_save(sender, instance, signal, *args, **kwargs):
    """
    1. transform plain text markup in body_source to HTML
    2. move from draft to pub, set publish date
    """
    # TODO feedback in admin, and log warning to user
    try:
        instance.body = unicode(markuping(instance.markup, instance.body_source))
    except Exception,e:
        print >>sys.stderr, 'failed to render body markup for blog entry %s' % instance.id
        print >>sys.stderr, e
    try:
        instance.tease = unicode(markuping(instance.markup, instance.tease_source))
    except Exception:
        print >>sys.stderr, 'failed to render tease markup for blog entry %s' % instance.id
        

    try:
        # update instance's pub_date if entry was draft
        e = Post.objects.get(id=instance.id)
        if e.status == 1: # DRAFT
            instance.publish = datetime.now()
    except Post.DoesNotExist:
        pass

signals.pre_save.connect(post_pre_save, sender=Post)

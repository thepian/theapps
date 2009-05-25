from django.contrib.syndication.feeds import FeedDoesNotExist
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.syndication.feeds import Feed
from django.core.urlresolvers import reverse
from theapps.blog.models import Post, Category

from django.utils.feedgenerator import Atom1Feed

from thepian.conf import structure

class BlogPostsFeed(Feed):
            
    def title(self):
        self._site = structure.machine.get_default_site()
        return '%s feed' % self._site.name
        
    def description(self, obj):
        if not obj:
            self._site = structure.machine.get_default_site()
            return '%s posts feed.' % self._site.name
        return "Posts recently categorized as %s" % obj.title
    
    title_template = "feeds/posts_title.html"
    description_template = "feeds/posts_description.html"

    def get_object(self, bits):
        if len(bits) != 1:
            return None
        return Category.objects.get(slug__exact=bits[0])

    def link(self, obj):
        if not obj:
            return reverse('blog_index')
        return obj.get_absolute_url()

    def items(self, obj):
        if not obj:
            return Post.objects.published()[:10]
        return Post.objects.published().filter(category=obj)[:10] # obj.post_set.published()
        
    def item_pubdate(self, obj):
        return obj.publish
        
    def item_author_name(self, item):
        return item.author

class AtomBlogPostsFeed(BlogPostsFeed):
    feed_type = Atom1Feed
    subtitle = BlogPostsFeed.description

class BlogPostsByCategory(Feed):
    _site = structure.machine.get_default_site()
    title = '%s posts category feed' % _site.name
    title_template = "feeds/posts_title.html"
    description_template = "feeds/posts_description.html"
    
    def get_object(self, bits):
        if len(bits) != 1:
            raise ObjectDoesNotExist
        return Category.objects.get(slug__exact=bits[0])

    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return obj.get_absolute_url()

    def description(self, obj):
        return "Posts recently categorized as %s" % obj.title
    
    def items(self, obj):
        return Post.objects.published().filter(category=obj)[:10] # obj.post_set.published()
        
    def item_pubdate(self, obj):
        return obj.publish
        
    def item_author_name(self, item):
        return item.author

class AtomBlogPostsByCategory(BlogPostsByCategory):
    feed_type = Atom1Feed
    subtitle = BlogPostsByCategory.description
    

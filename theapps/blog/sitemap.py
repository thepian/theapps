from theapps.sitemaps import Sitemap
from theapps.blog.models import Post


class BlogSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5
    
    def __init__(self):
        super(BlogSitemap,self).__init__()

    def items(self):
        return Post.objects.published()

    def lastmod(self, obj):
        return obj.publish
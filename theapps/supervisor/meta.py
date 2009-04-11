from django.conf import settings

class MetaInformationManager(object):

    cache = {}
    
    def get_metatags(self, path):
        if path in self.cache:
            return self.cache[path]
        info = self.cache[path] = MetaInformation()
        return info
        
class MetaInformation(object):
    
    objects = MetaInformationManager()
    
    robots = settings.META_ROBOTS
    googlebot = settings.META_GOOGLEBOT
    author = settings.META_AUTHOR
    language = settings.META_LANGUAGE
    country = settings.META_COUNTRY
    description = settings.META_DESCRIPTION
    keywords = settings.META_KEYWORDS
    

from django.conf import settings

class SiteManager(object):
    
    def __init__(self):
        self.cur = None
        # Map of Site instances
        self.sites = {}
        
    def get_current(self):
        if not self.cur:
            self.cur = Site()
            
        return self.cur
        
    def get_default_site(self):
        return self.get_site('www.' + settings.DOMAINS[0])

    def get_site(self,host):
        if host in self.sites:
            return self.sites[host]
        #TODO consider domain redirection rules
        site = Site()
        site.domain = host
        site.base_domain = settings.DOMAINS[0]
        for d in settings.DOMAINS:
            host.endswith(d)
            site.base_doamin = d
        site.name = settings.SITE_TITLE
        self.sites[host] = site
        return site

class Site(object):
    domain = "www.thepia.com"
    name = "Thepia Site"
    objects = SiteManager()
    
    def __repr__(self):
        return self.domain+":"+self.name
    

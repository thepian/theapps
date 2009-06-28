#import datetime, time, calendar
from django.template import loader, RequestContext
from django.http import HttpResponse #, HttpResponseRedirect, HttpResponsePermanentRedirect, HttpResponseGone, Http404 
#from django.core.xheaders import populate_xheaders
#from django.db.models.fields import DateTimeField

class View(object):
    """
    Render a given template with any extra URL parameters in the context as ``{{ params }}``
    """
    def __init__(self, template_name=None, mimetype=None, template_loader=None, template_object_name='object', context_processors=None):
        self.template_name = template_name
        self.mimetype = mimetype
        self.template_loader = template_loader or loader
        self.template_object_name = template_object_name
        self.context_processors = context_processors

    def get_template(self,template_name):
        return self.template_loader.get_template(template_name)
        
    def respond(self, request, dictionary, template_name, extra_context=None, mimetype=None):
        c = RequestContext(request, dictionary, self.context_processors)
        for key, value in (extra_context or {}).items():
            if callable(value):
                c[key] = value()
            else:
                c[key] = value
        t = self.get_template(template_name)
        return HttpResponse(t.render(c), mimetype=mimetype or self.mimetype)
        
    def __call__(self, request, extra_context=None, mimetype=None, *args, **kwargs):
        dictionary = {'params': kwargs}
        return self.respond(request, dictionary, self.template_name, extra_context=extra_context, mimetype=mimetype)
       
#TODO respond with in-browser redirect

def blank(request):
    return HttpResponse('<html><head></head><body></body></html>')
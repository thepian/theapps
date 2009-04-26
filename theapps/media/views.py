from django.http import HttpResponse, Http404
from django.template import RequestContext, loader
from django.conf import settings

from thepian.tickets import Identity
from thepian.assets import Asset

from forms import *

def hello(request):
    msg = '''the {{ HTTP_DOMAIN }} site is not meant to be browsed directly.
        '''.replace('{{ HTTP_DOMAIN }}',request.site.domain)
    if settings.DEVELOPING:
        raise Http404(msg)
    return HttpResponse(msg)
    
def blank(request):
    return HttpResponse('')

def crossdomain(request):
    data = {
        'media_domains': ['media.'+name for name in settings.DOMAINS],
        'base_domains': settings.DOMAINS,
        'star_domains': ['*.'+name for name in settings.DOMAINS],
    }
    return HttpResponse(loader.render_to_string('crossdomain.xml',data,
        context_instance=RequestContext(request)),mimetype="text/x-cross-domain-policy")

def entity(request, top, middle, iptime, format="html"):
    """Describes the assets for an entity in a list
    """
    entity = Identity(path=(top,middle,iptime))
    if request.method == "POST":
        form = UploadFileForm(request.POST,request.FILES)
        if form.is_valid():
            asset = Asset.objects.create(parent=entity)
            uploaded_file = request.FILES['file']
            upload_file = asset.build_upload_file(uploaded_file.name)
            destination = open(upload_file.file_path, 'wb+')
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
            destination.close()
            image_width = int(request.POST.get("image_width","120"))
            image_height= int(request.POST.get("image_height","120"))
            thumbnail = asset.get_thumb(width=image_width,height=image_height)
            
            props = {
                'new_asset_path': asset.path,
                'thumb_url': "http://"+ asset.subdomain+request.site.base_domain+thumbnail.path
            }
            
            return HttpResponse("""
                <html><body>File added
                <script>
                window.name = "%(props)s";
                /*location.replace("/blank#%(asset_path)s");*/</script>
                </body></html>
                """ % {'asset_path': asset.path, 'props': ascii_pack_dict(props).encode("string_escape") } )
    
    query = Asset.objects.filter(path=(top,middle,iptime),valid=True)
    query.ensure_bases()
    mimetype = { 'html':'text/html', 'js':'text/javascript' }[format]
    
    t = loader.get_template('media/query.'+format)
    c = RequestContext(request, { 'entity':entity, 'assets': query })

    return HttpResponse(t.render(c), mimetype=mimetype)
    
def static_area(request, top, area, format="html"):
    query = Asset.objects.filter(path=("static",top,area),valid=True)
    query.ensure_bases()
    mimetype = { 'html':'text/html', 'js':'text/javascript' }[format]
    
    t = loader.get_template('media/query.'+format)
    c = RequestContext(request, { 'assets': query })

    return HttpResponse(t.render(c), mimetype=mimetype)
    
def thumb(request, top, middle, iptime, sub, variant, width, height, extension, base="image0"):
    try:
        asset = Asset.objects.filter(path=(top,middle,iptime,sub)).get()
    except Asset.NotFound:
        raise Http404
        #TODO return file path to temp unavailable thumb

    thumb = asset.get_thumb(width=int(width),height=int(height),variant=variant,extension=extension)
    
    response = HttpResponse('',mimetype="image/png")
    response['Content-Type'] = ""
    response['X-Accel-Redirect'] = "/downloads"+thumb.path
    return response
    
def status_thumb(request, status, variant, width, height, extension, base="image0"):
    asset = Asset.objects.get_status_asset(status)

    thumb = asset.get_thumb(width=int(width),height=int(height),variant=variant,extension=extension)

    response = HttpResponse('',mimetype="image/png")
    response['X-Accel-Redirect'] = "/downloads"+thumb.path
    return response

def static_thumb(request, top, area, name, variant, width, height, extension, base="image0"):
    try:
        asset = Asset.objects.get_static_asset(path=("static",top,area,name))
    except Asset.NotFound:
        raise Http404
        #TODO return file path to temp unavailable thumb

    thumb = asset.get_thumb(width=int(width),height=int(height),variant=variant,extension=extension)
    
    response = HttpResponse('',mimetype="image/png")
    response['Content-Type'] = ""
    response['X-Accel-Redirect'] = "/downloads"+thumb.path
    return response
    

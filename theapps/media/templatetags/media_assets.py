import re
from django import template

from thepian.tickets import Identity
from thepian.assets import resolve_url, resolve_asset, Asset

register = template.Library()

DIMENSIONS = re.compile(r"(\d+)x(\d+)")
OPTS = re.compile(r"(\w+)=(.+)")

@register.tag
def thumbnail_url(parser,token):
    """Construct the url needed to get a thumbnail for media file {% thumbnail_url asset_var 1x1 %}
    save it as variable instead append 'as var_name'
    0x0 x=y "stuff" """
    bits = token.split_contents()
    var_name = None
    if bits[-2] == 'as':
        var_name = bits[-1]
        bits = bits[:-2]
    asset = bits[1]
    width, height = 120,120
    opts = []
    for b in bits[2:]:
        dim = DIMENSIONS.match(b)
        if dim:
            width,height = int(dim.groups()[0]),int(dim.groups()[1])
        o = OPTS.match(b)
        if o:
            opts.append( (o.groups()[0],o.groups()[1]) )
    
    return ThumbnailUrlNode(width,height,opts,var_name,asset=asset)
    
@register.tag
def still_url(parser,token):
    """Construct the url needed to get a the still image for an asset {% still_url asset_var index %}
    save it as variable instead append 'as var_name'
    """
    bits = token.split_contents()
    var_name = None
    if bits[-2] == 'as':
        var_name = bits[-1]
        bits = bits[:-2]
    asset = bits[1]
    index = bits[2]
    return UrlNode(asset,var_name,"still",index=index)
    
@register.tag
def video_url(parser,token):
    """Construct the url needed to get a video file for an asset {% video_url asset_var width type %}"""
    bits = token.split_contents()
    var_name = None
    if bits[-2] == 'as':
        var_name = bits[-1]
        bits = bits[:-2]
    asset = bits[1]
    width = bits[2]
    return UrlNode(asset,var_name,"video",width=width)
        
@register.tag
def uploadbutton(parser,token):
    """{% uploadbutton entity_identity %}<button class="upload">Upload</button>{% enduploadbutton %} """
    bits = token.split_contents()
    var_name = None
    if bits[-2] == 'as':
        var_name = bits[-1]
        bits = bits[:2]
    entity = bits[1]
    nodelist = parser.parse(("enduploadbutton",))
    parser.delete_first_token()
    return UploadButtonNode(entity,nodelist,var_name)

class ThumbnailUrlNode(template.Node):
    
    def __init__(self,width,height,opts,var_name,asset=None,entity=None,variant="0"):
        self.asset = asset and template.Variable(asset) or None
        self.entity = entity and template.Variable(entity) or None
        self.variant = variant
        self.width = width
        self.height = height
        self.opts = [(o[0],template.Variable(o[1])) for o in opts]
        self.var_name = var_name
        
    def render(self, context):
        try:
            if self.asset:
                try:
                    asset = resolve_asset(self.asset.resolve(context))
                except Asset.NotFound:
                    asset = None
                    #TODO handle not found
            else:
                entity = self.entity.resolve(context)
                asset = entity.get_icon_asset()
            if asset:
                thumbnail = asset.get_thumb(variant=self.variant,width=self.width,height=self.height)
                val = "http://"+ asset.subdomain+context['SITE'].base_domain+thumbnail.path
            else:
                #TODO FIX FUX default entity asset !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                val = ''
            if self.var_name:
                context[self.var_name] = val
                return ''
            return val
        except template.VariableDoesNotExist:
            return ''

class UrlNode(template.Node):
    
    def __init__(self,asset,var_name,type,index=None,width=None):
        self.type = type
        self.asset = template.Variable(asset)
        self.index = index
        self.width = width
        self.var_name = var_name
        
    def render(self, context):
        try:
            asset = self.asset.resolve(context)
            try:
                val = resolve_url(asset,context['SITE'],type=self.type,index=self.index)
            except Asset.NotFound:
                val = None
                #TODO handle not found
            if self.var_name:
                context[self.var_name] = val
                return ''
            return val
        except ValueError:
            return ''
        except template.VariableDoesNotExist:
            return ''

class UploadButtonNode(template.Node):
    
    def __init__(self, entity, nodelist, var_name):
        self.entity = template.Variable(entity)
        self.nodelist = nodelist
        self.var_name = var_name
        
    def render(self,context):
        """
        <form action="{{ upload_form.action }}" target="{{ upload_form.iframe_name }}" class="upload" 
        	enctype="multipart/form-data" method="POST">

        	<button title="Upload picture or clip" class="upload">Upload Clip</button>
        {{ upload_form }}
        </form>
        """
        from theapps.media.forms import UploadFileForm
        try:
            entity = self.entity.resolve(context)
        except ValueError:
            return ''
        except template.VariableDoesNotExist:
            return ''
        output = self.nodelist.render(context)
        if hasattr(entity,"id"):
            ident = Identity(encoded=entity.id)
        elif isinstance(entity,Identity):
            ident = entity
        else:
            ident = Identity(encoded=entity) #TODO differentiate tuple vs string
        upload_form = UploadFileForm()
        upload_form.action = ident.get_url(base_domain=context["SITE"].base_domain)
        return '\n'.join((
            '''<form action="%s" target="%s" class="upload" 
            	enctype="multipart/form-data" method="POST">
            ''' % (upload_form.action,upload_form.iframe_name),
            output,
            unicode(upload_form),
            u'</form>'
        ))


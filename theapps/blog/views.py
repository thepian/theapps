from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, loader
from django.core.exceptions import ObjectDoesNotExist
from django.core.xheaders import populate_xheaders
from django.db.models.fields import DateTimeField
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.views.generic import date_based, list_detail
from theapps.blog.models import *

#from theapps.tagging.models import Tag
#from theapps.tagging.utils import get_tag

import time, datetime, calendar
import re

BLOG_PAGINATE_BY = 15

def post_latest(request):
    latest = Post.published.all()[0]
    return HttpResponseRedirect(latest.get_absolute_url())
    

def post_list(request, page=0, paginate_by = BLOG_PAGINATE_BY, queryset = None):
    return list_detail.object_list(
        request,
        queryset = queryset or Post.published.all(),
        paginate_by = paginate_by,
        page = page,
    )
post_list.__doc__ = list_detail.object_list.__doc__


def post_detail(request, year, month, queryset, date_field, month_format='%b', object_id=None, slug=None, 
        slug_field='slug', template_name=None, template_name_field=None,
        template_object_name='object', mimetype=None, allow_future=False
        ):
    """
    An implementation similar to ``django.views.generic.date_based.object_detail``
    It assumes slug uniqueness within month, so it doesn't require day.
    
    which creates a ``QuerySet`` containing drafts and future entries if
    user has permission to change entries (``blog.change_entry``).

    This is useful for preview entries with your own templates and CSS.

    Tip: Uses the *View on site* button in Admin interface to access yours
    drafts and entries in future.
    """
    try:
        y,m,d = time.strptime(year+month+"01", '%Y'+month_format+"%d")[:3]
        date = datetime.date(y,m,d)
        date_to = datetime.date(y,m,calendar.monthrange(y,m)[1])
    except ValueError,e:
        import sys
        from traceback import print_exc
        print e
        print_exc(file=sys.stdout)
        raise Http404

    model = queryset.model

    if isinstance(model._meta.get_field(date_field), DateTimeField):
        lookup_kwargs = {'%s__range' % date_field: (datetime.datetime.combine(date, datetime.time.min), datetime.datetime.combine(date_to, datetime.time.max))}
    else:
        lookup_kwargs = {'%s__range' % date_field: (date, date_to) }

    if request.user.has_perm('blog.change_post'):
        allow_future = True
        queryset = Post.objects.all()
        
    if object_id:
        lookup_kwargs['%s__exact' % model._meta.pk.name] = object_id
    elif slug and slug_field:
        lookup_kwargs['%s__exact' % slug_field] = slug
    else:
        raise AttributeError, "Generic detail view must be called with either an object_id or a slug/slugfield"
    try:
        obj = queryset.get(**lookup_kwargs)
        obj_date = getattr(obj,date_field)
        now = datetime.datetime.now()
        if isinstance(obj_date,datetime.datetime):
            obj_date = obj_date.date()
        if obj_date >= now.date() and not allow_future:
            raise ObjectDoesNotExist("In the future")
    except ObjectDoesNotExist:
        raise Http404, "No %s found for" % model._meta.verbose_name
        
    if not template_name:
        template_name = "%s/%s_detail.html" % (model._meta.app_label, model._meta.object_name.lower())
    if template_name_field:
        template_name_list = [getattr(obj, template_name_field), template_name]
        t = loader.select_template(template_name_list)
    else:
        t = loader.get_template(template_name)
    c = RequestContext(request, { template_object_name: obj })

    response = HttpResponse(t.render(c), mimetype=mimetype)
    populate_xheaders(request, response, model, getattr(obj, obj._meta.pk.name))
    return response


def category_list(request):
    """
    Category list

    Template: ``blog/category_list.html``
    Context:
        object_list
            List of categories.
    """
    return list_detail.object_list(
        request,
        queryset = Category.objects.all(),
        template_name = 'blog/category_list.html',
    )

def category_detail(request, slug):
    """
    Category detail

    Template: ``blog/category_detail.html``
    Context:
        object_list
            List of posts specific to the given category.
        category
            Given category.
    """
    category = get_object_or_404(Category, slug__iexact=slug)

    return list_detail.object_list(
        request,
        queryset = category.post_set.published(),
        extra_context = {'category': category},
        template_name = 'blog/category_detail.html',
    )


# Stop Words courtesy of http://www.dcs.gla.ac.uk/idom/ir_resources/linguistic_utils/stop_words
STOP_WORDS = r"""\b(a|about|above|across|after|afterwards|again|against|all|almost|alone|along|already|also|
although|always|am|among|amongst|amoungst|amount|an|and|another|any|anyhow|anyone|anything|anyway|anywhere|are|
around|as|at|back|be|became|because|become|becomes|becoming|been|before|beforehand|behind|being|below|beside|
besides|between|beyond|bill|both|bottom|but|by|call|can|cannot|cant|co|computer|con|could|couldnt|cry|de|describe|
detail|do|done|down|due|during|each|eg|eight|either|eleven|else|elsewhere|empty|enough|etc|even|ever|every|everyone|
everything|everywhere|except|few|fifteen|fify|fill|find|fire|first|five|for|former|formerly|forty|found|four|from|
front|full|further|get|give|go|had|has|hasnt|have|he|hence|her|here|hereafter|hereby|herein|hereupon|hers|herself|
him|himself|his|how|however|hundred|i|ie|if|in|inc|indeed|interest|into|is|it|its|itself|keep|last|latter|latterly|
least|less|ltd|made|many|may|me|meanwhile|might|mill|mine|more|moreover|most|mostly|move|much|must|my|myself|name|
namely|neither|never|nevertheless|next|nine|no|nobody|none|noone|nor|not|nothing|now|nowhere|of|off|often|on|once|
one|only|onto|or|other|others|otherwise|our|ours|ourselves|out|over|own|part|per|perhaps|please|put|rather|re|same|
see|seem|seemed|seeming|seems|serious|several|she|should|show|side|since|sincere|six|sixty|so|some|somehow|someone|
something|sometime|sometimes|somewhere|still|such|system|take|ten|than|that|the|their|them|themselves|then|thence|
there|thereafter|thereby|therefore|therein|thereupon|these|they|thick|thin|third|this|those|though|three|through|
throughout|thru|thus|to|together|too|top|toward|towards|twelve|twenty|two|un|under|until|up|upon|us|very|via|was|
we|well|were|what|whatever|when|whence|whenever|where|whereafter|whereas|whereby|wherein|whereupon|wherever|whether|
which|while|whither|who|whoever|whole|whom|whose|why|will|with|within|without|would|yet|you|your|yours|yourself|
yourselves)\b"""


def search(request):
    """
    Search for blog posts.

    This template will allow you to setup a simple search form that will try to return results based on
    given search strings. The queries will be put through a stop words filter to remove words like
    'the', 'a', or 'have' to help imporve the result set.

    Template: ``blog/post_search.html``
    Context:
        object_list
            List of blog posts that match given search term(s).
        search_term
            Given search term.
    """
    if request.GET:
        stop_word_list = re.compile(STOP_WORDS, re.IGNORECASE)
        search_term = '%s' % request.GET['q']
        cleaned_search_term = stop_word_list.sub('', search_term)
        cleaned_search_term = cleaned_search_term.strip()
        if len(cleaned_search_term) != 0:
            post_list = Post.objects.filter(body__icontains=cleaned_search_term, status__gte=2, publish__lte=datetime.datetime.now())
            context = {'object_list': post_list, 'search_term':search_term}
            return render_to_response('blog/post_search.html', context, context_instance=RequestContext(request))
        else:
            message = 'Search term was too vague. Please try again.'
            context = {'message':message}
            return render_to_response('blog/post_search.html', context, context_instance=RequestContext(request))
    else:
        return render_to_response('blog/post_search.html', {}, context_instance=RequestContext(request))

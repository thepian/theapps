"""

"""
import datetime, time, calendar
from django.template import loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect, HttpResponseGone, Http404 
from django.core.xheaders import populate_xheaders
from django.db.models.fields import DateTimeField

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
       
class DateBasedView(View):
    
    def __init__(self, queryset, date_field, allow_empty=False, make_object_list=False, allow_future=False, **kwargs):
        super(DateBasedView, self).__init__(**kwargs)     
        self.queryset = queryset
        self.date_field = date_field
        self.allow_empty = allow_empty
        self.make_object_list = make_object_list
        self.allow_future = allow_future
        
class ArchiveYear(DateBasedView):
    """
    Generic yearly archive view.

    Templates: ``<app_label>/<model_name>_archive_year.html``
    Context:
        date_list
            List of months in this year with objects
        year
            This year
        object_list
            List of objects published in the given month
            (Only available if make_object_list argument is True)
    """
    
    def __call__(self, request, year, extra_context=None, mimetype=None):
        if extra_context is None: extra_context = {}
        model = self.queryset.model
        now = datetime.datetime.now()

        #year = kwargs['year'] #TODO why can't this be a regular argument???
        lookup_kwargs = {'%s__year' % self.date_field: year}

        # Only bother to check current date if the year isn't in the past and future objects aren't requested.
        if int(year) >= now.year and not self.allow_future:
            lookup_kwargs['%s__lte' % self.date_field] = now
        date_list = self.queryset.filter(**lookup_kwargs).dates(self.date_field, 'month')
        if not date_list and not self.allow_empty:
            raise Http404
        if self.make_object_list:
            object_list = self.queryset.filter(**lookup_kwargs)
        else:
            object_list = []
        
        model_template_name = "%s/%s_archive_year.html" % (model._meta.app_label, model._meta.object_name.lower())
        dictionary = {
            'date_list' : date_list, 'year':year,
            '%s_list' % self.template_object_name : object_list,
        }
        return self.respond(request, dictionary, self.template_name or model_template_name, extra_context=extra_context, mimetype=mimetype)
        
        
class ArchiveMonth(DateBasedView):
    """
    Generic monthly archive view.

    Templates: ``<app_label>/<model_name>_archive_month.html``
    Context:
        month:
            (date) this month
        next_month:
            (date) the first day of the next month, or None if the next month is in the future
        previous_month:
            (date) the first day of the previous month
        object_list:
            list of objects published in the given month
    """
    def __call__(self, request, year, month, extra_context=None, mimetype=None):
        month_format='%b' #TODO into __init__
        if extra_context is None: extra_context = {}
        try:
            tt = time.strptime("%s-%s" % (year, month), '%s-%s' % ('%Y', month_format))
            date = datetime.date(*tt[:3])
        except ValueError:
            raise Http404

        model = self.queryset.model
        now = datetime.datetime.now()

        # Calculate first and last day of month, for use in a date-range lookup.
        first_day = date.replace(day=1)
        if first_day.month == 12:
            last_day = first_day.replace(year=first_day.year + 1, month=1)
        else:
            last_day = first_day.replace(month=first_day.month + 1)
        lookup_kwargs = {
            '%s__gte' % self.date_field: first_day,
            '%s__lt' % self.date_field: last_day,
        }

        # Only bother to check current date if the month isn't in the past and future objects are requested.
        if last_day >= now.date() and not self.allow_future:
            lookup_kwargs['%s__lte' % self.date_field] = now
        object_list = self.queryset.filter(**lookup_kwargs)
        if not object_list and not self.allow_empty:
            raise Http404

        # Calculate the next month, if applicable.
        if self.allow_future:
            next_month = last_day
        elif last_day <= datetime.date.today():
            next_month = last_day
        else:
            next_month = None

        # Calculate the previous month
        if first_day.month == 1:
            previous_month = first_day.replace(year=first_day.year-1,month=12)
        else:
            previous_month = first_day.replace(month=first_day.month-1)

        model_template_name = "%s/%s_archive_month.html" % (model._meta.app_label, model._meta.object_name.lower())
        date_list = self.queryset.filter(**lookup_kwargs).dates(self.date_field, 'month')
        dictionary = {
            'date_list' : date_list, 
            'year':year,
            '%s_list' % self.template_object_name: object_list,
            'month': date,
            'next_month': next_month,
            'previous_month': previous_month,
        }
        return self.respond(request, dictionary, self.template_name or model_template_name, extra_context=extra_context, mimetype=mimetype)
        


class ObjectDetail(DateBasedView):
    """
    Generic monthly archive view.

    Templates: ``<app_label>/<model_name>_archive_month.html``
    Context:
        month:
            (date) this month
        next_month:
            (date) the first day of the next month, or None if the next month is in the future
        previous_month:
            (date) the first day of the previous month
        object_list:
            list of objects published in the given month

    An implementation similar to ``django.views.generic.date_based.object_detail``
    It assumes slug uniqueness within month, so it doesn't require day.

    which creates a ``QuerySet`` containing drafts and future entries if
    user has permission to change entries (``blog.change_entry``).

    This is useful for preview entries with your own templates and CSS.

    Tip: Uses the *View on site* button in Admin interface to access yours
    drafts and entries in future.

    """
    def __init__(self, queryset, date_field, month_format='%b', slug_field='slug', template_name_field=None, **kwargs):
        super(ObjectDetail, self).__init__(queryset, date_field, **kwargs)  
        self.slug_field = slug_field   
        self.template_name_field = template_name_field
        self.month_format = month_format

    def get_template(self,template_name):
        if self.template_name_field:
            template_name_list = [getattr(obj, self.template_name_field), template_name]
            return self.template_loader.select_template(template_name_list)
        else:
            return self.template_loader.get_template(template_name)

    def __call__(self, request, year, month, object_id=None, slug=None,  extra_context=None, mimetype=None):
        if extra_context is None: extra_context = {}
        try:
            y,m,d = time.strptime(year+month+"01", '%Y'+self.month_format+"%d")[:3]
            date = datetime.date(y,m,d)
            date_to = datetime.date(y,m,calendar.monthrange(y,m)[1])
        except ValueError,e:
            raise Http404

        model = self.queryset.model
        now = datetime.datetime.now()
        #TODO
        # if request.user.has_perm('blog.change_post'):
        #     allow_future = True
        #     queryset = Post.objects.all()

        if isinstance(model._meta.get_field(self.date_field), DateTimeField):
            lookup_kwargs = {'%s__range' % self.date_field: (datetime.datetime.combine(date, datetime.time.min), datetime.datetime.combine(date_to, datetime.time.max))}
        else:
            lookup_kwargs = {'%s__range' % self.date_field: (date, date_to) }

        # Only bother to check current date if the date isn't in the past and future objects aren't requested.
        if date >= now.date() and not self.allow_future:
            lookup_kwargs['%s__lte' % self.date_field] = now
        if object_id:
            lookup_kwargs['%s__exact' % model._meta.pk.name] = object_id
        elif slug and self.slug_field:
            lookup_kwargs['%s__exact' % self.slug_field] = slug
        else:
            raise AttributeError, "Generic detail view must be called with either an object_id or a slug/slugfield"
        try:
            obj = self.queryset.get(**lookup_kwargs)
        except ObjectDoesNotExist:
            raise Http404, "No %s found for" % model._meta.verbose_name

        model_template_name = "%s/%s_detail.html" % (model._meta.app_label, model._meta.object_name.lower())
        dictionary = {
            'year':year,
            'month': month,
            self.template_object_name: obj,
        }
        response = self.respond(request, dictionary, self.template_name or model_template_name, extra_context=extra_context, mimetype=mimetype)
        populate_xheaders(request, response, model, getattr(obj, obj._meta.pk.name))
        return response


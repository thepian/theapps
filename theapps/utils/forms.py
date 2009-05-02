from django import forms

def get_form_field(model,field_name,**kwargs):
    for field in model._meta.fields:
        if field.name == field_name:
            return field.formfield(**kwargs)

def ajaxform(form):
    from http import JsonResponse
    if '__all__' in form.errors:
        form.errors.pop('__all__')
    return JsonResponse({'errors': form.errors, 'valid': not form.errors})


def build_form(Form, _request, *args, **kwargs):
    """Build form using given form class
    Features:
     * detect POST and GET queries
     * detect AJAX queries
     * use initial only in GET queries
     * use POST/FILES only in POST queries
    Arguments:
     * Form - form class
     * _request - request instance (underscore allow us to give request in kwargs)
    """

    from exceptions import AjaxDataException
    # Uncomment and make proper comments then it will be needed
    #if 'get_trigger' in kwargs:
        #get_trigger = kwargs.pop('get_trigger')
    #else:
        #get_trigger = False

    #if 'use_get' in kwargs:
        #use_get = kwargs.pop('use_get')
    #else:
        #use_get = False
    
    #if not get_trigger and use_get:
        #form = Form(_request.GET, [], *args, **kwargs)
    #if not get_trigger and 'POST' == _request.method:
    if _request.method == 'POST':
        kwargs.pop('initial')
        form = Form(_request.POST, _request.FILES, *args, **kwargs)
    else:
        form = Form(*args, **kwargs)
    if '_ajax' in _request.POST:
        raise AjaxDataException({'errors': form.errors.as_json(), 'valid': not form.errors})
    return form

def CustomField(parent_class, model_class, model_field):
    class _CustomField(parent_class):
        def __init__(self, *args, **kwargs):
            super(_CustomField, self).__init__(*args, **kwargs)
            field = model_class._meta.get_field(model_field).formfield()
            for key in field.__dict__:
                setattr(self, key, field.__dict__[key])
    return _CustomField

class Form(forms.Form):
    def as_dl(self):
        "Returns this form rendered as HTML <dt>s and <dd>s -- excluding the <dl></dl>."
        return self._html_output(u'<dt>%(label)s</dt> <dd>%(errors)s%(field)s%(help_text)s</dd>', u'<dd>%s</dd>', '</dd>', u' %s', False)

    
def SmartForm(pop=[]):
    class _SmartForm(forms.Form):
        def __init__(self, *args, **kwargs):
            for arg in pop:
                setattr(self, arg, kwargs.pop(arg))
            super(_SmartForm, self).__init__(*args, **kwargs)
    return _SmartForm

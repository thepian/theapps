from os.path import join
from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.conf import settings

register = template.Library()

@register.tag
def supervisor_info(parser,token):
    """Render a definition list of supervisor information
    """
    bits = token.split_contents()
    var_name = None
    if len(bits)>2 and bits[-2] == 'as':
        var_name = bits[-1]
        bits = bits[:-2]
    return SupervisorInfoNode(var_name)
    
class SupervisorInfoNode(template.Node):
    
    def __init__(self,var_name):
        self.var_name = var_name
        
    def render(self, context):
        try:
            data = {
                'affinity': context.get('AFFINITY',context.get('affinity',None)),
                'affinity_access': context.get('affinity_access',None),
                'user_access': context.get('user_access',None),
                'userdata': context.get('userdata',None)
            }
            val = render_to_string("supervisor/supervisor_info.html", data, context_instance=context)
            if self.var_name:
                context[self.var_name] = val
                return ''
            return val
        except ValueError:
            return ''
        except template.VariableDoesNotExist:
            return ''


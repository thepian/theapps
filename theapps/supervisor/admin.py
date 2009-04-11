from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from models import *

admin.site.register(AccessTicket)
admin.site.register(UsedTicket)
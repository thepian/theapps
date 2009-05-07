import os.path
import time
from datetime import datetime

from django.conf import settings
from thepian.conf import structure

from meta import MetaInformation

def vars(request):
    return {
        'SITE_TITLE' : settings.SITE_TITLE,
        'SITE' : request.site,
        'META' : MetaInformation.objects.get_metatags(path=request.path),
        #TODO any request.site info?
        'contact_email': getattr(settings, 'CONTACT_EMAIL', ''),
        'CONTACT_EMAIL': getattr(settings, 'CONTACT_EMAIL', ''),
        'AFFINITY' : request.affinity,
        'AFFINITY_IP' : request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('HTTP_X_REAL_IP') or request.META.get('REMOTE_ADDR') or '127.0.0.1',
        #'AFFINITY_TIME' : request.affinity.first_datetime, 
        #'AFFINITY_SHARD' : request.affinity.subdomain,
        #'AFFINITY_NUMBER' : request.affinity.number,
        'AFFINITY_PASS' : not request.affinity.changed,
        'AFFINITY_CHECK' : 'no affinity debug info', #'%s == %s' %  (check, check_result),
        'HTTP_COUNTRY' : request.META.get(structure.HTTP_COUNTRY_VARIABLE),
        'HTTP_HOST' : request.site.base_domain,
        #'SHARD_DOMAIN' : request.affinity.domain
    }

def settings_vars(request):
    """ Not terribly secure if templates can be modified by users """
    return {
        'STATIC_URL': settings.STATIC_URL,
        'THEME_STATIC_URL': settings.THEME_STATIC_URL,
        'settings': settings,
        }

def contact_email(request):
    return {'contact_email': getattr(settings, 'CONTACT_EMAIL', '')}
from django.core.management.base import BaseCommand
from theapps.sitemaps import ping_google, ROBOTSTXT_URL

import subprocess
from thepian.conf import structure

class Command(BaseCommand):
    help = "Fetches %s " % ROBOTSTXT_URL

    def execute(self, *args, **options):
        if len(args) == 1:
            sitemap_url = args[0]
        else:
            sitemap_url = None
        subprocess.call('curl %s all_robots.txt' % ROBOTSTXT_URL,cwd=structure.CONF_DIR)

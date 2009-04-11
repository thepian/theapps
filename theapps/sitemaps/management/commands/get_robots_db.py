from django.core.management.base import BaseCommand
from theapps.sitemaps import ping_google


class Command(BaseCommand):
    help = "Fetches http://www.robotstxt.org/db/all.txt "

    def execute(self, *args, **options):
        if len(args) == 1:
            sitemap_url = args[0]
        else:
            sitemap_url = None
        os.system('curl http://www.robotstxt.org/db/all.txt conf/all_robots.txt')
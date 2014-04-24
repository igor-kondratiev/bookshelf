import time

from BeautifulSoup import BeautifulSoup
from django.core.management.base import BaseCommand, CommandError
from mechanize import Browser


class Command(BaseCommand):

    BASE_URL = 'http://www.e-reading.ws'

    def _resolve_absolute_url(self, relative_url):
        return self.BASE_URL + relative_url

    def handle(self, *args, **options):

        browser = Browser()
        for book_type in range(1, 11):
            relative_url = '/bookbytypes.php?type={0}&page=1'.format(book_type)
            browser.open(self._resolve_absolute_url(relative_url))
            soup = BeautifulSoup(browser.response().read())

            print soup.find('center').find('font').find('b').contents[0].encode('utf8')

            time.sleep(0.1)

# coding=utf-8
import os
import time
import urllib2

from BeautifulSoup import BeautifulSoup
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from mechanize import Browser

from books.models import Book, BookMark


class Command(BaseCommand):

    SCRAPER_UID = 'E-READING'
    SITE_USERNAME = 'e_reading'

    BASE_URL = 'http://www.e-reading.ws'

    def __init__(self):
        super(Command, self).__init__()
        self.user = User.objects.get(username=self.SITE_USERNAME)
        self.browser = Browser()

    def _prepare_book_set(self):
        return Book.objects.filter(source=self.SCRAPER_UID)

    def _build_absolute_url_for_book(self, book):
        relative_url = '/book.php?book={0}'.format(book.remote_id)
        return self.BASE_URL + relative_url

    def _process_book(self, book):
        url = self._build_absolute_url_for_book(book)
        self.browser.open(url)

        response = self.browser.response().read()
        book_soup = BeautifulSoup(response)

        mark_span = book_soup.find('span', {'itemprop': 'rating'})
        if mark_span:
            book_mark = mark_span.find('span', {'itemprop': 'average'}).contents[0]
            max_mark = mark_span.find('span', {'itemprop': 'best'}).contents[0]
            print '{0} from {1}'.format(book_mark, max_mark)

            # Saving mark
            db_mark, _ = BookMark.objects.get_or_create(user=self.user, book=book)
            real_mark = float(book_mark) * BookMark.MAX_MARK / float(max_mark)
            db_mark.mark = real_mark
            db_mark.save()

        else:
            print u'Failed to fetch marks for book {0}. {1}.'.format(book.author, book.caption)

        description = book_soup.find('span', {'itemprop': 'description'})
        if description:
            real_description = description.contents[0]
            print real_description

            book.description = real_description
        else:
            print u'Failed to fetch description for book {0}. {1}.'.format(book.author, book.caption)

        image = book_soup.find('img', {'itemprop': 'image'})
        if image:
            image_url = self.BASE_URL + image['src']
            print image_url

            response = urllib2.urlopen(image_url).read()
            image_filename = '{0}.jpg'.format(book.pk)
            full_filename = os.path.join(settings.BOOK_IMAGES_DIR, image_filename)
            with open(full_filename, 'w') as f:
                f.write(response)

            book.image = image_filename
        else:
            print u'Failed to fetch cover for book {0}. {1}.'.format(book.author, book.caption)

        book.save()

    def _safe_process_book(self, book):
        try:
            self._process_book(book)
        except Exception as e:
            print str(e)

    @staticmethod
    def _make_delay():
        time.sleep(0.1)

    def handle(self, *args, **options):
        books = self._prepare_book_set()
        print '{0} books found to process'.format(len(books))

        for book in books:
            self._safe_process_book(book)
            self._make_delay()

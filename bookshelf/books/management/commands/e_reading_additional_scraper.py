# coding=utf-8
import os
import time
import traceback
import urllib2

from BeautifulSoup import BeautifulSoup
from django.conf import settings
from django.core.management.base import BaseCommand
from mechanize import Browser

from books.models import Author, BookGenre, Book


class Command(BaseCommand):

    SCRAPER_UID = 'E-READING'

    BASE_URL = 'http://www.e-reading.ws'

    def __init__(self):
        super(Command, self).__init__()
        self.browser = Browser()

    def _prepare_book_set(self):
        return Book.objects.filter(source=self.SCRAPER_UID)[:5]

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
        else:
            print u'Failed to fetch marks for book {0}. {1}.'.format(book.author, book.caption)

        description = book_soup.find('span', {'itemprop': 'description'})
        if description:
            print description.contents[0]
        else:
            print u'Failed to fetch description for book {0}. {1}.'.format(book.author, book.caption)

        image = book_soup.find('img', {'itemprop': 'image'})
        if image:
            image_url = self.BASE_URL + image['src']
            print image_url
        else:
            print u'Failed to fetch cover for book {0}. {1}.'.format(book.author, book.caption)


    @staticmethod
    def _make_delay():
        time.sleep(0.1)

    def handle(self, *args, **options):
        books = self._prepare_book_set()
        print '{0} books found to process'.format(len(books))

        for book in books:
            self._process_book(book)
            self._make_delay()

# coding=utf-8
import os
import time
import urllib2

from BeautifulSoup import BeautifulSoup
from django.conf import settings
from django.core.management.base import BaseCommand
from mechanize import Browser

from books.models import Author, BookGenre, Book


class Command(BaseCommand):

    SCRAPER_UID = 'E-READING'

    BASE_URL = 'http://www.e-reading.ws'

    BOOK_TYPES_TO_READ = 10
    BOOKS_PER_TYPE = 40
    OFFSET = 10

    BOOKS_SUBDIR = 'e_reading'

    def __init__(self):
        super(Command, self).__init__()
        self.browser = Browser()

    @staticmethod
    def _repr_book(book):
        return u"{0}. {1}. Жанр: {2}. ID = {3}".format(
            book['author'],
            book['caption'],
            ', '.join(book['genres']),
            book['id']
        )

    def _save_book(self, book):
        author = Author.get_or_create_author(book['author'])
        db_book = Book(
            author=author,
            caption=book['caption'],
            text_file=book['filename'],
            source=self.SCRAPER_UID,
            remote_id=book['id']
        )
        db_book.save()

        for genre in book['genres']:
            db_genre = BookGenre.get_or_create_genre(genre)
            db_book.genres.add(db_genre)

        db_book.save()
        return db_book

    def _resolve_absolute_url(self, relative_url):
        return self.BASE_URL + relative_url

    def _parse_book(self, soup):
        book = {
            'id': unicode(soup['bookid']),
            'genres': [],
        }

        links = soup.find('div', {'class': 'bookrecord'}).findAll('a')
        book['author'] = unicode(links[0].contents[0])
        book['caption'] = unicode(links[1].contents[0])

        book_url = '/book.php?book={0}'.format(book['id'])
        self.browser.open(self._resolve_absolute_url(book_url))

        response = self.browser.response().read()
        book_soup = BeautifulSoup(response)

        genres = book_soup.findAll('a', {'itemprop': 'category genre'})
        for genre in genres:
            book['genres'].append(unicode(genre.contents[0]))

        book['filename'] = ''
        txt_link = book_soup.find('a', text='txt')
        if txt_link:
            href = '/' + unicode(txt_link.parent['href'])
            response = urllib2.urlopen(self._resolve_absolute_url(href)).read()

            base_dir = os.path.join(settings.BOOKS_DIR, self.BOOKS_SUBDIR)
            if not os.path.exists(base_dir):
                os.mkdir(base_dir)

            base_filename = os.path.join(self.BOOKS_SUBDIR, u"{0}.txt".format(book['id']))
            filename = os.path.join(settings.BOOKS_DIR, base_filename)
            with open(filename, 'w') as f:
                f.write(response)

            book['filename'] = base_filename
        else:
            print u"Ссылка на скачивание txt файла не найдена для книги {0}".format(book['id'])
            return None

        time.sleep(0.1)

        return book

    def handle(self, *args, **options):

        for book_type in range(self.BOOK_TYPES_TO_READ):
            real_book_type = book_type + 1

            relative_url = '/bookbytypes.php?type={0}&page=1'.format(real_book_type)
            self.browser.open(self._resolve_absolute_url(relative_url))

            response = self.browser.response().read()
            soup = BeautifulSoup(response)

            book_type_name = soup.find('center').find('font').find('b').contents[0]
            print u"Чтение раздела: {0}".format(book_type_name)

            books_list = soup.find('table', {'id': 'zebra', 'class': 'booklist'})
            books_list = books_list.findAll('tr')[:self.BOOKS_PER_TYPE]

            if len(books_list) == 0:
                print u"К сожалению, раздел пуст."
                continue

            for i, book in enumerate(books_list):
                if i < self.OFFSET:
                    continue

                real_book = self._parse_book(book)
                if real_book:
                    self._save_book(real_book)

                    # print self._repr_book(real_book)
                print u"Обработано {0}/{1} книг".format(i+1, len(books_list))

            time.sleep(0.1)

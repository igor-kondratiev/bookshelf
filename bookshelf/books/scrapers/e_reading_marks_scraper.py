import time
import traceback

from django.contrib.auth.models import User

from BeautifulSoup import BeautifulSoup
from mechanize import Browser

from books.models import Book, BookMark


class EReadingMarksScraper(object):

    @staticmethod
    def _build_url_for_book(book):
        return 'http://www.e-reading.ws/book.php?book={0}'.format(book.remote_id)

    @staticmethod
    def _make_delay(delay=0.1):
        time.sleep(delay)

    @staticmethod
    def _get_user_by_name(username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User.objects.create_user(username, 'e_reading@e-reading.ws', 'password')
        return user

    def __init__(self, books=None):
        super(EReadingMarksScraper, self).__init__()

        self._browser = Browser()

        self.books = books
        if not self.books:
            self.books = Book.objects.filter(source='E-READING')

    def _get_book_soup(self, book):
        url = self._build_url_for_book(book)
        self._browser.open(url)
        return BeautifulSoup(self._browser.response().read())

    def _process_comment(self, comment, book):
        stars_span = comment.find('span', {'property': 'v:rating'})
        if stars_span:
            stars = float(comment.find('span', {'property': 'v:rating'}).contents[0])
            max_stars = float(comment.find('span', {'property': 'v:best'}).contents[0])
            username = str(comment.find('span', {'property': 'v:reviewer'}).contents[0])

            real_mark = stars * BookMark.MAX_MARK / max_stars
            user = self._get_user_by_name(username)
            db_mark, _ = BookMark.objects.get_or_create(user=user, book=book)
            db_mark.mark = real_mark
            db_mark.save()

    def _process_book(self, book):
        soup = self._get_book_soup(book)
        comments_div = soup.find('div', {'class': 'comments', 'id': 'comments'})
        comments = comments_div.findAll('p', {'style': 'font-style:italic'})
        for comment in comments:
            self._process_comment(comment, book)

    def _safe_process_book(self, book):
        try:
            self._process_book(book)
        except Exception as e:
            print 'Caught exception {0} while processing book {1}'.format(str(e), book)
            traceback.print_exc()

    def perform_scrape(self):
        books_count = len(self.books)
        for i, book in enumerate(self.books):
            self._safe_process_book(book)
            print 'Book {0} of {1} processed.'.format(i+1, books_count)

            self._make_delay()

        print 'Done.'

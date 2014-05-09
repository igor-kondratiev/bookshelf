# coding=utf-8
import time
import traceback

from BeautifulSoup import BeautifulSoup
from books.models import Book, BookMark
from django.contrib.auth.models import User
from mechanize import Browser


class ImhoScraper(object):
    """
    Скрейпер оценок с сайта brb.to
    """

    BASE_URL = 'http://imhonet.ru'

    USER_NAME = 'imho'
    USER_EMAIL = 'imho@imhonet.ru'
    USER_PASSWORD = 'imho'

    def __init__(self, books=None):
        super(ImhoScraper, self).__init__()

        self.user = self._resolve_user()

        self.books = books
        if not self.books:
            self.books = Book.objects.all()

        self.browser = Browser()

        self._success_count = 0
        self._fail_count = 0

    @staticmethod
    def _make_delay(delay=0.1):
        time.sleep(delay)

    @staticmethod
    def _resolve_user():
        try:
            user = User.objects.get(username=ImhoScraper.USER_NAME)
        except User.DoesNotExist:
            user = User.objects.create_user(ImhoScraper.USER_NAME, ImhoScraper.USER_EMAIL, ImhoScraper.USER_PASSWORD)

        return user

    @staticmethod
    def _get_absolute_url(relative_url):
        return ImhoScraper.BASE_URL + relative_url

    def _go_to_main_page(self):
        root_url = self._get_absolute_url('/')
        self.browser.open(root_url)

    def _get_search_results(self, book):
        self._go_to_main_page()
        form_number = 0
        for form in self.browser.forms():
            if str(form.attrs.get("id")) == 'search-form':
                break
            form_number += 1
        self.browser.select_form(nr=form_number)

        book_query = book.author.name.encode('utf-8') + ' ' + book.caption.encode('utf-8')
        self.browser['search'] = book_query
        self.browser.submit()

        return BeautifulSoup(self.browser.response().read())

    @staticmethod
    def _fetch_link(soup):
        main_div = soup.find('div', {'class': 'main'})
        if main_div:
            search_table = main_div.find('table')
            if search_table:
                result = search_table.find('tr')
                link = result.find('a')['href']
                return link
        return None

    @staticmethod
    def _fetch_marks(soup):
        good_div = soup.find('div', {'class': 'b-tab-item__vote-value m-tab-item__vote-value_type_yes'})
        bad_div = soup.find('div', {'class': 'b-tab-item__vote-value m-tab-item__vote-value_type_no'})

        good = good_div.contents[0]
        bad = bad_div.contents[0]
        return good, bad

    def _process_book(self, book):
        search_list = self._get_search_results(book)
        book_div = search_list.find('div', {'class': 'm-inlineitemslist-item '})
        if book_div:
            counters_div = book_div.find('div', {'class': 'm-inlineitemslist-describe-counters'})
            if counters_div:
                mark_span = counters_div.find('span', {'class': 'is-masked'})
                mark = float(mark_span['data-content'])

                print 'Found mark {0}'.format(mark)
                db_mark, _ = BookMark.objects.get_or_create(user=self.user, book=book)
                db_mark.mark = mark
                db_mark.save()

                self._success_count += 1
                return

        print 'No mark found'
        self._fail_count += 1

    def perform_scrape(self):
        for i, book in enumerate(self.books):
            print 'processing book {0}'.format(book)
            try:
                self._process_book(book)
            except:
                traceback.print_exc()
            print '{0} of {1} books processed'.format(i+1, len(self.books))
            self._make_delay()

        print '{0} books processed successfully, {1} books was not found.'.format(self._success_count, self._fail_count)

        print 'Done.'

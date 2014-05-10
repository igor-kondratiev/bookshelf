# coding=utf-8
from django.core.management.base import BaseCommand
from books.models import Book

from books.scrapers.e_reading_marks_scraper import EReadingMarksScraper


class Command(BaseCommand):

    def __init__(self):
        super(Command, self).__init__()
        self.scraper = EReadingMarksScraper()

    def handle(self, *args, **options):
        self.scraper.perform_scrape()

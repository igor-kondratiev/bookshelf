# coding=utf-8
from django.core.management.base import BaseCommand
from books.models import Book

from books.scrapers.brb_to_scraper import BrbScraper


class Command(BaseCommand):

    def __init__(self):
        super(Command, self).__init__()
        self.scraper = BrbScraper()

    def handle(self, *args, **options):
        self.scraper.perform_scrape()

# coding=utf-8
from django.core.management.base import BaseCommand
from books.models import Book

from books.scrapers.imho_net_scraper import ImhoScraper


class Command(BaseCommand):

    def __init__(self):
        super(Command, self).__init__()
        self.scraper = ImhoScraper()

    def handle(self, *args, **options):
        self.scraper.perform_scrape()

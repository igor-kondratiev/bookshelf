# coding=utf-8
from optparse import make_option
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.models import Avg

from books.models import BookMark, Book


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option(
            '--user',
            dest='username',
            default='e_reading',
        ),
    )

    def __init__(self):
        super(Command, self).__init__()

    def handle(self, *args, **options):
        print options

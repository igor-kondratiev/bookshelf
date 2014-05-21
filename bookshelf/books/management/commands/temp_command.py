# coding=utf-8
from optparse import make_option
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.models import Avg

from books.models import BookMark, Book


class Command(BaseCommand):

    def __init__(self):
        super(Command, self).__init__()

    def handle(self, *args, **options):
        users = list(User.objects.all())
        bulk_list = []
        for i, user in enumerate(users):
            print 'processing user {0}'.format(i+1)
            marks = BookMark.objects.filter(user=user)
            marks_count = marks.count()
            if marks.count() > 40:
                continue

            print '{0} marks left'.format(40 - marks_count)
            present_ids = marks.values_list('book_id')
            books = Book.objects.exclude(pk__in=present_ids).order_by('?')
            created = 0
            for book in books:
                book_marks = BookMark.objects.filter(book=book).order_by('?')
                if book_marks.count():
                    mark = BookMark(
                        user=user,
                        book=book,
                        mark=book_marks[0].mark
                    )
                    bulk_list.append(mark)
                    created += 1

                if created + marks_count >= 40:
                    break

        print 'Executing bulk_create'
        BookMark.objects.bulk_create(bulk_list)
        print 'Done.'

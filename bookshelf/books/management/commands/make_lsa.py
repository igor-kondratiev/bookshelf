import chardet

from books.models import Book
from books.tools.reader import BookReader
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        book = Book.objects.all()[0]

        reader = BookReader(book)

        print 'found {0} words'.format(len(reader.words_list))

        for word in reader.words_list[:100]:
            #print chardet.detect(word.encode('utf-8'))
            print word

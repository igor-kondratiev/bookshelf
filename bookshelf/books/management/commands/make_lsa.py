from numpy import zeros, sum, asarray
from numpy.linalg import svd
from numpy.ma import log

from books.models import Book, BookDistance
from books.tools.reader import BookReader
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    BOOKS_TO_PROCESS = 100

    def __init__(self):
        self.words_dict = {}
        self.keys = []

        self.a = None
        self.u = None
        self.s = None
        self.vt = None

        self.books_count = self.BOOKS_TO_PROCESS

        super(Command, self).__init__()

    def perform_build(self):
        self.keys = [k for k in self.words_dict.keys() if len(self.words_dict[k]) > 1]
        self.keys.sort()

        self.a = zeros([len(self.keys), self.books_count])
        for i, k in enumerate(self.keys):
            for d in self.words_dict[k]:
                self.a[i, d] += 1

        print 'Valuable words found - {0}'.format(len(self.keys))

    # todo: fix it
    def perform_tf_idf(self):
        words_per_doc = sum(self.a, axis=0)
        docs_per_word = sum(asarray(self.a > 0, 'i'), axis=1)
        rows, cols = self.a.shape
        for i in range(rows):
            for j in range(cols):
                self.a[i, j] = (self.a[i, j] / words_per_doc[j]) * log(float(cols) / docs_per_word[i])

    def perform_svd(self):
        self.u, self.s, self.vt = svd(self.a, full_matrices=False)

    def handle(self, *args, **options):
        books = Book.objects.all()[:self.BOOKS_TO_PROCESS]
        self.books_count = len(books)

        for i, book in enumerate(books):
            reader = BookReader(book)
            for word in reader.words_list:
                if word in self.words_dict:
                    self.words_dict[word].append(i)
                else:
                    self.words_dict[word] = [i]

            print 'found {0} words in book {1}'.format(len(reader.words_list), i+1)

        print 'total words count = {0}'.format(len(self.words_dict))

        self.perform_build()
        # self.perform_tf_idf()
        self.perform_svd()

        print 'svd done. len(s) = {0}'.format(self.s.shape)

        w = self.s.shape[0]
        valuable = w / 2
        res_u = self.u[:, :valuable]
        for i in range(self.books_count):
            for j in range(i + 1, self.books_count):
                distance = 0.0
                for k in range(valuable):
                    distance += (res_u[i, k] - res_u[j, k]) * (res_u[i, k] - res_u[j, k])
                distance = pow(distance, 0.5)
                db_distance = BookDistance(
                    first_book=books[i],
                    second_book=books[j],
                    distance=distance
                )
                db_distance.save()

# coding=utf-8
import pymongo

from numpy import zeros, dot, diag
from numpy.linalg import svd
from scipy.cluster.vq import kmeans, vq, whiten

from books.models import Book
from books.tools.reader import BookReader
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    BOOKS_TO_PROCESS = 100
    CLUSTERS_COUNT = 20

    MONGODB_NAME = 'bookshelf'

    def __init__(self):
        self.words_dict = {}
        self.keys = []

        self.a = None
        self.u = None
        self.s = None
        self.vt = None

        self.valuable_count = 0

        self.books_count = self.BOOKS_TO_PROCESS

        self.mongodb = None
        try:
            self.mongodb = pymongo.Connection()[self.MONGODB_NAME]
        except Exception as e:
            print 'Не удалось подключится к Mongo: ' + str(e)

        super(Command, self).__init__()

    def perform_svd(self):
        self.u, self.s, self.vt = svd(self.a, full_matrices=False)

        print "SVD done."

        s_count = self.s.shape[0]
        self.valuable_count = (s_count + 1) / 2
        for i in range(self.valuable_count, s_count):
            self.s[i] = 0

        self.a = dot(dot(self.u, diag(self.s)), self.vt)

        print "Rank reduced."

    def handle(self, *args, **options):
        books = Book.objects.all()[:self.BOOKS_TO_PROCESS]
        self.books_count = len(books)

        readers = []
        for book in books:
            reader = BookReader(book, self.mongodb)
            if reader.words_count == 0:
                continue

            readers.append(reader)
            i = len(readers) - 1

            for word in reader.words_list:
                if word in self.words_dict:
                    self.words_dict[word].append(i)
                else:
                    self.words_dict[word] = [i]

            print 'found {0} words in book {1}'.format(len(reader.words_list), i+1)

        print 'total words count = {0}'.format(len(self.words_dict))

        self.books_count = len(readers)

        self.keys = [k for k in self.words_dict.keys()]
        self.keys.sort()

        self.a = zeros([self.books_count, len(self.keys)])
        for i, k in enumerate(self.keys):
            for d in self.words_dict[k]:
                self.a[d, i] = readers[d].words[k]

        print 'Valuable words found - {0}'.format(len(self.keys))

        self.perform_svd()

        print 'svd done. len(s) = {0}'.format(self.s.shape)

        print 'Clustering started'
        book_vectors = self.u[:, :self.valuable_count]
        prepared_book_vectors = whiten(book_vectors)
        centroids, dist = kmeans(prepared_book_vectors, self.CLUSTERS_COUNT)
        clusters, dists = vq(prepared_book_vectors, centroids)

        print 'Clustering finished. Saving results'

        for i in range(self.books_count):
            book = readers[i].db_book
            book.cluster_id = clusters[i]
            book.save()

        print 'Done.'

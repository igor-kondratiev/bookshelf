# coding=utf-8
from math import isinf

import pymongo
from numpy import zeros, sum
from numpy.linalg import svd
from numpy.ma import log
from scipy.stats import spearmanr
from django.core.management.base import BaseCommand

from books.models import Book, BookDistance
from books.tools.reader import BookReader


class Command(BaseCommand):

    BOOKS_TO_PROCESS = 200

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

    def perform_tf_idf(self):
        words_per_doc = sum(self.a, axis=0)
        docs_per_word = sum(self.a, axis=1)
        rows, cols = self.a.shape
        for i in range(rows):
            for j in range(cols):
                if words_per_doc[j] != 0:
                    self.a[i, j] = (self.a[i, j] / words_per_doc[j]) * log(float(cols) / docs_per_word[i])
                    if isinf(self.a[i, j]):
                        print "Infinity found!"

    def perform_svd(self):
        self.u, self.s, self.vt = svd(self.a, full_matrices=False)

        print "SVD done."

        s_count = self.s.shape[0]
        self.valuable_count = (s_count + 1) / 2

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

        self.keys = [k for k in self.words_dict.keys() if len(self.words_dict[k]) > 1]
        self.keys.sort()

        self.a = zeros([len(self.keys), self.books_count])
        for i, k in enumerate(self.keys):
            for d in self.words_dict[k]:
                self.a[i, d] = readers[d].words[k]

        print 'Valuable words found - {0}'.format(len(self.keys))

        self.perform_tf_idf()
        self.perform_svd()

        print 'svd done. len(s) = {0}'.format(self.s.shape)

        BookDistance.objects.all().delete()
        distances = []
        for i in range(self.books_count):
            for j in range(i + 1, self.books_count):
                distance, p = spearmanr(self.vt[:self.valuable_count, i], self.vt[:self.valuable_count, j])
                db_distance = BookDistance(
                    first_book=readers[i].db_book,
                    second_book=readers[j].db_book,
                    distance=distance
                )
                distances.append(db_distance)

        print "Distance calculated. Saving..."
        BookDistance.objects.bulk_create(distances)

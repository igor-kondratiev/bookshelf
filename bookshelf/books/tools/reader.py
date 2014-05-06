# coding=utf-8
import os
import string

from books.tools.stopwords import STOPWORDS_LIST
from books.tools.stemmer import PorterStemmer
from django.conf import settings


class BookReader(object):

    BOOKS_ENCODING = 'windows-1251'
    PUNCTUATION = string.punctuation

    MONGODB_SCHEMA_VERSION = '1'
    MONGODB_COLLECTION_NAME = 'parsed_books_data'

    def __init__(self, book, mongodb=None):
        self.mongodb = mongodb

        self.db_book = book
        self.filename = os.path.join(settings.BOOKS_DIR, book.text_file)
        self.id = book.pk

        self.words = {}
        try:
            self._read_book()
        except Exception as e:
            print "Failed to read book {0}: {1}".format(book.pk, e)

        super(BookReader, self).__init__()

    def _check_token(self, token):
        token = token.lower()
        token = token.strip(self.PUNCTUATION)
        if len(token) > 3 and token.isalpha():
            return token
        else:
            return None

    def _read_book(self):
        # Сначал пробуем достать из монго
        if self.mongodb:
            collection = self.mongodb[self.MONGODB_COLLECTION_NAME]
            book_data = collection.find_one({'book_id': self.db_book.pk})
            if book_data:
                if book_data['schema_version'] == self.MONGODB_SCHEMA_VERSION:
                    self.words = book_data['words']
                    return
                else:
                    collection.remove(book_data)

        # Если не вышло - парсим из файла
        with open(self.filename, 'r') as f:
            raw_lines = f.readlines()

        lines = []
        for line in raw_lines:
            decoded_line = line.decode(self.BOOKS_ENCODING)
            decoded_line = decoded_line.strip(' \n\r\t')
            if len(decoded_line) > 0:
                lines.append(decoded_line)

        words_candidates = {}
        for line in lines:
            tokens = line.split()
            for token in tokens:
                checked_token = self._check_token(token)
                if checked_token:
                    stemmed_token = self._safe_stem(checked_token)
                    if stemmed_token:
                        prev = words_candidates.get(stemmed_token, 0)
                        words_candidates[stemmed_token] = prev + 1

        for token in words_candidates.iterkeys():
            if not token in STOPWORDS_LIST and words_candidates[token] > 1:
                self.words[token] = words_candidates[token]

        # И сохраним в монго на будущее
        if self.mongodb:
            collection = self.mongodb[self.MONGODB_COLLECTION_NAME]
            book_data = {
                'book_id': self.db_book.pk,
                'schema_version': self.MONGODB_SCHEMA_VERSION,
                'words': self.words
            }
            collection.save(book_data)

    @staticmethod
    def _safe_stem(token):
        try:
            return PorterStemmer.stem(token)
        except:
            return None

    @property
    def words_list(self):
        return list(self.words.keys())

    @property
    def words_count(self):
        return len(self.words)

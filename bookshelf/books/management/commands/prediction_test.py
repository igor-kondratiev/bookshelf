# coding=utf-8
import importlib
import operator
import numpy as np

from math import sqrt

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from books.models import Book, BookMark


class Command(BaseCommand):
    """
    Комманда для тестирования качества различных
    методов прогнозирования
    """

    # Список классов предикторов, которые нужно тестировать
    PREDICTORS = [
        'books.predictors.AverageBookMarkPredictor'
    ]

    @staticmethod
    def _load_predictor(name):
        """
        Импортирует класс-предиктор по его названию
        """
        module_name, class_name = name.rsplit(".", 1)
        module = importlib.import_module(module_name)
        return getattr(module, class_name)

    def __init__(self):
        super(Command, self).__init__()

        # Список классов предикторов
        self._predictor_classes = [self._load_predictor(predictor_name) for predictor_name in self.PREDICTORS]

        # Словарь отклонений для каждого предиктора
        self._rmse = {}

        # Загружаем книги и пользователей
        self._users = list(User.objects.all())
        self._users_dict = dict((user, index) for index, user in enumerate(self._users))

        self._books = list(Book.objects.all())
        self._books_dict = dict((book, index) for index, book in enumerate(self._books))

        # Теперь загружаем оценки
        self._all_marks = list(BookMark.objects.all())

        self._source_marks = []
        self._test_marks = []
        for user in self._users:
            # У каждого пользователя забираем 1/3 оценок в тестовую выборку
            marks_count = user.bookmark_set.count()
            limit = marks_count - marks_count / 3
            self._source_marks.extend(list(user.bookmark_set.all()[:limit]))
            self._test_marks.extend(list(user.bookmark_set.all()[limit:]))

    def handle(self, *args, **options):
        print 'Начало тестирования...'
        print 'Загружено {0} книг, {1} пользователей, {2} оценок'.format(
            len(self._books),
            len(self._users),
            len(self._all_marks)
        )
        print '{0} оценок попало в исходную выборку, {1} оценок в тестовую'.format(
            len(self._source_marks),
            len(self._test_marks)
        )

        # prediction_matrix - матрица с исходной выборкой
        prediction_matrix = np.zeros([len(self._users), len(self._books)])

        for mark in self._source_marks:
            user_index = self._users_dict[mark.user]
            book_index = self._books_dict[mark.book]
            prediction_matrix[user_index, book_index] = mark.mark

        predictors = [predictor(prediction_matrix, self._users_dict, self._books_dict) for predictor in self._predictor_classes]
        print 'Загружено предикторов - {0}:'.format(len(predictors))
        for predictor in predictors:
            print predictor.__class__.__name__

        for predictor in predictors:
            self._rmse[predictor] = 0

        for mark in self._test_marks:
            for predictor in predictors:
                predicted_mark = predictor.predict(mark.user, mark.book)
                self._rmse[predictor] += (mark.mark - predicted_mark) * (mark.mark - predicted_mark)

        for predictor in predictors:
            self._rmse[predictor] = sqrt(self._rmse[predictor] / len(self._test_marks))

        ordered_rmse = sorted(self._rmse.iteritems(), key=operator.itemgetter(1))
        print 'Результаты тестирования - RMSE для каждого предиктора:'
        for rmse in ordered_rmse:
            print '{0} - {1}'.format(rmse[0].__class__.__name__, rmse[1])

        print 'Тестирование завершено.'

# coding=utf-8
import importlib
import operator
from django.db.models import Count
import numpy as np

from math import sqrt

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from books.models import Book, BookMark, PredictedBookMark


class Command(BaseCommand):
    """
    Комманда для тестирования качества различных
    методов прогнозирования
    """

    # Список классов предикторов, в порядке приоритета
    PREDICTORS = [
        'books.predictors.ItemToItemLSAPredictor',
        'books.predictors.ItemToItemCollaborativeCosinePredictor',
        'books.predictors.UserToUserCollaborativeCosinePredictor',
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

        self._users = list(User.objects.all())
        self._users_dict = dict((user, index) for index, user in enumerate(self._users))

        self._books = list(Book.objects.all())
        self._books_dict = dict((book, index) for index, book in enumerate(self._books))

        # Теперь загружаем оценки
        self._all_marks = list(BookMark.objects.all())

    def handle(self, *args, **options):
        print 'Начало прогнозирования...'
        print 'Загружено {0} книг, {1} пользователей, {2} оценок'.format(
            len(self._books),
            len(self._users),
            len(self._all_marks)
        )

        # prediction_matrix - матрица с исходной выборкой
        prediction_matrix = np.zeros([len(self._users), len(self._books)])

        for mark in self._all_marks:
            user_index = self._users_dict[mark.user]
            book_index = self._books_dict[mark.book]
            prediction_matrix[user_index, book_index] = mark.mark

        print 'Загрузка пердикторов...'
        predictors = []
        for i, predictor in enumerate(self._predictor_classes):
            predictors.append(predictor(prediction_matrix, self._users_dict, self._books_dict))
            print '{0} из {1} загружено.'.format(i+1, len(self._predictor_classes))

        print 'Загружено предикторов - {0}:'.format(len(predictors))
        for predictor in predictors:
            print predictor.__class__.__name__

        PredictedBookMark.objects.all().delete()

        bulk_list = []

        for user in self._users:
            user_index = self._users_dict[user]
            for book in self._books:
                book_index = self._books_dict[book]

                if prediction_matrix[user_index, book_index] == 0:
                    for predictor in predictors:
                        predicted_mark = predictor.predict(user, book)
                        if predicted_mark > 0:
                            db_mark = PredictedBookMark(
                                user=user,
                                book=book,
                                mark=predicted_mark
                            )
                            bulk_list.append(db_mark)
                            break

        PredictedBookMark.objects.bulk_create(bulk_list)

        print 'Прогнозирование завершено.'

# coding=utf-8
import numpy as np

from math import sqrt

from books.models import BookDistance


class BasePredictor(object):
    """
    Базовый класс для всех классов-предикторов
    """
    def __init__(self, matrix, users_dict, books_dict):
        """
        Конструктор получает на вход дополнительный
        параметр - матрицу оценок (пользователь, книга)
        0 - нет оценки, а также получает маппинг для индексов
        пользователей и книжек
        """
        super(BasePredictor, self).__init__()
        self._matrix = matrix
        self._users_dict = users_dict
        self._books_dict = books_dict

    def predict(self, user, book):
        """
        Метод, который прогнозирует оценку для книги book
        для пользователя user
        """
        raise NotImplementedError("Метод не определен")


class AverageBookMarkPredictor(BasePredictor):
    """
    Класс, который прогнозирует оценку для книги
    как среднюю оценку для этой книги по остальным пользователям
    """
    def __init__(self, matrix, users_dict, books_dict):
        """
        Конструктор, при инициализации рассчитывает средние оценки
        """
        super(AverageBookMarkPredictor, self).__init__(matrix, users_dict, books_dict)

        # Словарь со средними оценками
        self._book_marks = {}

        # Рассчитываем оценки
        presence_matrix = np.where(self._matrix > 0, 1.0, 0)
        counts = np.sum(presence_matrix, axis=0)
        self._book_marks = np.nan_to_num(np.sum(self._matrix, axis=0) / counts)

    def predict(self, user, book):
        """
        Просто возвращаем предпросчитанную среднюю оценку
        """
        return self._book_marks[self._books_dict[book]]


class UserToUserCollaborativeCosinePredictor(BasePredictor):
    """
    Реализует алгоритм колаборативной фильтрации на основе
    схожести пользователей, использует косинусную метрику
    """

    # Минимальныцй уровень похожести для учета при прогнозировании
    MINIMUM_SIMILARITY = 0.0

    def __init__(self, matrix, users_dict, books_dict):
        """
        Конструктор, сразу рассчитывает схожесть пользователей
        """
        super(UserToUserCollaborativeCosinePredictor, self).__init__(matrix, users_dict, books_dict)

        self._similarities_matrix = np.zeros([len(self._users_dict), len(self._users_dict)])

        for i in range(len(self._users_dict)):
            for j in range(i + 1, len(self._users_dict)):
                vi = self._matrix[i]
                vj = self._matrix[j]

                filtered_vi = np.where(vj > 0, vi, 0)
                filtered_vj = np.where(vi > 0, vj, 0)

                count = np.sum(np.where(filtered_vi * filtered_vj > 0, 1, 0))

                x = sqrt(np.sum(filtered_vi**2))
                y = sqrt(np.sum(filtered_vj**2))

                if x > 0 and y > 0 and count >= 6:
                    x_dot_y = np.sum(filtered_vi*filtered_vj)
                    similarity = x_dot_y / (x * y)
                    self._similarities_matrix[i, j] = similarity
                    self._similarities_matrix[j, i] = similarity

    def predict(self, user, book):
        """
        Просто считаем средневзвешенную оценку на основании
        матрицы похожетстей пользователей
        """
        user_index = self._users_dict[user]
        book_index = self._books_dict[book]

        predicted_mark = 0.0
        total_weights = 0.0
        for u in range(len(self._users_dict)):
            if self._matrix[u, book_index] > 0 and self._similarities_matrix[user_index, u] > self.MINIMUM_SIMILARITY:
                predicted_mark += self._matrix[u, book_index] * self._similarities_matrix[user_index, u]
                total_weights += self._similarities_matrix[user_index, u]

        if total_weights > 0:
            predicted_mark /= total_weights

        return predicted_mark


class UserToUserCollaborativePiersonPredictor(BasePredictor):
    """
    Реализует алгоритм колаборативной фильтрации на основе
    схожести пользователей, использует корреляцию Пирсона
    """

    # Минимальныцй уровень похожести для учета при прогнозировании
    MINIMUM_SIMILARITY = 0.0

    def __init__(self, matrix, users_dict, books_dict):
        """
        Конструктор, сразу рассчитывает схожесть пользователей
        """
        super(UserToUserCollaborativePiersonPredictor, self).__init__(matrix, users_dict, books_dict)

        self._similarities_matrix = np.zeros([len(self._users_dict), len(self._users_dict)])

        presence_matrix = np.where(self._matrix > 0, 1.0, 0)
        counts = np.sum(presence_matrix, axis=1)
        self._average_marks = np.nan_to_num(np.sum(self._matrix, axis=1) / counts)

        for i in range(len(self._users_dict)):
            for j in range(i + 1, len(self._users_dict)):
                vi = self._matrix[i]
                vj = self._matrix[j]

                filtered_vi = np.where(vj > 0, vi, 0)
                filtered_vj = np.where(vi > 0, vj, 0)

                count = np.sum(np.where(filtered_vi * filtered_vj > 0, 1, 0))

                filtered_vi -= np.ones(len(self._books_dict)) * self._average_marks[i]
                filtered_vj -= np.ones(len(self._books_dict)) * self._average_marks[j]

                x = sqrt(np.sum(filtered_vi**2))
                y = sqrt(np.sum(filtered_vj**2))

                if x > 0 and y > 0 and count >= 6:
                    x_dot_y = np.sum(filtered_vi*filtered_vj)
                    similarity = x_dot_y / (x * y)
                    self._similarities_matrix[i, j] = similarity
                    self._similarities_matrix[j, i] = similarity

    def predict(self, user, book):
        """
        Просто считаем средневзвешенную оценку на основании
        матрицы похожетстей пользователей
        """
        user_index = self._users_dict[user]
        book_index = self._books_dict[book]

        predicted_mark = 0.0
        total_weights = 0.0
        for u in range(len(self._users_dict)):
            if self._matrix[u, book_index] > 0 and self._similarities_matrix[user_index, u] > self.MINIMUM_SIMILARITY:
                predicted_mark += (self._matrix[u, book_index] - self._average_marks[u]) * self._similarities_matrix[user_index, u]
                total_weights += self._similarities_matrix[user_index, u]

        if total_weights != 0:
            predicted_mark /= total_weights

            predicted_mark += self._average_marks[user_index]
        else:
            predicted_mark = 0

        return predicted_mark


class ItemToItemLSAPredictor(BasePredictor):
    """
    Прогнозирует оценку как средневзвешенную оценку других
    книг данного пользователя с учетом корреляций, посчитанных по LSA
    """

    # Минимальныцй уровень похожести для учета при прогнозировании
    MINIMUM_SIMILARITY = 0.4

    def __init__(self, matrix, users_dict, books_dict):
        """
        Конструктор, сразу инициализирует матрицу корреляций
        """
        super(ItemToItemLSAPredictor, self).__init__(matrix, users_dict, books_dict)

        self._similarities_matrix = np.zeros([len(self._books_dict), len(self._books_dict)])

        distances = list(BookDistance.objects.all())
        for distance in distances:
            self._similarities_matrix[self._books_dict[distance.first_book], self._books_dict[distance.second_book]] = distance.distance
            self._similarities_matrix[self._books_dict[distance.second_book], self._books_dict[distance.first_book]] = distance.distance

    def predict(self, user, book):
        """
        Просто считаем средневзвешенную оценку на основании
        матрицы похожетстей книг
        """
        user_index = self._users_dict[user]
        book_index = self._books_dict[book]

        predicted_mark = 0.0
        total_weights = 0.0
        for b in range(len(self._books_dict)):
            if self._matrix[user_index, b] > 0 and self._similarities_matrix[book_index, b] > self.MINIMUM_SIMILARITY:
                predicted_mark += self._matrix[user_index, b] * self._similarities_matrix[book_index, b]
                total_weights += self._similarities_matrix[book_index, b]

        if total_weights > 0:
            predicted_mark /= total_weights

        return predicted_mark


class ItemToItemCollaborativeCosinePredictor(BasePredictor):
    """
    Реализует алгоритм колаборативной фильтрации на основе
    схожести книг, использует косинусную метрику
    """

    # Минимальныцй уровень похожести для учета при прогнозировании
    MINIMUM_SIMILARITY = 0.0

    def __init__(self, matrix, users_dict, books_dict):
        """
        Конструктор, сразу рассчитывает схожесть книг
        """
        super(ItemToItemCollaborativeCosinePredictor, self).__init__(matrix, users_dict, books_dict)

        self._similarities_matrix = np.zeros([len(self._books_dict), len(self._books_dict)])

        for i in range(len(self._books_dict)):
            for j in range(i + 1, len(self._books_dict)):
                vi = self._matrix[:, i]
                vj = self._matrix[:, j]

                filtered_vi = np.where(vj > 0, vi, 0)
                filtered_vj = np.where(vi > 0, vj, 0)

                count = np.sum(np.where(filtered_vi * filtered_vj > 0, 1, 0))

                x = sqrt(np.sum(filtered_vi**2))
                y = sqrt(np.sum(filtered_vj**2))

                if x > 0 and y > 0 and count >= 6:
                    x_dot_y = np.sum(filtered_vi*filtered_vj)
                    similarity = x_dot_y / (x * y)
                    self._similarities_matrix[i, j] = similarity
                    self._similarities_matrix[j, i] = similarity

    def predict(self, user, book):
        """
        Просто считаем средневзвешенную оценку на основании
        матрицы похожетстей книг
        """
        user_index = self._users_dict[user]
        book_index = self._books_dict[book]

        predicted_mark = 0.0
        total_weights = 0.0
        for b in range(len(self._books_dict)):
            if self._matrix[user_index, b] > 0 and self._similarities_matrix[book_index, b] > self.MINIMUM_SIMILARITY:
                predicted_mark += self._matrix[user_index, b] * self._similarities_matrix[book_index, b]
                total_weights += self._similarities_matrix[book_index, b]

        if total_weights > 0:
            predicted_mark /= total_weights

        return predicted_mark


class ItemToItemCollaborativePiersonPredictor(BasePredictor):
    """
    Реализует алгоритм колаборативной фильтрации на основе
    схожести книг, использует корреляцию Пирсона
    """

    # Минимальныцй уровень похожести для учета при прогнозировании
    MINIMUM_SIMILARITY = 0.0

    def __init__(self, matrix, users_dict, books_dict):
        """
        Конструктор, сразу рассчитывает схожесть книг
        """
        super(ItemToItemCollaborativePiersonPredictor, self).__init__(matrix, users_dict, books_dict)

        self._similarities_matrix = np.zeros([len(self._books_dict), len(self._books_dict)])
        self._average_marks = np.zeros([len(self._users_dict)])

        presence_matrix = np.where(self._matrix > 0, 1.0, 0)
        counts = np.sum(presence_matrix, axis=1)
        self._average_marks = np.nan_to_num(np.sum(self._matrix, axis=1) / counts)

        for i in range(len(self._books_dict)):
            for j in range(i + 1, len(self._books_dict)):
                vi = self._matrix[:, i]
                vj = self._matrix[:, j]

                filtered_vi = np.where(vj > 0, vi, 0)
                filtered_vj = np.where(vi > 0, vj, 0)

                count = np.sum(np.where(filtered_vi * filtered_vj > 0, 1, 0))

                filtered_vi -= self._average_marks
                filtered_vj -= self._average_marks

                x = sqrt(np.sum(filtered_vi**2))
                y = sqrt(np.sum(filtered_vj**2))

                if x > 0 and y > 0 and count >= 6:
                    x_dot_y = np.sum(filtered_vi*filtered_vj)
                    similarity = x_dot_y / (x * y)
                    self._similarities_matrix[i, j] = similarity
                    self._similarities_matrix[j, i] = similarity

    def predict(self, user, book):
        """
        Просто считаем средневзвешенную оценку на основании
        матрицы похожестей книг
        """
        user_index = self._users_dict[user]
        book_index = self._books_dict[book]

        predicted_mark = 0.0
        total_weights = 0.0
        for b in range(len(self._books_dict)):
            if self._matrix[user_index, b] > 0 and self._similarities_matrix[book_index, b] > self.MINIMUM_SIMILARITY:
                predicted_mark += self._matrix[user_index, b] * self._similarities_matrix[book_index, b]
                total_weights += self._similarities_matrix[book_index, b]

        if total_weights > 0:
            predicted_mark /= total_weights
        else:
            predicted_mark = 0

        return predicted_mark

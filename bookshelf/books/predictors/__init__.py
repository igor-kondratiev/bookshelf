# coding=utf-8
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
        users_count = self._matrix.shape[0]
        books_count = self._matrix.shape[1]
        for book in range(books_count):
            self._book_marks[book] = 0

            count = 0
            for user in range(users_count):
                if self._matrix[user, book] > 0:
                    self._book_marks[book] += self._matrix[user, book]
                    count += 1

            if count > 0:
                self._book_marks[book] /= count

    def predict(self, user, book):
        """
        Просто возвращаем предпросчитанную среднюю оценку
        """
        return self._book_marks[self._books_dict[book]]

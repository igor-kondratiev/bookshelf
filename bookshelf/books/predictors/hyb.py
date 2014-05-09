from math import sqrt
from django.contrib.auth.models import User

from books.models import BookMark
from books.predictors.cos import CosineSimilarityPredictor


class LocalSimilarityPredictor(object):
    def __init__(self, user):
        super(LocalSimilarityPredictor, self).__init__()
        self.user = user
        self.users = list(User.objects.exclude(pk=self.user.pk))
        self.cos_predictor = CosineSimilarityPredictor(self.user)

    def predict(self, book):
        predicted_mark = 0.0
        total_weight = 0.0

        similar_books = book.get_similar_books()
        for user in self.users:
            x = 0.0
            y = 0.0
            xy = 0.0

            for mark in BookMark.objects.filter(user=user, book__in=similar_books):
                try:
                    own_mark = BookMark.objects.get(user=self.user, book=mark.book)
                except:
                    continue

                x += mark.mark * mark.mark
                y += own_mark.mark * own_mark.mark
                xy += mark.mark * own_mark.mark

            if x > 0 and y > 0:
                x = sqrt(x)
                y = sqrt(y)
                cos = xy / (x*y)

                try:
                    his_mark = BookMark.objects.get(user=user, book=book)
                    predicted_mark += his_mark.mark * cos
                    total_weight += cos
                except:
                    pass

        if total_weight > 0:
            predicted_mark /= total_weight

        if predicted_mark == 0:
            predicted_mark = self.cos_predictor.predict(book)

        return predicted_mark


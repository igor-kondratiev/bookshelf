from math import sqrt
from django.contrib.auth.models import User
from django.db.models import Avg

from books.models import BookMark
from books.predictors.cos import CosineSimilarityPredictor
from books.predictors.item import CosineItemSimilarityPredictor


class LocalSimilarityPredictor(object):
    def __init__(self, user):
        super(LocalSimilarityPredictor, self).__init__()
        self.user = user
        self.avg_mark = BookMark.objects.filter(user=self.user).aggregate(Avg('mark'))['mark__avg']
        self.users = list(User.objects.exclude(pk=self.user.pk))
        self.cos_predictor = CosineSimilarityPredictor(self.user)

    def predict(self, book):
        predicted_mark = 0.0
        total_weight = 0.0

        similar_books = book.get_similar_books()
        for user in self.users:
            users_avg_mark = BookMark.objects.filter(user=user).aggregate(Avg('mark'))['mark__avg']

            x = 0.0
            y = 0.0
            xy = 0.0

            for mark in BookMark.objects.filter(user=user, book__in=similar_books):
                try:
                    own_mark = BookMark.objects.get(user=self.user, book=mark.book)
                except:
                    continue

                x += (mark.mark - users_avg_mark) * (mark.mark - users_avg_mark)
                y += (own_mark.mark - self.avg_mark) * (own_mark.mark - self.avg_mark)
                xy += (mark.mark - users_avg_mark) * (own_mark.mark - self.avg_mark)

            if x > 0 and y > 0:
                x = sqrt(x)
                y = sqrt(y)
                cos = xy / (x*y)

                try:
                    his_mark = BookMark.objects.get(user=user, book=book)
                    predicted_mark += (his_mark.mark - users_avg_mark) * cos
                    total_weight += cos
                except:
                    pass

        if total_weight != 0:
            predicted_mark /= total_weight
            predicted_mark += self.avg_mark
        else:
            predicted_mark = self.cos_predictor.predict(book)

        return predicted_mark


class HybCosItemPredictor(object):

    K_COS = 0.5
    K_ITEM = 0.5

    def __init__(self, user):
        super(HybCosItemPredictor, self).__init__()
        self.user = user
        self.cos_predictor = CosineSimilarityPredictor(self.user)
        self.item_predictor = CosineItemSimilarityPredictor(self.user)

    def predict(self, book):
        return self.K_COS * self.cos_predictor.predict(book) + self.K_ITEM * self.item_predictor.predict(book)

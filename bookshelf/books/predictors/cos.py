from math import sqrt
from django.contrib.auth.models import User
from django.db.models import Avg

from books.models import BookMark


class CosineSimilarityPredictor(object):
    def __init__(self, user):
        super(CosineSimilarityPredictor, self).__init__()
        self.user = user
        self.similarities = {}
        self.marks = BookMark.objects.filter(user=user)
        self.avg_mark = BookMark.objects.filter(user=user).aggregate(Avg('mark'))['mark__avg']

        users = User.objects.exclude(pk=self.user.pk)
        for u in users:
            u_avg_mark = BookMark.objects.filter(user=u).aggregate(Avg('mark'))['mark__avg']
            x = 0.0
            y = 0.0
            xy = 0.0
            marks = BookMark.objects.filter(user=u)
            for mark in marks:
                try:
                    own_mark = self.marks.get(book=mark.book)
                except:
                    continue
                x += (mark.mark - u_avg_mark) * (mark.mark - u_avg_mark)
                y += (own_mark.mark - self.avg_mark) * (own_mark.mark - self.avg_mark)
                xy += (mark.mark - u_avg_mark) * (own_mark.mark - self.avg_mark)

            cosine = 0
            if x > 0 and y > 0:
                x = sqrt(x)
                y = sqrt(y)
                cosine = xy / (x*y)

            self.similarities[u] = cosine

    def predict(self, book):
        marks = BookMark.objects.filter(book=book).exclude(user=self.user)
        predicted_mark = 0.0
        total_weight = 0.0
        for mark in marks:
            users_avg_mark = BookMark.objects.filter(user=mark.user).aggregate(Avg('mark'))['mark__avg']
            cos = max(self.similarities[mark.user], 0)
            predicted_mark += cos * (mark.mark - users_avg_mark)
            total_weight += cos

        if total_weight != 0:
            predicted_mark /= total_weight

        predicted_mark += self.avg_mark

        return predicted_mark

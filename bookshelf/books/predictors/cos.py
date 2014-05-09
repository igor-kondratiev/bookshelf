from math import sqrt
from django.contrib.auth.models import User

from books.models import BookMark


class CosineSimilarityPredictor(object):
    def __init__(self, user):
        super(CosineSimilarityPredictor, self).__init__()
        self.user = user
        self.similarities = {}
        self.marks = BookMark.objects.filter(user=user)

        users = User.objects.exclude(pk=self.user.pk)
        for u in users:
            x = 0.0
            y = 0.0
            xy = 0.0
            marks = BookMark.objects.filter(user=u)
            for mark in marks:
                try:
                    own_mark = self.marks.get(book=mark.book)
                except:
                    continue
                x += mark.mark * mark.mark
                y += own_mark.mark * own_mark.mark
                xy += mark.mark * own_mark.mark

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
            predicted_mark += self.similarities[mark.user] * mark.mark
            total_weight += self.similarities[mark.user]

        if total_weight > 0:
            predicted_mark /= total_weight

        return predicted_mark

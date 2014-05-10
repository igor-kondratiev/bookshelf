from django.db.models import Avg, Q

from books.models import BookMark, BookDistance


class CosineItemSimilarityPredictor(object):
    def __init__(self, user):
        super(CosineItemSimilarityPredictor, self).__init__()
        self.user = user

    def predict(self, book):
        marks = BookMark.objects.filter(user=self.user).exclude(book=book)
        avg_mark = marks.aggregate(Avg('mark'))['mark__avg']
        marks = list(marks)
        predicted_mark = 0.0
        total_weight = 0.0
        distances_list = list(BookDistance.objects.filter(Q(first_book=book) | Q(second_book=book)))
        distances = {}
        for dist in distances_list:
            if dist.first_book == book:
                distances[dist.second_book] = dist.distance
            else:
                distances[dist.first_book] = dist.distance

        for mark in marks:
            cos = max(distances.get(mark.book, 0), 0)
            predicted_mark += cos * (mark.mark - avg_mark)
            total_weight += cos

        if total_weight != 0:
            predicted_mark /= total_weight

        predicted_mark += avg_mark

        return predicted_mark


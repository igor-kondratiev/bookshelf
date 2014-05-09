# coding=utf-8
from math import sqrt

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.models import Sum, Q

from books.models import Book, BookDistance, BookMark


class Command(BaseCommand):

    USERNAME = 'e_reading'

    def __init__(self):
        super(Command, self).__init__()
        self.user = User.objects.get(username=self.USERNAME)

    def handle(self, *args, **options):
        marks = BookMark.objects.filter(user=self.user)
        marks_count = marks.count()
        marks_sum = marks.aggregate(Sum('mark'))['mark__sum']

        mse = 0.0
        for mark in marks:
            real_mark = mark.mark

            similar_books = mark.book.get_similar_books()
            predicted_mark = 0.0
            weights_sum = 0.0
            for book in similar_books:
                distance = BookDistance.objects.get(
                    Q(first_book=book, second_book=mark.book) | Q(first_book=mark.book, second_book=book)
                )
                try:
                    dmark = book.bookmark_set.get(user=self.user).mark
                    predicted_mark += distance.distance * dmark
                    weights_sum += distance.distance
                except:
                    pass

            if predicted_mark > 0:
                predicted_mark /= weights_sum
                mse += (real_mark - predicted_mark) * (real_mark - predicted_mark)
            else:
                real_mark = mark.mark
                predicted_mark = (marks_sum - real_mark) / (marks_count - 1)
                mse += (real_mark - predicted_mark) * (real_mark - predicted_mark)

        mse /= marks_count
        rmse = sqrt(mse)
        print 'RMSE for similar_books user mark prediction = {0}'.format(rmse)


# coding=utf-8
from math import sqrt

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from books.models import BookMark
from books.predictors.hyb import LocalSimilarityPredictor


class Command(BaseCommand):

    USERNAME = 'imho'

    def __init__(self):
        super(Command, self).__init__()
        self.user = User.objects.get(username=self.USERNAME)

    def handle(self, *args, **options):
        marks = list(BookMark.objects.filter(user=self.user))
        mse = 0.0
        count = 0
        predictor = LocalSimilarityPredictor(self.user)
        for mark in marks:
            real_mark = mark.mark
            predicted_mark = predictor.predict(mark.book)
            if predicted_mark > 0:
                mse += (real_mark - predicted_mark) * (real_mark - predicted_mark)
                count += 1

        mse /= count
        rmse = sqrt(mse)

        print 'RMSE for LocalSimilarityPredictor = {0}'.format(rmse)

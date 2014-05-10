# coding=utf-8
from math import sqrt
from optparse import make_option

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from books.models import BookMark
from books.predictors.cos import CosineSimilarityPredictor


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option(
            '--user',
            dest='username',
            default='e_reading',
        ),
    )

    def __init__(self):
        super(Command, self).__init__()

    def handle(self, *args, **options):
        user = User.objects.get(username=options['username'])
        marks = list(BookMark.objects.filter(user=user))
        mse = 0.0
        count = 0
        predictor = CosineSimilarityPredictor(user)
        for mark in marks:
            real_mark = mark.mark
            predicted_mark = predictor.predict(mark.book)
            if predicted_mark > 0:
                mse += (real_mark - predicted_mark) * (real_mark - predicted_mark)
                count += 1

        mse /= count
        rmse = sqrt(mse)

        print 'RMSE for CosineSimilarityPredictor = {0}'.format(rmse)

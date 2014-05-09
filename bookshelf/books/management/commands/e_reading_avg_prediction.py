# coding=utf-8
from math import sqrt

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.models import Sum

from books.models import BookMark


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
            predicted_mark = (marks_sum - real_mark) / (marks_count - 1)
            mse += (real_mark - predicted_mark) * (real_mark - predicted_mark)

        mse /= marks_count
        rmse = sqrt(mse)
        print 'RMSE for average user  mark prediction = {0}'.format(rmse)

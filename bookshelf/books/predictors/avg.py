from books.models import BookMark
from django.db.models import Avg


class AveragePredictor(object):

    def __init__(self):
        super(AveragePredictor, self).__init__()

    def predict(self, book, user):
        return BookMark.objects.filter(book=book).exclude(user=user).aggregate(Avg('mark'))['mark__avg']

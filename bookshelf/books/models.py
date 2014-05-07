# coding=utf-8
from django.db import models
from django.db.models import Q


class Author(models.Model):
    name = models.CharField(max_length=64)

    @classmethod
    def get_or_create_author(cls, name):
        try:
            author = cls.objects.get(name=name)
        except cls.DoesNotExist:
            author = Author(name=name)
            author.save()

        return author

    def __unicode__(self):
        return unicode(self.name)


class BookGenre(models.Model):
    name = models.CharField(max_length=64)

    @classmethod
    def get_or_create_genre(cls, name):
        try:
            genre = cls.objects.get(name=name)
        except cls.DoesNotExist:
            genre = BookGenre(name=name)
            genre.save()

        return genre

    def __unicode__(self):
        return unicode(self.name)


class Book(models.Model):
    author = models.ForeignKey(Author)
    caption = models.CharField(max_length=128)
    genres = models.ManyToManyField(BookGenre)
    text_file = models.CharField(max_length=64, blank=True)

    # Тут храним данные о том, какой скрейпер притащил книжку, и ее идентификатор
    source = models.CharField(max_length=64, blank=True, null=True)
    remote_id = models.CharField(max_length=128, blank=True, null=True)

    # Кластер, в который попала книжка
    cluster_id = models.IntegerField(null=True, default=None)

    def get_similar_books(self, limit=None):
        distances = BookDistance.objects.filter(Q(first_book=self) | Q(second_book=self)).filter(distance__gte=0.4).order_by('-distance')
        if limit:
            distances = distances[:limit]

        # Так как книжек будет скорее всего немного, то
        # пожертвуем памятью во благо скорости
        distances = list(distances)

        books = []
        for dist in distances:
            books.append(dist.first_book if dist.second_book == self else dist.second_book)

        return books

    def __unicode__(self):
        return u'{0}. {1}'.format(self.author, self.caption)


class BookDistance(models.Model):
    first_book = models.ForeignKey(Book, related_name='first_book')
    second_book = models.ForeignKey(Book, related_name='second_book')
    distance = models.FloatField()

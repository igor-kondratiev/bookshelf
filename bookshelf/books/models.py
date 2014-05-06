# coding=utf-8
from django.db import models


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

    def get_similar_books(self, count):
        result = list(BookDistance.objects.filter(first_book=self).order_by('distance')[:count])
        result.extend(list(BookDistance.objects.filter(second_book=self).order_by('distance')[:count]))
        result.sort(key=lambda x: x.distance)
        result = result[:count]

        books = []
        for distance in result:
            if distance.first_book == self:
                books.append(distance.second_book)
            else:
                books.append(distance.first_book)

        return books


    def __unicode__(self):
        return u'{0}. {1}'.format(self.author, self.caption)


class BookDistance(models.Model):
    first_book = models.ForeignKey(Book, related_name='first_book')
    second_book = models.ForeignKey(Book, related_name='second_book')
    distance = models.FloatField()

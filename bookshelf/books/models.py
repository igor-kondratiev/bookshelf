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

    def __unicode__(self):
        return u'{0}. {1}'.format(self.author, self.caption)
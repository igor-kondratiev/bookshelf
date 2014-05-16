# coding=utf-8
from django.conf import settings
from django.db.models import Count

from books.models import Book, BookGenre, Author


def settings_processor(request):
    """
    Добавляет настройки в контекст
    """
    return {'settings': settings}


def genres_processor(request):
    """
    Добавляет в контекст список жанров с количеством книг
    """
    genres_list = BookGenre.objects.annotate(books_count=Count('book')) \
                           .exclude(books_count=0) \
                           .order_by('-books_count')
    genres_count = genres_list.count()
    genres_list = genres_list[:20]
    return {
        'genres_list': genres_list,
        'genres_count': genres_count,
    }


def authors_processor(request):
    """
    Добавляет в контекст список авторов с количеством книг
    """
    authors_list = Author.objects.annotate(books_count=Count('book')) \
                         .exclude(books_count=0) \
                         .order_by('-books_count')
    authors_count = authors_list.count()
    authors_list = authors_list[:20]
    return {
        'authors_list': authors_list,
        'authors_count': authors_count,
    }


def random_book_processor(request):
    """
    Добавляет в контекст 2 рандомные книжки
    """
    random_books = Book.objects.order_by('?')[:2]
    return {'random_books': random_books}

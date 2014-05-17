from django.db.models import Avg, Count
from django.http import HttpResponse
from django.shortcuts import render

from books.models import Book


def home_view(request):
    popular_books = Book.objects.annotate(mark=Avg('bookmark')).order_by('-mark')[:12]
    readable_books = Book.objects.annotate(marks_count=Count('bookmark')).order_by('-marks_count')[:6]
    return render(request, 'index.html', {
        'popular_books': popular_books,
        'readable_books': readable_books,
    })


def book_view(request, book_id):
    return HttpResponse()


def authors_books_view(request, author_id):
    return HttpResponse()

from django.contrib import admin

from books.models import Book, BookGenre, Author


admin.site.register(Author)
admin.site.register(BookGenre)
admin.site.register(Book)

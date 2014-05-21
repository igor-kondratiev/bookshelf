# coding=utf-8
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Avg, Count
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect

from books.forms import RegistrationForm
from books.models import Author, Book, BookGenre, BookMark


def home_view(request):
    popular_books = Book.objects.annotate(mark=Avg('bookmark__mark')).exclude(mark=None).order_by('-mark')[:12]
    readable_books = Book.objects.annotate(marks_count=Count('bookmark')).order_by('-marks_count')[:6]
    return render(request, 'index.html', {
        'popular_books': popular_books,
        'readable_books': readable_books,
    })


def book_view(request, book_id):
    try:
        book = Book.objects.get(pk=book_id)
    except:
        raise Http404()

    related_books = book.get_similar_books(6)
    book_mark = str(BookMark.objects.filter(book=book).aggregate(Avg('mark'))['mark__avg'])[:4]

    users_mark = None
    if request.user and request.user.is_authenticated():
        try:
            users_mark = str(BookMark.objects.get(book=book, user=request.user).mark)
        except:
            pass

    return render(request, 'book_details.html', {
        'book': book,
        'related_books': related_books,
        'book_mark': book_mark,
        'users_mark': users_mark,
    })


def authors_books_view(request, author_id):
    try:
        author = Author.objects.get(pk=author_id)
    except:
        raise Http404()

    books_list = author.book_set.all()
    return render(request, 'books_list.html', {
        'books_list': books_list,
        'title': 'Книги автора {0}'.format(author.name.encode('utf-8'))
    })


def books_by_genre_view(request, genre_id):
    try:
        genre = BookGenre.objects.get(pk=genre_id)
    except:
        raise Http404()

    books_list = genre.book_set.all()
    return render(request, 'books_list.html', {
        'books_list': books_list,
        'title': '{0}'.format(genre.name.encode('utf-8'))
    })


def popular_books_view(request):
    books_list = Book.objects.annotate(mark=Avg('bookmark__mark')).exclude(mark=None).order_by('-mark')[:20]
    return render(request, 'books_list.html', {
        'books_list': books_list,
        'title': 'Популярні книги'
    })


def readable_books_view(request):
    books_list = Book.objects.annotate(marks_count=Count('bookmark')).order_by('-marks_count')[:20]
    return render(request, 'books_list.html', {
        'books_list': books_list,
        'title': 'Найбільше переглядів'
    })


def recommended_books_view(request):
    return HttpResponse()


def genres_list_view(request):
    genres_list = BookGenre.objects.annotate(books_count=Count('book')) \
                           .exclude(books_count=0) \
                           .order_by('-books_count')

    return render(request, 'genres_list.html', {'genres_list': genres_list})


def authors_list_view(request):
    authors_list = Author.objects.annotate(books_count=Count('book')) \
                         .exclude(books_count=0) \
                         .order_by('-books_count')

    return render(request, 'authors_list.html', {'authors_list': authors_list})


def login_view(request):
    if request.method != "POST":
        return redirect(reverse('home'))

    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = authenticate(username=username, password=password)
    if user is not None and user.is_active:
        login(request, user)

    return redirect(reverse('home'))


def logout_view(request):
    logout(request)
    return redirect(reverse('home'))


def registration_view(request):

    # TODO: исправить отображение ошибок валидации

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            User.objects.create_user(username, email, password)
            auth_user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            login(request, auth_user)

            return redirect(reverse('home'))
    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})


@login_required
def vote_book(request):
    source = request.GET.get('from', reverse('home'))

    book_id = request.GET.get('book_id')
    if book_id:
        print 'Here1'
        mark = request.GET.get('mark')
        if mark and 0 < int(mark) <= 10:
            print 'Here2'
            try:
                book = Book.objects.get(pk=book_id)
                db_mark = BookMark(user=request.user, book=book, mark=mark)
                db_mark.save()
                print 'done'
            except Exception as e:
                print str(e)

    return redirect(source)

# coding=utf-8
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Avg, Count
from django.http import HttpResponse
from django.shortcuts import render, redirect

from books.forms import RegistrationForm
from books.models import Book


def home_view(request):
    popular_books = Book.objects.annotate(mark=Avg('bookmark__mark')).exclude(mark=None).order_by('-mark')[:12]
    readable_books = Book.objects.annotate(marks_count=Count('bookmark')).order_by('-marks_count')[:6]
    return render(request, 'index.html', {
        'popular_books': popular_books,
        'readable_books': readable_books,
    })


def book_view(request, book_id):
    return HttpResponse()


def authors_books_view(request, author_id):
    return HttpResponse()


def books_by_genre_view(request, genre_id):
    return HttpResponse()


def popular_books_view(request):
    return HttpResponse()


def readable_books_view(request):
    return HttpResponse()


def recommended_books_view(request):
    return HttpResponse()


def genres_list_view(request):
    return HttpResponse()


def authors_list_view(request):
    return HttpResponse()


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

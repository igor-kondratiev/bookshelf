from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^$', 'books.views.home_view', name='home'),
    url(r'^login/$', 'books.views.login_view', name='login'),
    url(r'^logout/$', 'books.views.logout_view', name='logout'),
    url(r'^registration/$', 'books.views.registration_view', name='registration'),
    url(r'^books/popular/$', 'books.views.popular_books_view', name='popular_books'),
    url(r'^books/readable/$', 'books.views.readable_books_view', name='readable_books'),
    url(r'^books/recommended/$', 'books.views.recommended_books_view', name='recommended_books'),
    url(r'^books/vote/$', 'books.views.vote_book', name='vote_book'),
    url(r'^books/(?P<book_id>\d+)/$', 'books.views.book_view', name='book'),
    url(r'^authors/$', 'books.views.authors_list_view', name='authors_list'),
    url(r'^authors/(?P<author_id>\d+)/$', 'books.views.authors_books_view', name='author'),
    url(r'^genres/$', 'books.views.genres_list_view', name='genres_list'),
    url(r'^genres/(?P<genre_id>\d+)/$', 'books.views.books_by_genre_view', name='genre'),
)

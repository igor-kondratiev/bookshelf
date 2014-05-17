from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^$', 'books.views.home_view', name='home'),
    url(r'^login/$', 'books.views.login_view', name='login'),
    url(r'^logout/$', 'books.views.logout_view', name='logout'),
    url(r'^books/(?P<book_id>\d+)/$', 'books.views.book_view', name='book'),
    url(r'^authors/(?P<author_id>\d+)/$', 'books.views.authors_books_view', name='author'),
)

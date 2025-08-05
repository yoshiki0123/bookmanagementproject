from django.urls import path

from .views import login_view, signup_view, home_view, borrow_book, return_book, logout_view

app_name = 'bookmanagement'

urlpatterns = [
    path("login/", login_view, name="login"),
    path("signup/", signup_view, name="signup"),
    path("home/", home_view, name="home"),
    path('borrow/', borrow_book, name='borrow'),
    path("return/", return_book, name="return"),
    path("logout/", logout_view, name='logout'),
]
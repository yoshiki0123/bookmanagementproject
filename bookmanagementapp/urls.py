from django.urls import path

from .views import login_view, signup_view, home_view, borrow_book, return_book, logout_view, book_list, add_book, loan_status_list

app_name = 'bookmanagement'

urlpatterns = [
    path("login/", login_view, name="login"),
    path("signup/", signup_view, name="signup"),
    path("home/", home_view, name="home"),
    path('borrow/', borrow_book, name='borrow'),
    path("return/", return_book, name="return"),
    path('', book_list, name='book_list'),  # 書籍一覧
    path('add_book/', add_book, name='add_book'),  # 書籍登録
    path('loan_status/', loan_status_list, name='loan_status'),  # 貸出状況
    path("logout/", logout_view, name='logout'),
]
from django.urls import path
from .views import book_list, add_book, loan_status_list

app_name = 'bookcatalog'

urlpatterns = [
    path('', book_list, name='book_list'),  # 書籍一覧
    path('add_book/', add_book, name='add_book'),  # 書籍登録
    path('loan_status/', loan_status_list, name='loan_status'),  # 貸出状況
]

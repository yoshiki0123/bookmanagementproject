from django.shortcuts import render, redirect
from django.http import HttpResponse
from bookmanagementapp.models import BookModel, LoanModel
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.db.utils import IntegrityError

def book_list(request):
    query = request.GET.get("q", "") # 検索クエリ
    page  = request.GET.get("page", 1) # ページ番号

    # DBに登録されている書籍を取得
    books = BookModel.objects.all().order_by('isbn')

    # 検索クエリがあればタイトルにフィルタを適用
    if query:
        books = books.filter(title__icontains=query.strip())

    # ページネーション処理
    paginator = Paginator(books, 15)  # 1ページ15件
    try:
        books_page = paginator.get_page(page)  
    except (PageNotAnInteger, EmptyPage):
        books_page = paginator.get_page(1)

    return render(request, 'bookcatalogapp/book_list.html', {
        'books_page': books_page,  
        'q': query,
    })

def add_book(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        isbn = request.POST.get('isbn')

        # BookModelテーブルに書籍があるか確認
        if not BookModel.objects.filter(isbn=isbn).exists():
            # 書籍がない場合は登録処理を実施
            try:
                # BookModelテーブルにレコードを作成
                BookModel.objects.create(title=title, author=author, isbn=isbn)
                messages.success(request, f"「{title}」の登録を完了しました。")
                return redirect('bookcatalog:add_book')
            except IntegrityError:
                # レコード作成に失敗した場合はメッセージを表示
                messages.warning(request, f"「{title}」登録に失敗しました。")
        else:
            #　書籍がある場合はメッセージを表示
            messages.info(request, f"「{title}」は既に登録済みです。")
            return redirect('bookcatalog:add_book')
            
        # エラー時のみ値を保持して再表示
        return render(request, 'bookcatalogapp/add_book.html', {
            'title': title, 'author': author, 'isbn': isbn
        })

    return render(request, 'bookcatalogapp/add_book.html')

def loan_status_list(request):
    # 貸出状況の一覧を取得
    loans = LoanModel.objects.filter(returned_date__isnull=True)
    return render(request, 'bookcatalogapp/loan_status.html', {'loans': loans})

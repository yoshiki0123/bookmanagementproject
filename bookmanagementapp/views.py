from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import BookModel, LoanModel
from django.db.models import Q,Count
from django.contrib import messages
from django.urls import reverse
from django.db import transaction
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.http import urlencode
import json

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username'] 
        password = request.POST['password']
        user = authenticate(request, username=username, password=password) # ユーザーの権限確認
        
        # 
        if user is not None:
            login(request, user) # login処理
            return redirect('bookmanagement:home')
        else:
            return render(request, 'bookmanagementapp/login.html', {'error':'入力が間違っています。\nもう一度入力してください。'})

    return render(request, 'bookmanagementapp/login.html', {})

@login_required
def logout_view(request):
    logout(request) # logout処理
    return redirect('bookmanagement:login')

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        try:
            # ユーザー登録
            user = User.objects.create_user(username, '', password)
            return redirect('bookmanagement:login')
        except IntegrityError:
            return render(request, 'bookmanagementapp/signup.html', {'error':'このユーザーは既に登録されています'})
    return render(request, 'bookmanagementapp/signup.html', {})

@login_required
def home_view(request):
    query = request.GET.get("q", "") # 検索クエリ
    page  = request.GET.get("page", 1) # page番号

    # ログインユーザーの貸出履歴を取得
    loan_records = (
        LoanModel.objects
        .filter(user=request.user)
        .order_by('returned_date', 'book__isbn')
    )

    # 検索クエリがあればタイトルにフィルタを適用
    if query:
        loan_records = loan_records.filter(book__title__icontains=query.strip())

    # ページネーション処理
    paginator = Paginator(loan_records, 15)  # 1ページ15件
    try:
        loan_records_page = paginator.get_page(page)  
    except (PageNotAnInteger, EmptyPage):
        loan_records_page = paginator.get_page(1)

    return render(request, 'bookmanagementapp/home.html', {
        'loan_records_page': loan_records_page,  
        'q': query,
    })

@login_required
def borrow_book(request):
    # --- POSTメソッドの処理 ---
    if request.method == 'POST':
        query = request.GET.get('q', '') # 検索クエリ

        # 選択された書籍のISBNを取得(json形式)
        selected_isbns = request.POST.getlist("selected_isbns")
        selected_isbns = list(set(selected_isbns)) # 重複処理
        selected_isbns = json.loads(selected_isbns[0]) # json処理
        
        # 書籍が選択されずに借りるが押された場合
        if not selected_isbns:
            messages.info(request, '書籍が選択されていません。')
            url = reverse('bookmanagement:borrow')
            return redirect(url + (f'?{urlencode({"q": query})}' if query else ''))

        borrowed = [] # 貸出成功した書籍タイトルのリスト
        skipped = [] # 貸出できなかった書籍タイトルのリスト

        # ISBNごとに貸出処理を実行
        for isbn in selected_isbns:
            book = BookModel.objects.get(isbn=isbn)

            # すでに貸出中の場合はスキップ
            if book.on_loan:
                skipped.append(book.title)
                continue

            # 貸出処理
            try:
                # 失敗時はこのブロックだけロールバック
                with transaction.atomic():
                    LoanModel.objects.create(book=book, user=request.user)
                borrowed.append(book.title)

            except IntegrityError:
                # 登録に失敗した場合もスキップ扱いに
                skipped.append(book.title)

        # 貸出に成功した書籍のメッセージ
        if borrowed:
            messages.success(request, f"「{'、'.join(borrowed)}」の貸出を完了しました。")
        # 貸出に失敗した書籍のメッセージ
        if skipped:
            messages.warning(request, f"「{'、'.join(skipped)}」は既に貸出中です。")

        # PRG：再送信防止＆検索クエリを保持したままリダイレクト
        url = reverse('bookmanagement:borrow')
        return redirect(url + (f'?{urlencode({"q": query})}' if query else ''))

    # --- GETメソッドの処理 ---
    query = request.GET.get("q", "") # 検索クエリ
    page  = request.GET.get("page", 1) # ページ番号

    # 貸出可能な書籍（現在貸出されていないもの）を取得
    can_borrow_books = (
        BookModel.objects
        .annotate(
            active_loans=Count(
                'loans',
                filter=Q(loans__returned_date__isnull=True)  # 未返却の貸出のみカウント
            )
        )
        .filter(active_loans=0) # 未返却の貸出が0冊 → 貸出可能
        .order_by('isbn')
    )

    # 検索クエリがあればタイトルにフィルタを適用
    if query:
        can_borrow_books = can_borrow_books.filter(title__icontains=query.strip())

    # ページネーション処理
    paginator = Paginator(can_borrow_books, 15)  # 1ページ15件
    try:
        can_borrow_books_page = paginator.get_page(page)  
    except (PageNotAnInteger, EmptyPage):
        can_borrow_books_page = paginator.get_page(1)

    return render(request, 'bookmanagementapp/borrow.html', {
        'can_borrow_books_page': can_borrow_books_page,  
        'q': query,
    })

@login_required
def return_book(request):
    # --- POSTメソッドの処理 ---
    if request.method == 'POST':
        query = request.GET.get('q', '') # 検索クエリ
        now = timezone.now() # 現在時刻(TIME_ZONE = 'Asia/Tokyo')

        # 選択された書籍のISBNを取得(json形式)
        selected_isbns = request.POST.getlist("selected_isbns")
        selected_isbns = list(set(selected_isbns)) # 重複処理
        selected_isbns = json.loads(selected_isbns[0]) # json処理

        # 書籍が選択されずに返却が押された場合
        if not selected_isbns:
            messages.info(request, '書籍が選択されていません。')
            url = reverse('bookmanagement:return')
            return redirect(url + (f'?{urlencode({"q": query})}' if query else ''))

        # 返却処理
        updated = LoanModel.objects.filter(
            book__isbn__in=selected_isbns, 
            user=request.user,
            returned_date__isnull=True
        ).update(returned_date=now)
        
        if updated:
            messages.success(request, f"{updated}件を返却しました。")
        else:
            messages.info(request, "返却対象が見つかりませんでした。")

        # PRG：再送信防止＆検索クエリを保持したままリダイレクト
        url = reverse('bookmanagement:return')
        return redirect(url + (f'?{urlencode({"q": query})}' if query else ''))
    
    # --- GETメソッドの処理 ---
    query = request.GET.get("q", "") # 検索クエリ
    page  = request.GET.get("page", 1) # ページ番号

    # 返却可能な書籍（現在貸りているもの）を取得
    can_return_books = (
        LoanModel.objects
        .filter(user=request.user, returned_date__isnull=True)
        .order_by('borrowed_date', 'book__isbn')
    )

    # 検索クエリがあればタイトルにフィルタを適用
    if query:
        can_return_books = can_return_books.filter(book__title__icontains=query.strip())

    # ページネーション処理
    paginator = Paginator(can_return_books, 15)  # 1ページ20件
    try:
        can_return_books_page = paginator.get_page(page)  
    except (PageNotAnInteger, EmptyPage):
        can_return_books_page = paginator.get_page(1)

    return render(request, 'bookmanagementapp/return.html', {
        'can_return_books_page': can_return_books_page,  
        'q': query,
    })

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

    return render(request, 'bookmanagementapp/book_list.html', {
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
                return redirect('bookmanagement:add_book')
            except IntegrityError:
                # レコード作成に失敗した場合はメッセージを表示
                messages.warning(request, f"「{title}」登録に失敗しました。")
        else:
            #　書籍がある場合はメッセージを表示
            messages.info(request, f"「{title}」は既に登録済みです。")
            return redirect('bookmanagement:add_book')
            
        # エラー時のみ値を保持して再表示
        return render(request, 'bookmanagementapp/add_book.html', {
            'title': title, 'author': author, 'isbn': isbn
        })

    return render(request, 'bookmanagementapp/add_book.html')

def loan_status_list(request):
    # 貸出状況の一覧を取得
    loans = LoanModel.objects.filter(returned_date__isnull=True)
    return render(request, 'bookmanagementapp/loan_status.html', {'loans': loans})

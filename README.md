# bookmanagementproject - 書籍管理ウェブアプリ
## 概要
このウェブアプリは、ユーザー認証機能を搭載した書籍管理ウェブアプリです。ユーザーは個別にログインし、書籍の貸出、返却、登録などができます。また貸出や返却などの処理には検索機能があり、特定の書籍を素早く見つけることができます。データベースは SQLiteを使用しています。
## 主な機能
## 主な機能
- **ユーザー認証機能**（ログイン／ログアウト／ユーザー登録）
- **書籍登録**（タイトル・著者・ISBNなどの情報を追加）
- **書籍一覧**（登録された書籍を一覧表示）
- **書籍貸出**（login中のユーザーを指定して書籍を貸出登録）
- **書籍返却**（貸出中の書籍を返却処理）
- **貸出状況管理**（誰がどの本を借りているかを一覧表示）
- **ログアウト**（セッションを終了してログイン画面へ戻る）

## 使用環境のセットアップ
### 前提条件
- Python 3.12+ がインストールされていること。
- 仮想環境を推奨します。(今回はvenvを使用)
### インストール手順
1. このリポジトリをクローンします:
    ```bash
    git clone https://github.com/yoshiki0123/diary_webapp.git
    ```

2. プロジェクトディレクトリに移動します:
    ```bash
    cd diary_webapp
    ```

3. Condaを使用して仮想環境を作成します:
    ```bash
    conda create --name diary_env python=3.8
    ```

4. 仮想環境をアクティブ化します:
    ```bash
    conda activate diary_env
    ```
5. 必要なパッケージをインストールします:
    ```bash
    pip install -r requirements.txt
    ```
6. `SECRET_KEY` を生成します:

    Djangoの `get_random_secret_key` を使ってランダムな `SECRET_KEY` を生成します。

    1. Djangoシェルを起動します:
        ```bash
        python manage.py shell
        ```

    2. 次のコマンドを実行して、`SECRET_KEY` を生成します:
        ```python
        from django.core.management.utils import get_random_secret_key
        get_random_secret_key()
        ```
    3. 生成された`SECRET_KEY` を、`settings.py`に設定してください
       ```
       SECRET_KEY = 'your_secret_key'
       ```
7.  `settings.py` のデータベース設定を MariaDB に変更します:
   
    以下は MariaDB に接続するためのサンプル設定です。これを settings.py の DATABASES セクションに追加してください。
    ```
    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '3306',  
        }
    }
    ```
9. マイグレーションを適用します:
    ```bash
    python manage.py migrate
    ```

10. 管理者ユーザーを作成します:
    ```bash
    python manage.py createsuperuser
    ```

11. 開発サーバーを起動します:
    ```bash
    python manage.py runserver
    ```

12. ブラウザで以下のURLにアクセスして動作を確認します:
    ```
    http://127.0.0.1:8000/diary/
    ```

---

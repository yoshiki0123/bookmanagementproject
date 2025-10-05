// googleのAPIからisbnを取得し実行する
document.getElementById('isbn-form').addEventListener('submit', function (e) {
e.preventDefault(); //フォームの通常の送信処理（ページ遷移）を止める。これがないとリロードされてしまう。
const isbn = document.getElementById('isbn-input').value.trim();
const errorDiv = document.getElementById('error-message');
const registerForm = document.getElementById('register-form');

// 初期化
errorDiv.classList.add('d-none');
errorDiv.textContent = "";
registerForm.classList.add('d-none');

// 正規表現で「10桁 または 13桁の数字か」をチェック
if (!isbn.match(/^\d{10}(\d{3})?$/)) {
    errorDiv.textContent = "有効なISBN（10桁または13桁）を入力してください。";
    errorDiv.classList.remove('d-none');
    return;
}

fetch(`https://www.googleapis.com/books/v1/volumes?q=isbn:${isbn}`)
    .then(res => {
        if (!res.ok) {
            throw new Error("Google Books APIへの接続に失敗しました。");
        }
        return res.json();
    })
    .then(data => {
    if (!data.totalItems || !data.items || !data.items[0]) {
        throw new Error("書籍が見つかりませんでした。");
    }

    const info = data.items[0].volumeInfo;
    document.getElementById('title').value = info.title || "";
    document.getElementById('author').value = (info.authors || [""]).join(', ');
    document.getElementById('isbn').value = isbn;

    registerForm.classList.remove('d-none');
    })
    .catch(err => {
    errorDiv.textContent = err.message || "予期せぬエラーが発生しました。";
    errorDiv.classList.remove('d-none');
    });
});

// カーソルをデフォルトで検索欄に配置
window.addEventListener('DOMContentLoaded', function () {
const isbnInput = document.getElementById('isbn-input');
if (isbnInput) {
    isbnInput.focus();
}
});

// alertを3秒後にゆっくり消す処理
$(document).ready(function(){
$(".alert").delay(3000).fadeOut("slow");
});
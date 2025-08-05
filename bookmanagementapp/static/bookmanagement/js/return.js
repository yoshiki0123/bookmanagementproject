// static/js/return.js
(function () {
  const KEY   = 'return:selected_isbns'; // ← Borrow と分けるためのキー
  const FORM  = 'returnForm';            // ← borrow.html との違い：フォームID
  const FIELD = 'selected_isbns';        // 送信用 hidden の name（JSON 文字列）

  const store = window.sessionStorage;

  // ---- storage helpers ----
  function readArr() {
    const raw = store.getItem(KEY);
    if (!raw) return [];
    try {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed)) return parsed.map(String);
      if (typeof parsed === 'string') {
        return (parsed.includes(',') ? parsed.split(',') : [parsed]).map(s => s.trim()).filter(Boolean);
      }
      return [String(parsed)];
    } catch {
      return (raw.includes(',') ? raw.split(',') : [raw]).map(s => s.trim()).filter(Boolean);
    }
  }
  function writeArr(arr) {
    store.setItem(KEY, JSON.stringify(arr.map(String)));
  }

  // 表示時：保存分をチェックに反映
  function restoreChecks() {
    const saved = new Set(readArr());
    document.querySelectorAll('input[type="checkbox"][name="selected_isbns"]').forEach(cb => {
      const v = (cb.value || '').trim();
      cb.checked = saved.has(v);
    });
  }

  // 変更を即保存（ページまたぎ保持）
  function bindChangeSave() {
    document.querySelectorAll('input[type="checkbox"][name="selected_isbns"]').forEach(cb => {
      cb.addEventListener('change', (e) => {
        const v = (e.target.value || '').trim();
        if (!v) return;
        const arr = readArr();
        if (e.target.checked) {
          if (!arr.includes(v)) arr.push(v);   // 過剰増殖は防止
        } else {
          const filtered = arr.filter(x => x !== v);
          arr.length = 0; arr.push(...filtered);
        }
        writeArr(arr);
      });
    });
  }

  function init() {
    restoreChecks();
    bindChangeSave();

    const form = document.getElementById(FORM);
    if (!form) return;

    // 送信時：sessionStorage の“全件”を JSON 1本で送る → 直後に必ずクリア
    form.addEventListener('submit', (e) => {
      e.preventDefault(); // 整えてから送る（クリア取りこぼし防止）

      // 1) sessionStorage 全量
      const all = readArr();

      // 直前の操作取りこぼし防止：今ページで checked の分を合流（任意だが推奨）
      form.querySelectorAll('input[type="checkbox"][name="selected_isbns"]:checked')
          .forEach(cb => {
            const v = (cb.value || '').trim();
            if (v && !all.includes(v)) all.push(v);
          });

      // 2) hidden（JSON 1本）をセット
      form.querySelectorAll(`input[type="hidden"][name="${FIELD}"]`).forEach(n => n.remove());
      // 重複送信防止：画面上の checkbox は送らないよう name を変更
      form.querySelectorAll('input[type="checkbox"][name="selected_isbns"]')
          .forEach(cb => cb.name = '_selected_isbns');

      const h = document.createElement('input');
      h.type  = 'hidden';
      h.name  = FIELD;                 // サーバ側は json.loads で受ける
      h.value = JSON.stringify(all);   // 例: ["978...","978..."]
      form.appendChild(h);

      // 3) 送信前に sessionStorage を必ず空にする（hidden 作成後なので安全）
      try { store.removeItem(KEY); } catch {}

      // 4) 送信（この submit は再発火しません）
      form.submit();
    });
  }

  document.addEventListener('DOMContentLoaded', init);
  // 戻る（bfcache）でもチェック復元
  window.addEventListener('pageshow', restoreChecks);
})();

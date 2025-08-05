// static/js/borrow.js
(function () {
  const KEY = 'borrow:selected_isbns';   // sessionStorage のキー
  const FORM_ID = 'borrowForm';          // POSTフォームのid（borrow.html と一致）
  const FIELD = 'selected_isbns';        // 送信用 hidden の name（JSON 文字列）

  const store = window.sessionStorage;

  // ---- storage helpers ----
  function readArr() {
    const raw = store.getItem(KEY);
    if (!raw) return [];
    try {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed)) return parsed.map(String);
      if (typeof parsed === 'string') return (parsed.includes(',') ? parsed.split(',') : [parsed]).map(s => s.trim()).filter(Boolean);
      return [String(parsed)];
    } catch {
      return (raw.includes(',') ? raw.split(',') : [raw]).map(s => s.trim()).filter(Boolean);
    }
  }
  function writeArr(arr) { store.setItem(KEY, JSON.stringify(arr.map(String))); }

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
          // 重複はサーバで処理可だが、クライアントでも過剰増殖を防いでおく
          if (!arr.includes(v)) arr.push(v);
        } else {
          // その値を全て除去（1回で十分だが安全に）
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

    const form = document.getElementById(FORM_ID);
    if (!form) return;

    // 送信時：sessionStorage の中身をそのまま JSON 1本で送る → 直後に必ずクリア
    form.addEventListener('submit', (e) => {
      e.preventDefault();                         // 整えてから送る（クリア取りこぼし防止）

      // 1) sessionStorage 全量を取得
      const all = readArr();

      // 直前の操作取りこぼしを防ぐため、「今ページでchecked」を合流（任意）
      form.querySelectorAll('input[type="checkbox"][name="selected_isbns"]:checked')
          .forEach(cb => { const v = (cb.value || '').trim(); if (v && !all.includes(v)) all.push(v); });

      // 2) hidden を作成（JSON 1本）
      // （既存 hidden を掃除）
      form.querySelectorAll(`input[type="hidden"][name="${FIELD}"]`).forEach(n => n.remove());
      // （画面のチェックボックスは送らない：重複送信を避ける）
      form.querySelectorAll('input[type="checkbox"][name="selected_isbns"]').forEach(cb => cb.name = '_selected_isbns');

      const h = document.createElement('input');
      h.type = 'hidden';
      h.name = FIELD;                              // サーバは json.loads で受ける
      h.value = JSON.stringify(all);              // 例: ["0000000000016","1111111111111"]
      form.appendChild(h);

      // 3) 送信前に sessionStorage を必ず空にする（hidden 作成後なので安全）
      try { store.removeItem(KEY); } catch {}

      // （デバッグしたいときは以下を一時的に残す）
      // console.log('[borrow] POST selected_isbns =', h.value);

      // 4) 送信（この submit は再発火しません）
      form.submit();
    });
  }

  document.addEventListener('DOMContentLoaded', init);
  // 戻る（bfcache）でもチェック復元できるように
  window.addEventListener('pageshow', restoreChecks);
})();

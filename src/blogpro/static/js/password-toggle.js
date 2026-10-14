// 「👁」ボタンでパスワード入力欄の表示/非表示を切り替える
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".toggle-password").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var input = document.getElementById(btn.dataset.target);
      if (!input) { return; }
      var show = input.type === "password";
      input.type = show ? "text" : "password";
      btn.setAttribute("aria-pressed", show ? "true" : "false");
      btn.setAttribute("aria-label", show ? "パスワードを隠す" : "パスワードを表示");
      btn.classList.toggle("active", show);
    });
  });
});

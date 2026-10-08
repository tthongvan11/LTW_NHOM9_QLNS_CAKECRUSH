(() => {
  // Khối JSON test chỉ có trên trang đăng nhập dev; không có khối này thì script dừng ngay.
  const payload = document.getElementById("dev-login-accounts");
  if (!payload) return;
  const accounts = JSON.parse(payload.textContent);
  const username = document.querySelector('input[name="username"]');
  const password = document.querySelector('input[name="password"]');
  const buttons = document.querySelectorAll("[data-dev-role]");
  const status = document.querySelector(".cc-dev-login-status");

  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      const account = accounts.find((entry) => entry.role === button.dataset.devRole);
      if (!account) return;
      // Chỉ điền hai ô; người dùng vẫn bấm Đăng nhập để Django kiểm tra tài khoản/mật khẩu thật.
      username.value = account.username;
      password.value = account.password;
      [username, password].forEach((input) => {
        input.dispatchEvent(new Event("input", { bubbles: true }));
        input.dispatchEvent(new Event("change", { bubbles: true }));
      });
      buttons.forEach((item) => item.setAttribute("aria-pressed", String(item === button)));
      status.textContent = `Đã điền tài khoản ${account.username}. Bấm Đăng nhập để tiếp tục.`;
    });
  });
})();

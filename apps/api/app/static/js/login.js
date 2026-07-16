const bodyEl = document.body;
const themeToggle = document.getElementById("login-theme-toggle");
const passwordInput = document.getElementById("password");
const passwordToggle = document.getElementById("password-toggle");
const THEME_KEY = "miyin.dashboard.theme.v2";

function applyTheme(theme) {
  const isDark = theme === "dark";
  bodyEl.classList.toggle("dark", isDark);
  document.documentElement.style.colorScheme = isDark ? "dark" : "light";

  if (!themeToggle) return;
  const icon = themeToggle.querySelector("i");
  const label = themeToggle.querySelector("span");
  const nextLabel = isDark ? themeToggle.dataset.themeLight : themeToggle.dataset.themeDark;
  if (icon) icon.className = isDark ? "ri-sun-line" : "ri-moon-line";
  if (label) label.textContent = nextLabel || "";
  if (nextLabel) {
    themeToggle.setAttribute("aria-label", nextLabel);
    themeToggle.title = nextLabel;
  }
}

try {
  applyTheme(window.localStorage.getItem(THEME_KEY) || "light");
} catch (err) {
  applyTheme("light");
}

themeToggle?.addEventListener("click", () => {
  const nextTheme = bodyEl.classList.contains("dark") ? "light" : "dark";
  applyTheme(nextTheme);
  try {
    window.localStorage.setItem(THEME_KEY, nextTheme);
  } catch (err) {
    // Storage can be unavailable in hardened browser contexts.
  }
});

passwordToggle?.addEventListener("click", () => {
  if (!passwordInput) return;
  const reveal = passwordInput.type === "password";
  passwordInput.type = reveal ? "text" : "password";
  const icon = passwordToggle.querySelector("i");
  if (icon) icon.className = reveal ? "ri-eye-off-line" : "ri-eye-line";
  passwordInput.focus();
});

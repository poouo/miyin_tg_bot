const bodyEl = document.body;
const sidebar = document.getElementById("sidebar");
const menuToggle = document.getElementById("mobile-menu-toggle");
const workspaceTitle = document.getElementById("workspace-title");
const navItems = Array.from(document.querySelectorAll(".nav-item"));

const securityOutput = document.getElementById("security-output");
const runtimeOutput = document.getElementById("runtime-output");
const btnCheck = document.getElementById("check-update");
const btnTrigger = document.getElementById("trigger-update");
const btnSaveSecurity = document.getElementById("save-security");
const btnSaveRuntime = document.getElementById("save-runtime");
const btnSavePassword = document.getElementById("save-password");

const loginBanEnabled = document.getElementById("login-ban-enabled");
const loginMaxAttempts = document.getElementById("login-max-attempts");
const loginBanMinutes = document.getElementById("login-ban-minutes");
const webLanguage = document.getElementById("web-language");
const currentPassword = document.getElementById("current-password");
const newPassword = document.getElementById("new-password");
const confirmPassword = document.getElementById("confirm-password");
const passwordOutput = document.getElementById("password-output");

const rtTelegramBotToken = document.getElementById("rt-telegram-bot-token");
const rtTelegramBotUsername = document.getElementById("rt-telegram-bot-username");
const rtTelegramAdminIds = document.getElementById("rt-telegram-admin-ids");
const rtDeepseekApiKey = document.getElementById("rt-deepseek-api-key");
const rtDeepseekBaseUrl = document.getElementById("rt-deepseek-base-url");
const rtDeepseekModel = document.getElementById("rt-deepseek-model");
const rtDeepseekTimeoutSec = document.getElementById("rt-deepseek-timeout-sec");
const rtJoinVerifyTimeoutSec = document.getElementById("rt-join-verify-timeout-sec");
const rtSpamWindowSec = document.getElementById("rt-spam-window-sec");
const rtSpamMaxMessages = document.getElementById("rt-spam-max-messages");
const rtAdRegex = document.getElementById("rt-ad-regex");

const upgradeFill = document.getElementById("upgrade-fill");
const upgradeStatus = document.getElementById("upgrade-status");

const i18nEl = document.getElementById("i18n-data");
const i18n = i18nEl ? JSON.parse(i18nEl.textContent || "{}") : {};

function t(key, fallback) {
  return i18n[key] || fallback || key;
}

let updatePollTimer = null;

function print(el, data) {
  if (!el) return;
  el.textContent = JSON.stringify(data, null, 2);
}

function setUpgradeStatus(progress, text, type = "normal") {
  const safeProgress = Math.max(0, Math.min(100, Number(progress) || 0));
  if (upgradeFill) {
    upgradeFill.style.width = `${safeProgress}%`;
    upgradeFill.classList.remove("success", "failed");
    if (type === "success") upgradeFill.classList.add("success");
    if (type === "failed") upgradeFill.classList.add("failed");
  }
  if (upgradeStatus) {
    upgradeStatus.textContent = `${safeProgress}% - ${text}`;
  }
}

function setActiveNav(target) {
  navItems.forEach((item) => {
    item.classList.toggle("active", item.dataset.target === target);
  });
  const active = navItems.find((item) => item.dataset.target === target);
  if (active && workspaceTitle) {
    workspaceTitle.textContent = active.textContent || "";
  }
}

function closeMobileSidebar() {
  bodyEl.classList.remove("sidebar-open");
}

menuToggle?.addEventListener("click", () => {
  bodyEl.classList.toggle("sidebar-open");
});

document.addEventListener("click", (event) => {
  if (!bodyEl.classList.contains("sidebar-open")) return;
  const target = event.target;
  if (!(target instanceof Element)) return;
  if (sidebar?.contains(target) || menuToggle?.contains(target)) return;
  closeMobileSidebar();
});

navItems.forEach((item) => {
  item.addEventListener("click", () => {
    const target = item.dataset.target;
    if (!target) return;
    const section = document.getElementById(target);
    if (!section) return;
    setActiveNav(target);
    section.scrollIntoView({ behavior: "smooth", block: "start" });
    closeMobileSidebar();
  });
});

async function pollOnlineUpdateStatus() {
  try {
    const res = await fetch("/api/v1/updates/online-status");
    const data = await res.json();
    if (!data.ok) {
      setUpgradeStatus(0, t("update_status_load_failed"), "failed");
      stopPolling();
      if (btnTrigger) btnTrigger.disabled = false;
      return;
    }

    const state = data.state || "idle";
    const progress = data.progress || 0;
    const message = data.message || t("update_status_working");

    if (state === "running") {
      setUpgradeStatus(progress, message, "normal");
      if (btnTrigger) btnTrigger.disabled = true;
      return;
    }

    if (state === "success") {
      setUpgradeStatus(100, t("update_success_refreshing"), "success");
      stopPolling();
      if (btnTrigger) btnTrigger.disabled = false;
      setTimeout(() => window.location.reload(), 1800);
      return;
    }

    if (state === "failed") {
      setUpgradeStatus(progress, t("update_failed_retry"), "failed");
      stopPolling();
      if (btnTrigger) btnTrigger.disabled = false;
      return;
    }

    setUpgradeStatus(0, t("update_ready"), "normal");
    stopPolling();
    if (btnTrigger) btnTrigger.disabled = false;
  } catch (err) {
    setUpgradeStatus(0, t("update_network_error"), "failed");
    stopPolling();
    if (btnTrigger) btnTrigger.disabled = false;
  }
}

function startPolling() {
  if (updatePollTimer) return;
  updatePollTimer = setInterval(pollOnlineUpdateStatus, 1500);
}

function stopPolling() {
  if (!updatePollTimer) return;
  clearInterval(updatePollTimer);
  updatePollTimer = null;
}

btnCheck?.addEventListener("click", async () => {
  setUpgradeStatus(0, t("update_checking"));
  try {
    const res = await fetch("/api/v1/updates/check");
    const data = await res.json();
    if (!data.ok) {
      setUpgradeStatus(0, t("update_check_failed"), "failed");
      return;
    }
    if (data.has_update) {
      setUpgradeStatus(0, t("update_available_click"));
    } else {
      setUpgradeStatus(100, t("update_uptodate"), "success");
    }
  } catch (err) {
    setUpgradeStatus(0, t("update_check_failed"), "failed");
  }
});

btnTrigger?.addEventListener("click", async () => {
  if (btnTrigger) btnTrigger.disabled = true;
  setUpgradeStatus(2, t("update_starting"));
  try {
    const res = await fetch("/api/v1/updates/online", { method: "POST" });
    const data = await res.json();
    if (!data.ok) {
      setUpgradeStatus(0, data.message || t("update_start_failed"), "failed");
      if (btnTrigger) btnTrigger.disabled = false;
      return;
    }
    startPolling();
    await pollOnlineUpdateStatus();
  } catch (err) {
    setUpgradeStatus(0, t("update_start_failed"), "failed");
    if (btnTrigger) btnTrigger.disabled = false;
  }
});

btnSaveRuntime?.addEventListener("click", async () => {
  if (runtimeOutput) runtimeOutput.textContent = t("security_saving");
  const payload = {
    telegram_bot_token: rtTelegramBotToken?.value || "",
    telegram_bot_username: rtTelegramBotUsername?.value || "",
    telegram_admin_ids: rtTelegramAdminIds?.value || "",
    deepseek_api_key: rtDeepseekApiKey?.value || "",
    deepseek_base_url: rtDeepseekBaseUrl?.value || "https://api.deepseek.com",
    deepseek_model: rtDeepseekModel?.value || "deepseek-chat",
    deepseek_timeout_sec: Number(rtDeepseekTimeoutSec?.value || 30),
    join_verify_timeout_sec: Number(rtJoinVerifyTimeoutSec?.value || 180),
    spam_window_sec: Number(rtSpamWindowSec?.value || 10),
    spam_max_messages: Number(rtSpamMaxMessages?.value || 6),
    ad_regex: rtAdRegex?.value || "",
  };

  try {
    const res = await fetch("/api/v1/runtime", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    print(runtimeOutput, data);
  } catch (err) {
    print(runtimeOutput, { ok: false, error: String(err) });
  }
});

btnSaveSecurity?.addEventListener("click", async () => {
  if (securityOutput) securityOutput.textContent = t("security_saving");
  const payload = {
    login_ban_enabled: Boolean(loginBanEnabled?.checked),
    login_max_attempts: Number(loginMaxAttempts?.value || 5),
    login_ban_minutes: Number(loginBanMinutes?.value || 5),
    web_language: (webLanguage?.value || "zh").toLowerCase(),
  };

  try {
    const res = await fetch("/api/v1/security/login", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    print(securityOutput, data);
    if (data.web_language) {
      setTimeout(() => window.location.reload(), 300);
    }
  } catch (err) {
    print(securityOutput, { ok: false, error: String(err) });
  }
});

btnSavePassword?.addEventListener("click", async () => {
  if (!passwordOutput) return;
  passwordOutput.textContent = t("security_saving");

  const payload = {
    current_password: currentPassword?.value || "",
    new_password: newPassword?.value || "",
    confirm_password: confirmPassword?.value || "",
  };

  try {
    const res = await fetch("/api/v1/security/password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();

    if (!res.ok) {
      const detail = data?.detail || t("password_change_failed");
      passwordOutput.textContent = `${t("password_change_failed")}: ${detail}`;
      return;
    }

    passwordOutput.textContent = t("password_changed");
    if (currentPassword) currentPassword.value = "";
    if (newPassword) newPassword.value = "";
    if (confirmPassword) confirmPassword.value = "";
  } catch (err) {
    passwordOutput.textContent = `${t("password_change_failed")}: ${String(err)}`;
  }
});

pollOnlineUpdateStatus();

const bodyEl = document.body;
const sidebar = document.getElementById("sidebar");
const workspaceEl = document.querySelector(".workspace");
const menuToggle = document.getElementById("mobile-menu-toggle");
const workspaceTitle = document.getElementById("workspace-title");
const actionStatus = document.getElementById("action-status");
const navItems = Array.from(document.querySelectorAll(".nav-item"));
const sections = Array.from(document.querySelectorAll(".section"));

const securityOutput = document.getElementById("security-output");
const runtimeOutput = document.getElementById("runtime-output");
const deepseekOutput = document.getElementById("deepseek-output");
const passwordOutput = document.getElementById("password-output");
const btnCheck = document.getElementById("check-update");
const btnTrigger = document.getElementById("trigger-update");
const btnSaveSecurity = document.getElementById("save-security");
const btnSaveRuntime = document.getElementById("save-runtime");
const btnSaveDeepseek = document.getElementById("save-deepseek");
const btnSavePassword = document.getElementById("save-password");

const loginBanEnabled = document.getElementById("login-ban-enabled");
const loginMaxAttempts = document.getElementById("login-max-attempts");
const loginBanMinutes = document.getElementById("login-ban-minutes");
const webLanguage = document.getElementById("web-language");
const currentPassword = document.getElementById("current-password");
const newPassword = document.getElementById("new-password");
const confirmPassword = document.getElementById("confirm-password");

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

const arChatId = document.getElementById("ar-chat-id");
const arKeyword = document.getElementById("ar-keyword");
const arReplyText = document.getElementById("ar-reply-text");
const arDeleteAfter = document.getElementById("ar-delete-after");
const arEnabled = document.getElementById("ar-enabled");
const arAddRule = document.getElementById("ar-add-rule");
const arCancelEdit = document.getElementById("ar-cancel-edit");
const arRefresh = document.getElementById("ar-refresh");
const arTableBody = document.getElementById("ar-table-body");
const arOutput = document.getElementById("ar-output");

const akChatId = document.getElementById("ak-chat-id");
const akKeyword = document.getElementById("ak-keyword");
const akEnabled = document.getElementById("ak-enabled");
const akAddKeyword = document.getElementById("ak-add-keyword");
const akCancelEdit = document.getElementById("ak-cancel-edit");
const akRefresh = document.getElementById("ak-refresh");
const akTableBody = document.getElementById("ak-table-body");
const akOutput = document.getElementById("ak-output");

const evChatId = document.getElementById("ev-chat-id");
const evRefresh = document.getElementById("ev-refresh");
const evTableBody = document.getElementById("ev-table-body");
const groupsTableBody = document.getElementById("groups-table-body");
const groupsOutput = document.getElementById("groups-output");

const i18nEl = document.getElementById("i18n-data");
const i18n = i18nEl ? JSON.parse(i18nEl.textContent || "{}") : {};

let updatePollTimer = null;
const ACTIVE_SECTION_KEY = "miyin.dashboard.activeSection";
let arEditingRuleId = null;
let akEditingKeywordId = null;
let actionStatusTimer = null;

function t(key, fallback) {
  return i18n[key] || fallback || key;
}

function print(el, data) {
  if (el) {
    el.textContent = JSON.stringify(data, null, 2);
  }
  if (Array.isArray(data)) return;
  if (!data || typeof data !== "object") return;
  if (data.ok === false) {
    showStatus(data.message || data.detail || data.error || t("operation_failed", "Operation failed"), true);
    return;
  }
  showStatus(t("saved", "Saved"), false);
}

function escapeHtml(text) {
  return String(text || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function resetAutoReplyEditor() {
  arEditingRuleId = null;
  if (arAddRule) arAddRule.textContent = t("auto_reply_add", "Add Auto Reply");
  if (arCancelEdit) arCancelEdit.style.display = "none";
  if (arKeyword) arKeyword.value = "";
  if (arReplyText) arReplyText.value = "";
  if (arDeleteAfter) arDeleteAfter.value = "0";
  if (arEnabled) arEnabled.checked = true;
}

function resetAdKeywordEditor() {
  akEditingKeywordId = null;
  if (akAddKeyword) akAddKeyword.textContent = t("ad_keyword_add", "Add Ad Keyword");
  if (akCancelEdit) akCancelEdit.style.display = "none";
  if (akKeyword) akKeyword.value = "";
  if (akEnabled) akEnabled.checked = true;
}

function showStatus(message, isError = false) {
  if (!actionStatus) return;
  actionStatus.textContent = message;
  actionStatus.classList.toggle("error", Boolean(isError));
  if (actionStatusTimer) {
    window.clearTimeout(actionStatusTimer);
  }
  actionStatusTimer = window.setTimeout(() => {
    if (!actionStatus) return;
    actionStatus.textContent = "";
    actionStatus.classList.remove("error");
  }, 2200);
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

function setActiveSection(target) {
  sections.forEach((section) => {
    section.classList.toggle("section-active", section.id === target);
  });
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

async function handleSectionEnter(target) {
  if (target === "auto-replies") {
    await loadAutoReplies();
  }
  if (target === "ad-keywords") {
    await loadAdKeywords();
  }
  if (target === "member-events") {
    await loadMemberEvents();
  }
}

navItems.forEach((item) => {
  item.addEventListener("click", async () => {
    const target = item.dataset.target;
    if (!target) return;
    const section = document.getElementById(target);
    if (!section) return;
    setActiveNav(target);
    setActiveSection(target);
    try {
      window.localStorage.setItem(ACTIVE_SECTION_KEY, target);
    } catch (err) {
      // ignore
    }
    if (workspaceEl) {
      workspaceEl.scrollTop = 0;
    }
    await handleSectionEnter(target);
    closeMobileSidebar();
  });
});

let initialTarget = navItems.find((item) => item.classList.contains("active"))?.dataset.target || "overview";
try {
  const stored = window.localStorage.getItem(ACTIVE_SECTION_KEY) || "";
  if (stored && navItems.some((item) => item.dataset.target === stored)) {
    initialTarget = stored;
  }
} catch (err) {
  // ignore
}
setActiveNav(initialTarget);
setActiveSection(initialTarget);
handleSectionEnter(initialTarget);

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

function buildRuntimePayload() {
  return {
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
}

async function saveRuntime(outputEl) {
  if (outputEl) outputEl.textContent = t("security_saving");
  const payload = {
    ...buildRuntimePayload(),
  };

  try {
    const res = await fetch("/api/v1/runtime", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    print(outputEl, data);
  } catch (err) {
    print(outputEl, { ok: false, error: String(err) });
  }
}

btnSaveRuntime?.addEventListener("click", async () => {
  await saveRuntime(runtimeOutput);
});

btnSaveDeepseek?.addEventListener("click", async () => {
  await saveRuntime(deepseekOutput);
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
      showStatus(`${t("password_change_failed")}: ${detail}`, true);
      return;
    }

    showStatus(t("password_changed"), false);
    if (currentPassword) currentPassword.value = "";
    if (newPassword) newPassword.value = "";
    if (confirmPassword) confirmPassword.value = "";
  } catch (err) {
    showStatus(`${t("password_change_failed")}: ${String(err)}`, true);
  }
});

function renderAutoReplies(items) {
  if (!arTableBody) return;
  if (!Array.isArray(items) || !items.length) {
    arTableBody.innerHTML = `<tr><td colspan="5">${escapeHtml(t("no_data", "No data"))}</td></tr>`;
    return;
  }

  arTableBody.innerHTML = items
    .map((item) => {
      const statusText = item.enabled ? t("switch_on", "on") : t("switch_off", "off");
      const toggleText = item.enabled ? t("disable", "Disable") : t("enable", "Enable");
      return `<tr>
        <td>${escapeHtml(item.keyword)}</td>
        <td>${escapeHtml(item.reply_text)}</td>
        <td>${Number(item.delete_after_seconds || 0)}</td>
        <td>${escapeHtml(statusText)}</td>
        <td>
          <button class="table-btn" type="button" data-action="edit" data-id="${item.id}">${escapeHtml(t("edit", "Edit"))}</button>
          <button class="table-btn" type="button" data-action="toggle" data-id="${item.id}" data-enabled="${item.enabled ? 1 : 0}">${escapeHtml(toggleText)}</button>
          <button class="table-btn warning" type="button" data-action="delete" data-id="${item.id}">${escapeHtml(t("delete", "Delete"))}</button>
        </td>
      </tr>`;
    })
    .join("");
}

async function loadAutoReplies() {
  if (!arChatId?.value) {
    renderAutoReplies([]);
    return;
  }
  try {
    const res = await fetch(`/api/v1/groups/${encodeURIComponent(arChatId.value)}/auto-replies`);
    const data = await res.json();
    if (!res.ok) {
      print(arOutput, data);
      return;
    }
    renderAutoReplies(data);
  } catch (err) {
    print(arOutput, { ok: false, error: String(err) });
  }
}

arAddRule?.addEventListener("click", async () => {
  const chatId = arChatId?.value || "";
  const keyword = arKeyword?.value.trim() || "";
  const replyText = arReplyText?.value.trim() || "";
  const deleteAfter = Number(arDeleteAfter?.value || 0);
  if (!chatId || !keyword || !replyText) {
    print(arOutput, { ok: false, message: t("fill_required_fields", "Please fill required fields") });
    return;
  }

  const payload = {
    chat_id: Number(chatId),
    keyword,
    reply_text: replyText,
    delete_after_seconds: Math.max(0, deleteAfter),
    enabled: Boolean(arEnabled?.checked),
  };
  try {
    const isEditing = arEditingRuleId !== null;
    const url = isEditing
      ? `/api/v1/groups/${encodeURIComponent(chatId)}/auto-replies/${encodeURIComponent(String(arEditingRuleId))}`
      : `/api/v1/groups/${encodeURIComponent(chatId)}/auto-replies`;
    const method = isEditing ? "PATCH" : "POST";
    const bodyPayload = isEditing
      ? {
          keyword: payload.keyword,
          reply_text: payload.reply_text,
          delete_after_seconds: payload.delete_after_seconds,
          enabled: payload.enabled,
        }
      : payload;

    const res = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(bodyPayload),
    });
    const data = await res.json();
    print(arOutput, data);
    if (!res.ok) return;
    resetAutoReplyEditor();
    await loadAutoReplies();
  } catch (err) {
    print(arOutput, { ok: false, error: String(err) });
  }
});

arCancelEdit?.addEventListener("click", () => {
  resetAutoReplyEditor();
});

arRefresh?.addEventListener("click", async () => {
  await loadAutoReplies();
});

arChatId?.addEventListener("change", async () => {
  resetAutoReplyEditor();
  await loadAutoReplies();
});

arTableBody?.addEventListener("click", async (event) => {
  const target = event.target;
  if (!(target instanceof HTMLButtonElement)) return;
  const action = target.dataset.action || "";
  const ruleId = target.dataset.id || "";
  const chatId = arChatId?.value || "";
  if (!action || !ruleId || !chatId) return;

  try {
    if (action === "delete") {
      const res = await fetch(`/api/v1/groups/${encodeURIComponent(chatId)}/auto-replies/${encodeURIComponent(ruleId)}`, {
        method: "DELETE",
      });
      const data = await res.json();
      print(arOutput, data);
      if (!res.ok) return;
      if (String(arEditingRuleId) === String(ruleId)) {
        resetAutoReplyEditor();
      }
      await loadAutoReplies();
      return;
    }

    if (action === "edit") {
      const res = await fetch(`/api/v1/groups/${encodeURIComponent(chatId)}/auto-replies`);
      const data = await res.json();
      if (!res.ok) {
        print(arOutput, data);
        return;
      }
      const found = Array.isArray(data) ? data.find((item) => String(item.id) === String(ruleId)) : null;
      if (!found) {
        print(arOutput, { ok: false, message: t("rule_not_found", "Rule not found") });
        return;
      }
      arEditingRuleId = found.id;
      if (arKeyword) arKeyword.value = found.keyword || "";
      if (arReplyText) arReplyText.value = found.reply_text || "";
      if (arDeleteAfter) arDeleteAfter.value = String(Number(found.delete_after_seconds || 0));
      if (arEnabled) arEnabled.checked = Boolean(found.enabled);
      if (arAddRule) arAddRule.textContent = t("auto_reply_update", "Update Rule");
      if (arCancelEdit) arCancelEdit.style.display = "";
      return;
    }

    if (action === "toggle") {
      const enabled = target.dataset.enabled === "1";
      const payload = { enabled: !enabled };
      const res = await fetch(`/api/v1/groups/${encodeURIComponent(chatId)}/auto-replies/${encodeURIComponent(ruleId)}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      print(arOutput, data);
      if (!res.ok) return;
      await loadAutoReplies();
    }
  } catch (err) {
    print(arOutput, { ok: false, error: String(err) });
  }
});

groupsTableBody?.addEventListener("click", async (event) => {
  const target = event.target;
  if (!(target instanceof HTMLButtonElement)) return;
  const action = target.dataset.action || "";
  if (action !== "save-group-ai") return;
  const chatId = target.dataset.chatId || "";
  if (!chatId) return;

  const checkbox = groupsTableBody.querySelector(`.group-ai-toggle[data-chat-id="${chatId}"]`);
  if (!(checkbox instanceof HTMLInputElement)) return;
  const payload = { deepseek_enabled: checkbox.checked };

  try {
    const res = await fetch(`/api/v1/groups/${encodeURIComponent(chatId)}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    print(groupsOutput, data);
    if (!res.ok) return;
    target.textContent = t("saved", "Saved");
    setTimeout(() => {
      target.textContent = t("save", "Save");
    }, 1200);
  } catch (err) {
    print(groupsOutput, { ok: false, error: String(err) });
  }
});

function renderAdKeywords(items) {
  if (!akTableBody) return;
  if (!Array.isArray(items) || !items.length) {
    akTableBody.innerHTML = `<tr><td colspan="3">${escapeHtml(t("no_data", "No data"))}</td></tr>`;
    return;
  }

  akTableBody.innerHTML = items
    .map((item) => {
      const statusText = item.enabled ? t("switch_on", "on") : t("switch_off", "off");
      const toggleText = item.enabled ? t("disable", "Disable") : t("enable", "Enable");
      return `<tr>
        <td>${escapeHtml(item.keyword)}</td>
        <td>${escapeHtml(statusText)}</td>
        <td>
          <button class="table-btn" type="button" data-action="edit" data-id="${item.id}">${escapeHtml(t("edit", "Edit"))}</button>
          <button class="table-btn" type="button" data-action="toggle" data-id="${item.id}" data-enabled="${item.enabled ? 1 : 0}">${escapeHtml(toggleText)}</button>
          <button class="table-btn warning" type="button" data-action="delete" data-id="${item.id}">${escapeHtml(t("delete", "Delete"))}</button>
        </td>
      </tr>`;
    })
    .join("");
}

async function loadAdKeywords() {
  if (!akChatId?.value) {
    renderAdKeywords([]);
    return;
  }
  try {
    const res = await fetch(`/api/v1/groups/${encodeURIComponent(akChatId.value)}/ad-keywords`);
    const data = await res.json();
    if (!res.ok) {
      print(akOutput, data);
      return;
    }
    renderAdKeywords(data);
  } catch (err) {
    print(akOutput, { ok: false, error: String(err) });
  }
}

akAddKeyword?.addEventListener("click", async () => {
  const chatId = akChatId?.value || "";
  const keyword = akKeyword?.value.trim() || "";
  if (!chatId || !keyword) {
    print(akOutput, { ok: false, message: t("fill_required_fields", "Please fill required fields") });
    return;
  }

  const payload = {
    chat_id: Number(chatId),
    keyword,
    enabled: Boolean(akEnabled?.checked),
  };
  try {
    const isEditing = akEditingKeywordId !== null;
    const url = isEditing
      ? `/api/v1/groups/${encodeURIComponent(chatId)}/ad-keywords/${encodeURIComponent(String(akEditingKeywordId))}`
      : `/api/v1/groups/${encodeURIComponent(chatId)}/ad-keywords`;
    const method = isEditing ? "PATCH" : "POST";
    const bodyPayload = isEditing
      ? {
          keyword: payload.keyword,
          enabled: payload.enabled,
        }
      : payload;
    const res = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(bodyPayload),
    });
    const data = await res.json();
    print(akOutput, data);
    if (!res.ok) return;

    resetAdKeywordEditor();
    await loadAdKeywords();
  } catch (err) {
    print(akOutput, { ok: false, error: String(err) });
  }
});

akCancelEdit?.addEventListener("click", () => {
  resetAdKeywordEditor();
});

akRefresh?.addEventListener("click", async () => {
  await loadAdKeywords();
});

akChatId?.addEventListener("change", async () => {
  resetAdKeywordEditor();
  await loadAdKeywords();
});

akTableBody?.addEventListener("click", async (event) => {
  const target = event.target;
  if (!(target instanceof HTMLButtonElement)) return;
  const action = target.dataset.action || "";
  const keywordId = target.dataset.id || "";
  const chatId = akChatId?.value || "";
  if (!action || !keywordId || !chatId) return;

  try {
    if (action === "delete") {
      const res = await fetch(`/api/v1/groups/${encodeURIComponent(chatId)}/ad-keywords/${encodeURIComponent(keywordId)}`, {
        method: "DELETE",
      });
      const data = await res.json();
      print(akOutput, data);
      if (!res.ok) return;
      if (String(akEditingKeywordId) === String(keywordId)) {
        resetAdKeywordEditor();
      }
      await loadAdKeywords();
      return;
    }

    if (action === "edit") {
      const res = await fetch(`/api/v1/groups/${encodeURIComponent(chatId)}/ad-keywords`);
      const data = await res.json();
      if (!res.ok) {
        print(akOutput, data);
        return;
      }
      const found = Array.isArray(data) ? data.find((item) => String(item.id) === String(keywordId)) : null;
      if (!found) {
        print(akOutput, { ok: false, message: t("rule_not_found", "Rule not found") });
        return;
      }
      akEditingKeywordId = found.id;
      if (akKeyword) akKeyword.value = found.keyword || "";
      if (akEnabled) akEnabled.checked = Boolean(found.enabled);
      if (akAddKeyword) akAddKeyword.textContent = t("ad_keyword_update", "Update Ad Rule");
      if (akCancelEdit) akCancelEdit.style.display = "";
      return;
    }

    if (action === "toggle") {
      const enabled = target.dataset.enabled === "1";
      const payload = { enabled: !enabled };
      const res = await fetch(`/api/v1/groups/${encodeURIComponent(chatId)}/ad-keywords/${encodeURIComponent(keywordId)}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      print(akOutput, data);
      if (!res.ok) return;
      await loadAdKeywords();
    }
  } catch (err) {
    print(akOutput, { ok: false, error: String(err) });
  }
});

function toEventLabel(eventType) {
  const key = `event_${eventType}`;
  if (i18n[key]) return i18n[key];
  return eventType;
}

function renderMemberEvents(items) {
  if (!evTableBody) return;
  if (!Array.isArray(items) || !items.length) {
    evTableBody.innerHTML = `<tr><td colspan="5">${escapeHtml(t("no_data", "No data"))}</td></tr>`;
    return;
  }

  evTableBody.innerHTML = items
    .map((item) => {
      const userText = item.username ? `${item.user_id} (@${item.username})` : `${item.user_id}`;
      const groupText = item.group_title ? `${item.group_title} (${item.chat_id})` : `${item.chat_id}`;
      const time = item.created_at ? new Date(item.created_at).toLocaleString() : "";
      return `<tr>
        <td>${escapeHtml(time)}</td>
        <td>${escapeHtml(groupText)}</td>
        <td>${escapeHtml(toEventLabel(item.event_type))}</td>
        <td>${escapeHtml(userText)}</td>
        <td>${escapeHtml(item.detail || "")}</td>
      </tr>`;
    })
    .join("");
}

async function loadMemberEvents() {
  const params = new URLSearchParams();
  params.set("limit", "200");
  const chatId = evChatId?.value || "";
  if (!chatId) {
    renderMemberEvents([]);
    return;
  }
  params.set("chat_id", chatId);

  try {
    const res = await fetch(`/api/v1/logs/member-events?${params.toString()}`);
    const data = await res.json();
    if (!res.ok) {
      renderMemberEvents([]);
      return;
    }
    renderMemberEvents(data);
  } catch (err) {
    renderMemberEvents([]);
  }
}

evRefresh?.addEventListener("click", async () => {
  await loadMemberEvents();
});

evChatId?.addEventListener("change", async () => {
  await loadMemberEvents();
});

pollOnlineUpdateStatus();

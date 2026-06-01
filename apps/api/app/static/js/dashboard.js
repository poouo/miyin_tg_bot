const bodyEl = document.body;
const sidebar = document.getElementById("sidebar");
const sidebarOverlay = document.getElementById("sidebar-overlay");
const workspaceEl = document.querySelector(".workspace");
const menuToggle = document.getElementById("mobile-menu-toggle");
const themeToggle = document.getElementById("theme-toggle");
const workspaceTitle = document.getElementById("workspace-title");
const actionStatus = document.getElementById("action-status");
const navItems = Array.from(document.querySelectorAll(".nav-item"));
const sections = Array.from(document.querySelectorAll(".section"));

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

const upgradeFill = document.getElementById("upgrade-fill");
const upgradeStatus = document.getElementById("upgrade-status");

const arChatId = document.getElementById("ar-chat-id");
const arOpenAdd = document.getElementById("ar-open-add");
const arRefresh = document.getElementById("ar-refresh");
const arTableBody = document.getElementById("ar-table-body");
const arModal = document.getElementById("ar-modal");
const arModalTitle = document.getElementById("ar-modal-title");
const arModalKeyword = document.getElementById("ar-modal-keyword");
const arModalReplyText = document.getElementById("ar-modal-reply-text");
const arModalParseMode = document.getElementById("ar-modal-parse-mode");
const arModalDeleteAfter = document.getElementById("ar-modal-delete-after");
const arModalEnabled = document.getElementById("ar-modal-enabled");
const arModalPreview = document.getElementById("ar-modal-preview");
const arModalSave = document.getElementById("ar-modal-save");
const arModalCancel = document.getElementById("ar-modal-cancel");
const arModalClose = document.getElementById("ar-modal-close");
const arPreviewModal = document.getElementById("ar-preview-modal");
const arPreviewContent = document.getElementById("ar-preview-content");
const arPreviewClose = document.getElementById("ar-preview-close");
const arPreviewOk = document.getElementById("ar-preview-ok");

const kwChatId = document.getElementById("kw-chat-id");
const kwOpenAdd = document.getElementById("kw-open-add");
const kwRefresh = document.getElementById("kw-refresh");
const kwTableBody = document.getElementById("kw-table-body");
const kwModal = document.getElementById("kw-modal");
const kwModalTitle = document.getElementById("kw-modal-title");
const kwModalKeyword = document.getElementById("kw-modal-keyword");
const kwModalAction = document.getElementById("kw-modal-action");
const kwModalMuteMinutes = document.getElementById("kw-modal-mute-minutes");
const kwModalEnabled = document.getElementById("kw-modal-enabled");
const kwModalSave = document.getElementById("kw-modal-save");
const kwModalCancel = document.getElementById("kw-modal-cancel");
const kwModalClose = document.getElementById("kw-modal-close");

const akChatId = document.getElementById("ak-chat-id");
const akOpenAdd = document.getElementById("ak-open-add");
const akRefresh = document.getElementById("ak-refresh");
const akTableBody = document.getElementById("ak-table-body");
const akModal = document.getElementById("ak-modal");
const akModalTitle = document.getElementById("ak-modal-title");
const akModalKeyword = document.getElementById("ak-modal-keyword");
const akModalEnabled = document.getElementById("ak-modal-enabled");
const akModalSave = document.getElementById("ak-modal-save");
const akModalCancel = document.getElementById("ak-modal-cancel");
const akModalClose = document.getElementById("ak-modal-close");

const evChatId = document.getElementById("ev-chat-id");
const evRefresh = document.getElementById("ev-refresh");
const evTableBody = document.getElementById("ev-table-body");

const logChatId = document.getElementById("log-chat-id");
const logEventType = document.getElementById("log-event-type");
const logLimit = document.getElementById("log-limit");
const logRefresh = document.getElementById("log-refresh");
const logTableBody = document.getElementById("log-table-body");

const banChatId = document.getElementById("ban-chat-id");
const banRefresh = document.getElementById("ban-refresh");
const banTableBody = document.getElementById("ban-table-body");

const cmChatId = document.getElementById("cm-chat-id");
const cmRulesText = document.getElementById("cm-rules-text");
const cmWelcomeEnabled = document.getElementById("cm-welcome-enabled");
const cmGoodbyeEnabled = document.getElementById("cm-goodbye-enabled");
const cmCleanWelcome = document.getElementById("cm-clean-welcome");
const cmWelcomeText = document.getElementById("cm-welcome-text");
const cmGoodbyeText = document.getElementById("cm-goodbye-text");
const cmWarnLimit = document.getElementById("cm-warn-limit");
const cmWarnAction = document.getElementById("cm-warn-action");
const cmWarnMuteMinutes = document.getElementById("cm-warn-mute-minutes");
const cmWarnBanMinutes = document.getElementById("cm-warn-ban-minutes");
const cmReportsEnabled = document.getElementById("cm-reports-enabled");
const cmLockLinks = document.getElementById("cm-lock-links");
const cmLockForwards = document.getElementById("cm-lock-forwards");
const cmLockMedia = document.getElementById("cm-lock-media");
const cmLockStickers = document.getElementById("cm-lock-stickers");
const cmLockCommands = document.getElementById("cm-lock-commands");
const cmLogEnabled = document.getElementById("cm-log-enabled");
const cmLogChatId = document.getElementById("cm-log-chat-id");
const cmDisabledCommands = Array.from(document.querySelectorAll(".cm-disabled-command"));
const cmSection = document.getElementById("community");
const cmSave = document.getElementById("cm-save");
const cmRefresh = document.getElementById("cm-refresh");
const cmNoteName = document.getElementById("cm-note-name");
const cmNoteParseMode = document.getElementById("cm-note-parse-mode");
const cmNoteText = document.getElementById("cm-note-text");
const cmNoteSave = document.getElementById("cm-note-save");
const cmNotesBody = document.getElementById("cm-notes-body");
const cmRssUrl = document.getElementById("cm-rss-url");
const cmRssTitle = document.getElementById("cm-rss-title");
const cmRssSave = document.getElementById("cm-rss-save");
const cmRssBody = document.getElementById("cm-rss-body");
const cmGbanUserId = document.getElementById("cm-gban-user-id");
const cmGbanReason = document.getElementById("cm-gban-reason");
const cmGbanSave = document.getElementById("cm-gban-save");
const cmGbanBody = document.getElementById("cm-gban-body");

const gsChatId = document.getElementById("gs-chat-id");
const gsJoinVerify = document.getElementById("gs-join-verify");
const gsKeywordFilter = document.getElementById("gs-keyword-filter");
const gsAdBlock = document.getElementById("gs-ad-block");
const gsAntiSpam = document.getElementById("gs-anti-spam");
const gsAutoRecover = document.getElementById("gs-auto-recover");
const gsAi = document.getElementById("gs-ai");
const gsAiReplyDeleteAfterSeconds = document.getElementById("gs-ai-reply-delete-after-seconds");
const gsJoinVerifyFailAction = document.getElementById("gs-join-verify-fail-action");
const gsJoinVerifyFailKickMinutes = document.getElementById("gs-join-verify-fail-kick-minutes");
const gsJoinVerifyFailMuteMinutes = document.getElementById("gs-join-verify-fail-mute-minutes");
const gsJoinVerifyFailBanMinutes = document.getElementById("gs-join-verify-fail-ban-minutes");
const gsAdBlockAction = document.getElementById("gs-ad-block-action");
const gsAdBlockDeleteMessage = document.getElementById("gs-ad-block-delete-message");
const gsAdBlockKickMinutes = document.getElementById("gs-ad-block-kick-minutes");
const gsAdBlockMuteMinutes = document.getElementById("gs-ad-block-mute-minutes");
const gsAdBlockBanMinutes = document.getElementById("gs-ad-block-ban-minutes");
const gsAntiSpamAction = document.getElementById("gs-anti-spam-action");
const gsAntiSpamDeleteMessage = document.getElementById("gs-anti-spam-delete-message");
const gsAntiSpamWindowSec = document.getElementById("gs-anti-spam-window-sec");
const gsAntiSpamSameTextMax = document.getElementById("gs-anti-spam-same-text-max");
const gsAntiSpamDifferentTextMax = document.getElementById("gs-anti-spam-different-text-max");
const gsAntiSpamKickMinutes = document.getElementById("gs-anti-spam-kick-minutes");
const gsAntiSpamMuteMinutes = document.getElementById("gs-anti-spam-mute-minutes");
const gsAntiSpamBanMinutes = document.getElementById("gs-anti-spam-ban-minutes");
const gsSave = document.getElementById("gs-save");
const gsRefresh = document.getElementById("gs-refresh");

const i18nEl = document.getElementById("i18n-data");
const i18n = i18nEl ? JSON.parse(i18nEl.textContent || "{}") : {};

let updatePollTimer = null;
const ACTIVE_SECTION_KEY = "miyin.dashboard.activeSection";
const THEME_KEY = "miyin.dashboard.theme";
const COMMUNITY_CHAT_KEY = "miyin.dashboard.communityChatId";
let actionStatusTimer = null;
let arEditingRuleId = null;
let kwEditingKeywordId = null;
let akEditingKeywordId = null;
const groupConfigCache = new Map();

function t(key, fallback) {
  return i18n[key] || fallback || key;
}

function escapeHtml(text) {
  return String(text || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function formatParseMode(mode) {
  const normalized = String(mode || "plain").toLowerCase();
  if (normalized === "markdownv2") return t("auto_reply_parse_mode_markdownv2", "MarkdownV2");
  if (normalized === "html") return t("auto_reply_parse_mode_html", "HTML");
  return t("auto_reply_parse_mode_plain", "Plain Text");
}

function formatReplyPreview(text, parseMode) {
  const raw = String(text || "");
  if (String(parseMode || "plain").toLowerCase() !== "html") {
    return raw;
  }
  const parser = new DOMParser();
  const doc = parser.parseFromString(raw.replace(/<br\s*\/?>/gi, "\n"), "text/html");
  return (doc.body.textContent || raw).replace(/\n{3,}/g, "\n\n").trim();
}

function sanitizeHtml(raw) {
  const template = document.createElement("template");
  template.innerHTML = raw || "";
  const blockedTags = new Set(["script", "style", "iframe", "object", "embed", "link", "meta"]);
  const walker = document.createTreeWalker(template.content, NodeFilter.SHOW_ELEMENT);
  const toRemove = [];
  while (walker.nextNode()) {
    const node = walker.currentNode;
    if (!(node instanceof Element)) continue;
    if (blockedTags.has(node.tagName.toLowerCase())) {
      toRemove.push(node);
      continue;
    }
    for (const attr of Array.from(node.attributes)) {
      const name = attr.name.toLowerCase();
      const value = attr.value.trim().toLowerCase();
      if (name.startsWith("on")) node.removeAttribute(attr.name);
      if ((name === "href" || name === "src") && value.startsWith("javascript:")) {
        node.removeAttribute(attr.name);
      }
    }
  }
  toRemove.forEach((node) => node.remove());
  return template.innerHTML;
}

function renderMarkdownV2Preview(rawText) {
  let text = escapeHtml(String(rawText || ""));
  text = text.replace(/\\([_\*\[\]\(\)~`>#+\-=|{}.!\\])/g, "$1");
  text = text.replace(/\r\n/g, "\n");
  text = text.replace(/```([\s\S]*?)```/g, "<pre><code>$1</code></pre>");
  text = text.replace(/`([^`]+?)`/g, "<code>$1</code>");
  text = text.replace(/\*\*([\s\S]+?)\*\*/g, "<strong>$1</strong>");
  text = text.replace(/\*([^\n*][\s\S]*?)\*/g, "<strong>$1</strong>");
  text = text.replace(/__([\s\S]+?)__/g, "<u>$1</u>");
  text = text.replace(/_([^\n_][\s\S]*?)_/g, "<em>$1</em>");
  text = text.replace(/~([^\n~][\s\S]*?)~/g, "<s>$1</s>");
  text = text.replace(/\|\|([\s\S]+?)\|\|/g, '<span class="preview-spoiler">$1</span>');
  text = text.replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
  text = text.replace(/\n/g, "<br>");
  return text;
}

function buildAutoReplyPreviewHtml(content, parseMode) {
  const mode = String(parseMode || "plain").toLowerCase();
  if (mode === "html") {
    return sanitizeHtml(content);
  }
  if (mode === "markdownv2") {
    return renderMarkdownV2Preview(content);
  }
  return escapeHtml(content).replace(/\n/g, "<br>");
}

function showStatus(message, isError = false) {
  if (!actionStatus) return;
  actionStatus.textContent = message || "";
  actionStatus.classList.toggle("error", Boolean(isError));
  if (actionStatusTimer) {
    window.clearTimeout(actionStatusTimer);
  }
  if (!message) return;
  actionStatusTimer = window.setTimeout(() => {
    if (!actionStatus) return;
    actionStatus.textContent = "";
    actionStatus.classList.remove("error");
  }, 2400);
}

async function requestJson(url, options = {}) {
  try {
    const res = await fetch(url, options);
    const data = await res.json();
    return { ok: res.ok, status: res.status, data };
  } catch (err) {
    return { ok: false, status: 0, data: { ok: false, error: String(err) } };
  }
}

function parseApiMessage(payload) {
  if (!payload || typeof payload !== "object") return "";
  return payload.message || payload.detail || payload.error || "";
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
    const label = active.querySelector(".nav-item-label");
    workspaceTitle.textContent = (label && label.textContent) || active.textContent || "";
  }
}

function setActiveSection(target) {
  sections.forEach((section) => {
    const active = section.id === target;
    section.classList.toggle("section-active", active);
    section.hidden = !active;
    if (active) {
      section.classList.remove("route-content-enter");
      void section.offsetWidth;
      section.classList.add("route-content-enter");
    } else {
      section.classList.remove("route-content-enter");
    }
  });
  if (workspaceEl) workspaceEl.scrollTop = 0;
}

function closeMobileSidebar() {
  bodyEl.classList.remove("sidebar-open");
  if (sidebarOverlay) sidebarOverlay.hidden = true;
}

menuToggle?.addEventListener("click", () => {
  const willOpen = !bodyEl.classList.contains("sidebar-open");
  bodyEl.classList.toggle("sidebar-open", willOpen);
  if (sidebarOverlay) sidebarOverlay.hidden = !willOpen;
});

document.addEventListener("click", (event) => {
  if (!bodyEl.classList.contains("sidebar-open")) return;
  const target = event.target;
  if (!(target instanceof Element)) return;
  if (sidebar?.contains(target) || menuToggle?.contains(target)) return;
  closeMobileSidebar();
});

sidebarOverlay?.addEventListener("click", closeMobileSidebar);

window.addEventListener("resize", () => {
  if (window.innerWidth > 900) {
    closeMobileSidebar();
  }
});

function openModal(modal) {
  if (!modal) return;
  modal.hidden = false;
  bodyEl.classList.add("modal-open");
}

function closeModal(modal) {
  if (!modal) return;
  modal.hidden = true;
  if (!document.querySelector(".modal-backdrop:not([hidden])")) {
    bodyEl.classList.remove("modal-open");
  }
}

function resetAutoReplyModal() {
  arEditingRuleId = null;
  if (arModalTitle) arModalTitle.textContent = t("auto_reply_add", "Add Auto Reply");
  if (arModalKeyword) arModalKeyword.value = "";
  if (arModalReplyText) arModalReplyText.value = "";
  if (arModalParseMode) arModalParseMode.value = "plain";
  if (arModalDeleteAfter) arModalDeleteAfter.value = "0";
  if (arModalEnabled) arModalEnabled.checked = true;
}

function resetKeywordModal() {
  kwEditingKeywordId = null;
  if (kwModalTitle) kwModalTitle.textContent = t("keyword_add", "Add Keyword Rule");
  if (kwModalKeyword) kwModalKeyword.value = "";
  if (kwModalAction) kwModalAction.value = "delete";
  if (kwModalMuteMinutes) kwModalMuteMinutes.value = "10";
  if (kwModalEnabled) kwModalEnabled.checked = true;
}

function resetAdKeywordModal() {
  akEditingKeywordId = null;
  if (akModalTitle) akModalTitle.textContent = t("ad_keyword_add", "Add Ad Keyword");
  if (akModalKeyword) akModalKeyword.value = "";
  if (akModalEnabled) akModalEnabled.checked = true;
}

function renderAutoReplies(items) {
  if (!arTableBody) return;
  if (!Array.isArray(items) || !items.length) {
    arTableBody.innerHTML = `<tr><td colspan="6">${escapeHtml(t("no_data", "No data"))}</td></tr>`;
    return;
  }

  arTableBody.innerHTML = items
    .map((item) => {
      const statusText = item.enabled ? t("switch_on", "on") : t("switch_off", "off");
      const toggleText = item.enabled ? t("disable", "Disable") : t("enable", "Enable");
      const replyPreview = formatReplyPreview(item.reply_text, item.parse_mode);
      return `<tr>
        <td><div class="cell-keyword">${escapeHtml(item.keyword)}</div></td>
        <td><div class="cell-reply">${escapeHtml(replyPreview)}</div></td>
        <td><div class="cell-center">${escapeHtml(formatParseMode(item.parse_mode))}</div></td>
        <td><div class="cell-center">${Number(item.delete_after_seconds || 0)}</div></td>
        <td><div class="cell-center">${escapeHtml(statusText)}</div></td>
        <td>
          <div class="row-actions">
            <button class="table-btn" type="button" data-action="edit" data-id="${item.id}">${escapeHtml(t("edit", "Edit"))}</button>
            <button class="table-btn" type="button" data-action="toggle" data-id="${item.id}" data-enabled="${item.enabled ? 1 : 0}">${escapeHtml(toggleText)}</button>
            <button class="table-btn warning" type="button" data-action="delete" data-id="${item.id}">${escapeHtml(t("delete", "Delete"))}</button>
          </div>
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
  const result = await requestJson(`/api/v1/groups/${encodeURIComponent(arChatId.value)}/auto-replies`);
  if (!result.ok) {
    showStatus(parseApiMessage(result.data) || t("operation_failed"), true);
    renderAutoReplies([]);
    return;
  }
  renderAutoReplies(result.data);
}

function formatKeywordAction(action) {
  return action === "mute" ? t("action_mute", "Mute") : t("action_delete", "Delete message");
}

function renderKeywords(items) {
  if (!kwTableBody) return;
  if (!Array.isArray(items) || !items.length) {
    kwTableBody.innerHTML = `<tr><td colspan="5">${escapeHtml(t("no_data", "No data"))}</td></tr>`;
    return;
  }

  kwTableBody.innerHTML = items
    .map((item) => {
      const statusText = item.enabled ? t("switch_on", "on") : t("switch_off", "off");
      const toggleText = item.enabled ? t("disable", "Disable") : t("enable", "Enable");
      return `<tr>
        <td><div class="cell-keyword">${escapeHtml(item.keyword)}</div></td>
        <td><div class="cell-center">${escapeHtml(formatKeywordAction(item.action))}</div></td>
        <td><div class="cell-center">${Number(item.mute_minutes || 10)}</div></td>
        <td><div class="cell-center">${escapeHtml(statusText)}</div></td>
        <td>
          <div class="row-actions">
            <button class="table-btn" type="button" data-action="edit" data-id="${item.id}">${escapeHtml(t("edit", "Edit"))}</button>
            <button class="table-btn" type="button" data-action="toggle" data-id="${item.id}" data-enabled="${item.enabled ? 1 : 0}">${escapeHtml(toggleText)}</button>
            <button class="table-btn warning" type="button" data-action="delete" data-id="${item.id}">${escapeHtml(t("delete", "Delete"))}</button>
          </div>
        </td>
      </tr>`;
    })
    .join("");
}

async function loadKeywords() {
  if (!kwChatId?.value) {
    renderKeywords([]);
    return;
  }
  const result = await requestJson(`/api/v1/groups/${encodeURIComponent(kwChatId.value)}/keywords`);
  if (!result.ok) {
    showStatus(parseApiMessage(result.data) || t("operation_failed"), true);
    renderKeywords([]);
    return;
  }
  renderKeywords(result.data);
}

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
        <td><div class="cell-keyword">${escapeHtml(item.keyword)}</div></td>
        <td><div class="cell-center">${escapeHtml(statusText)}</div></td>
        <td>
          <div class="row-actions">
            <button class="table-btn" type="button" data-action="edit" data-id="${item.id}">${escapeHtml(t("edit", "Edit"))}</button>
            <button class="table-btn" type="button" data-action="toggle" data-id="${item.id}" data-enabled="${item.enabled ? 1 : 0}">${escapeHtml(toggleText)}</button>
            <button class="table-btn warning" type="button" data-action="delete" data-id="${item.id}">${escapeHtml(t("delete", "Delete"))}</button>
          </div>
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
  const result = await requestJson(`/api/v1/groups/${encodeURIComponent(akChatId.value)}/ad-keywords`);
  if (!result.ok) {
    showStatus(parseApiMessage(result.data) || t("operation_failed"), true);
    renderAdKeywords([]);
    return;
  }
  renderAdKeywords(result.data);
}

function toEventLabel(eventType) {
  const key = `event_${eventType}`;
  return i18n[key] || eventType;
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

function formatLogUser(item) {
  if (!item.user_id) return "";
  return item.username ? `${item.user_id} (@${item.username})` : `${item.user_id}`;
}

function parseLogDetail(detail) {
  const result = { reason: "", message: "", raw: detail || "" };
  for (const line of String(detail || "").split(/\r?\n/)) {
    if (line.startsWith("reason=")) {
      result.reason = line.slice("reason=".length);
    } else if (line.startsWith("message=")) {
      result.message = line.slice("message=".length);
    }
  }
  return result;
}

function renderLogDetail(item) {
  const detail = item.detail || "";
  if (item.event_type === "message_blocked") {
    const parsed = parseLogDetail(detail);
    const reason = parsed.reason || parsed.raw;
    const lines = [`<div class="log-detail-line"><strong>${escapeHtml(t("log_action_blocked", "Blocked"))}</strong>${reason ? `: ${escapeHtml(reason)}` : ""}</div>`];
    if (parsed.message) {
      lines.push(`<div class="log-message-text">${escapeHtml(parsed.message)}</div>`);
    }
    return lines.join("");
  }
  if (item.event_type === "lock_deleted") {
    return `<div class="log-detail-line"><strong>${escapeHtml(t("log_action_deleted", "Deleted"))}</strong>${detail ? `: ${escapeHtml(detail)}` : ""}</div>`;
  }
  if (item.event_type === "auto_reply_triggered") {
    return detail ? `<div class="log-detail-line"><strong>${escapeHtml(t("auto_reply_keyword", "Trigger keyword"))}</strong>: ${escapeHtml(detail)}</div>` : "";
  }
  return escapeHtml(detail);
}

function renderModerationLogs(items) {
  if (!logTableBody) return;
  if (!Array.isArray(items) || !items.length) {
    logTableBody.innerHTML = `<tr><td colspan="5">${escapeHtml(t("no_data", "No data"))}</td></tr>`;
    return;
  }
  logTableBody.innerHTML = items
    .map((item) => {
      const groupText = item.group_title ? `${item.group_title} (${item.chat_id})` : `${item.chat_id}`;
      const time = item.created_at ? new Date(item.created_at).toLocaleString() : "";
      return `<tr>
        <td>${escapeHtml(time)}</td>
        <td>${escapeHtml(groupText)}</td>
        <td>${escapeHtml(toEventLabel(item.event_type))}</td>
        <td>${escapeHtml(formatLogUser(item))}</td>
        <td>${renderLogDetail(item)}</td>
      </tr>`;
    })
    .join("");
}

async function loadModerationLogs() {
  const params = new URLSearchParams();
  params.set("limit", String(Number(logLimit?.value || 200)));
  if (logChatId?.value) params.set("chat_id", logChatId.value);
  if (logEventType?.value) params.set("event_type", logEventType.value);
  const result = await requestJson(`/api/v1/logs/recent?${params.toString()}`);
  if (!result.ok) {
    showStatus(parseApiMessage(result.data) || t("operation_failed"), true);
    renderModerationLogs([]);
    return;
  }
  renderModerationLogs(result.data);
}

async function loadMemberEvents() {
  if (!evChatId?.value) {
    renderMemberEvents([]);
    return;
  }
  const params = new URLSearchParams();
  params.set("limit", "200");
  params.set("chat_id", evChatId.value);
  const result = await requestJson(`/api/v1/logs/member-events?${params.toString()}`);
  if (!result.ok) {
    renderMemberEvents([]);
    return;
  }
  renderMemberEvents(result.data);
}

function applyTheme(theme) {
  const isDark = theme === "dark";
  bodyEl.classList.toggle("dark", isDark);
  if (!themeToggle) return;
  const icon = themeToggle.querySelector("i");
  const label = themeToggle.querySelector("span");
  if (icon) icon.className = isDark ? "ri-sun-line" : "ri-moon-line";
  if (label) label.textContent = isDark ? t("theme_light", "Light mode") : t("theme_dark", "Dark mode");
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
    // ignore
  }
});

function renderBans(items) {
  if (!banTableBody) return;
  if (!Array.isArray(items) || !items.length) {
    banTableBody.innerHTML = `<tr><td colspan="5">${escapeHtml(t("no_data", "No data"))}</td></tr>`;
    return;
  }
  banTableBody.innerHTML = items
    .map((item) => {
      const groupText = item.group_title ? `${item.group_title} (${item.chat_id})` : `${item.chat_id}`;
      const expiresAt = item.expires_at ? new Date(item.expires_at).toLocaleString() : "";
      return `<tr>
        <td>${escapeHtml(groupText)}</td>
        <td>${escapeHtml(String(item.user_id || ""))}</td>
        <td>${escapeHtml(item.reason || "")}</td>
        <td>${escapeHtml(expiresAt)}</td>
        <td>
          <button class="table-btn" type="button" data-action="unban" data-chat-id="${item.chat_id}" data-user-id="${item.user_id}">
            ${escapeHtml(t("unban", "Unban"))}
          </button>
        </td>
      </tr>`;
    })
    .join("");
}

async function loadBans() {
  const params = new URLSearchParams();
  if (banChatId?.value) params.set("chat_id", banChatId.value);
  const query = params.toString();
  const result = await requestJson(`/api/v1/sanctions/bans${query ? `?${query}` : ""}`);
  if (!result.ok) {
    showStatus(parseApiMessage(result.data) || t("operation_failed"), true);
    renderBans([]);
    return;
  }
  renderBans(result.data);
}

function getCommunityChatId() {
  return cmChatId?.value || "";
}

function rememberCommunityChatId() {
  const chatId = getCommunityChatId();
  if (!chatId) return;
  try {
    window.localStorage.setItem(COMMUNITY_CHAT_KEY, chatId);
  } catch (err) {
    // ignore
  }
}

function restoreCommunityChatId() {
  if (!cmChatId) return;
  try {
    const stored = window.localStorage.getItem(COMMUNITY_CHAT_KEY) || "";
    if (stored && Array.from(cmChatId.options).some((option) => option.value === stored)) {
      cmChatId.value = stored;
    }
  } catch (err) {
    // ignore
  }
}

function applyCommunityConfig(config) {
  if (!config) return;
  if (cmRulesText) cmRulesText.value = config.rules_text || "";
  if (cmWelcomeEnabled) cmWelcomeEnabled.checked = Boolean(config.welcome_enabled);
  if (cmGoodbyeEnabled) cmGoodbyeEnabled.checked = Boolean(config.goodbye_enabled);
  if (cmCleanWelcome) cmCleanWelcome.checked = Boolean(config.clean_welcome);
  if (cmWelcomeText) cmWelcomeText.value = config.welcome_text || "";
  if (cmGoodbyeText) cmGoodbyeText.value = config.goodbye_text || "";
  if (cmWarnLimit) cmWarnLimit.value = String(Number(config.warn_limit || 3));
  if (cmWarnAction) cmWarnAction.value = config.warn_action || "mute";
  if (cmWarnMuteMinutes) cmWarnMuteMinutes.value = String(Number(config.warn_mute_minutes || 60));
  if (cmWarnBanMinutes) cmWarnBanMinutes.value = String(Number(config.warn_ban_minutes || 1440));
  if (cmReportsEnabled) cmReportsEnabled.checked = Boolean(config.reports_enabled);
  if (cmLockLinks) cmLockLinks.checked = Boolean(config.lock_links);
  if (cmLockForwards) cmLockForwards.checked = Boolean(config.lock_forwards);
  if (cmLockMedia) cmLockMedia.checked = Boolean(config.lock_media);
  if (cmLockStickers) cmLockStickers.checked = Boolean(config.lock_stickers);
  if (cmLockCommands) cmLockCommands.checked = Boolean(config.lock_commands);
  if (cmLogEnabled) cmLogEnabled.checked = Boolean(config.log_enabled);
  if (cmLogChatId) cmLogChatId.value = String(Number(config.log_chat_id || 0));
  const disabled = new Set(Array.isArray(config.disabled_commands) ? config.disabled_commands : []);
  cmDisabledCommands.forEach((input) => {
    input.checked = disabled.has(input.value);
  });
}

async function loadCommunityConfig() {
  const chatId = getCommunityChatId();
  if (!chatId) return;
  rememberCommunityChatId();
  const result = await requestJson(`/api/v1/community/${encodeURIComponent(chatId)}`);
  if (!result.ok) {
    showStatus(parseApiMessage(result.data) || t("operation_failed"), true);
    return;
  }
  applyCommunityConfig(result.data);
  await Promise.all([loadCommunityNotes(), loadCommunityRss(), loadGlobalBans()]);
}

function buildCommunityPayload() {
  return {
    rules_text: cmRulesText?.value || "",
    welcome_enabled: Boolean(cmWelcomeEnabled?.checked),
    goodbye_enabled: Boolean(cmGoodbyeEnabled?.checked),
    clean_welcome: Boolean(cmCleanWelcome?.checked),
    welcome_text: cmWelcomeText?.value || "",
    goodbye_text: cmGoodbyeText?.value || "",
    warn_limit: Number(cmWarnLimit?.value || 3),
    warn_action: cmWarnAction?.value || "mute",
    warn_mute_minutes: Number(cmWarnMuteMinutes?.value || 60),
    warn_ban_minutes: Number(cmWarnBanMinutes?.value || 1440),
    reports_enabled: Boolean(cmReportsEnabled?.checked),
    lock_links: Boolean(cmLockLinks?.checked),
    lock_forwards: Boolean(cmLockForwards?.checked),
    lock_media: Boolean(cmLockMedia?.checked),
    lock_stickers: Boolean(cmLockStickers?.checked),
    lock_commands: Boolean(cmLockCommands?.checked),
    log_enabled: Boolean(cmLogEnabled?.checked),
    log_chat_id: Number(cmLogChatId?.value || 0),
    disabled_commands: cmDisabledCommands.filter((input) => input.checked).map((input) => input.value),
  };
}

async function saveCommunityConfig() {
  const chatId = getCommunityChatId();
  if (!chatId) {
    showStatus(t("select_group"), true);
    return;
  }
  const result = await requestJson(`/api/v1/community/${encodeURIComponent(chatId)}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(buildCommunityPayload()),
  });
  if (!result.ok) {
    showStatus(parseApiMessage(result.data) || t("operation_failed"), true);
    return;
  }
  await loadCommunityConfig();
  showStatus(t("saved"), false);
}

function renderCommunityNotes(items) {
  if (!cmNotesBody) return;
  if (!Array.isArray(items) || !items.length) {
    cmNotesBody.innerHTML = `<tr><td colspan="3">${escapeHtml(t("no_data", "No data"))}</td></tr>`;
    return;
  }
  cmNotesBody.innerHTML = items
    .map(
      (item) => `<tr>
        <td>${escapeHtml(item.name)}</td>
        <td>${escapeHtml(formatParseMode(item.parse_mode))}</td>
        <td><button class="table-btn warning" type="button" data-action="delete-note" data-name="${escapeHtml(item.name)}">${escapeHtml(t("delete", "Delete"))}</button></td>
      </tr>`,
    )
    .join("");
}

async function loadCommunityNotes() {
  const chatId = getCommunityChatId();
  if (!chatId) {
    renderCommunityNotes([]);
    return;
  }
  const result = await requestJson(`/api/v1/community/${encodeURIComponent(chatId)}/notes`);
  renderCommunityNotes(result.ok ? result.data : []);
}

async function saveCommunityNote() {
  const chatId = getCommunityChatId();
  const payload = {
    name: (cmNoteName?.value || "").trim(),
    text: (cmNoteText?.value || "").trim(),
    parse_mode: (cmNoteParseMode?.value || "plain").toLowerCase(),
  };
  if (!chatId || !payload.name || !payload.text) {
    showStatus(t("fill_required_fields"), true);
    return;
  }
  const result = await requestJson(`/api/v1/community/${encodeURIComponent(chatId)}/notes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!result.ok) {
    showStatus(parseApiMessage(result.data) || t("operation_failed"), true);
    return;
  }
  if (cmNoteName) cmNoteName.value = "";
  if (cmNoteText) cmNoteText.value = "";
  showStatus(t("saved"), false);
  await loadCommunityNotes();
}

function renderCommunityRss(items) {
  if (!cmRssBody) return;
  if (!Array.isArray(items) || !items.length) {
    cmRssBody.innerHTML = `<tr><td colspan="3">${escapeHtml(t("no_data", "No data"))}</td></tr>`;
    return;
  }
  cmRssBody.innerHTML = items
    .map(
      (item) => `<tr>
        <td>${escapeHtml(item.title || "-")}</td>
        <td><div class="cell-reply">${escapeHtml(item.url)}</div></td>
        <td><button class="table-btn warning" type="button" data-action="delete-rss" data-url="${escapeHtml(item.url)}">${escapeHtml(t("delete", "Delete"))}</button></td>
      </tr>`,
    )
    .join("");
}

async function loadCommunityRss() {
  const chatId = getCommunityChatId();
  if (!chatId) {
    renderCommunityRss([]);
    return;
  }
  const result = await requestJson(`/api/v1/community/${encodeURIComponent(chatId)}/rss`);
  renderCommunityRss(result.ok ? result.data : []);
}

async function saveCommunityRss() {
  const chatId = getCommunityChatId();
  const payload = {
    url: (cmRssUrl?.value || "").trim(),
    title: (cmRssTitle?.value || "").trim(),
  };
  if (!chatId || !payload.url) {
    showStatus(t("fill_required_fields"), true);
    return;
  }
  const result = await requestJson(`/api/v1/community/${encodeURIComponent(chatId)}/rss`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!result.ok) {
    showStatus(parseApiMessage(result.data) || t("operation_failed"), true);
    return;
  }
  if (cmRssUrl) cmRssUrl.value = "";
  if (cmRssTitle) cmRssTitle.value = "";
  showStatus(t("saved"), false);
  await loadCommunityRss();
}

function renderGlobalBans(items) {
  if (!cmGbanBody) return;
  if (!Array.isArray(items) || !items.length) {
    cmGbanBody.innerHTML = `<tr><td colspan="3">${escapeHtml(t("no_data", "No data"))}</td></tr>`;
    return;
  }
  cmGbanBody.innerHTML = items
    .map(
      (item) => `<tr>
        <td>${escapeHtml(String(item.user_id || ""))}</td>
        <td>${escapeHtml(item.reason || "")}</td>
        <td><button class="table-btn" type="button" data-action="delete-gban" data-user-id="${item.user_id}">${escapeHtml(t("unban", "Unban"))}</button></td>
      </tr>`,
    )
    .join("");
}

async function loadGlobalBans() {
  const result = await requestJson("/api/v1/community/global-bans/list");
  renderGlobalBans(result.ok ? result.data : []);
}

async function saveGlobalBan() {
  const payload = {
    user_id: Number(cmGbanUserId?.value || 0),
    reason: (cmGbanReason?.value || "").trim(),
  };
  if (!payload.user_id) {
    showStatus(t("fill_required_fields"), true);
    return;
  }
  const result = await requestJson("/api/v1/community/global-bans", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!result.ok) {
    showStatus(parseApiMessage(result.data) || t("operation_failed"), true);
    return;
  }
  if (cmGbanUserId) cmGbanUserId.value = "";
  if (cmGbanReason) cmGbanReason.value = "";
  showStatus(t("saved"), false);
  await loadGlobalBans();
}

function applyGroupSettings(chatIdValue) {
  const chatId = Number(chatIdValue || 0);
  const config = groupConfigCache.get(chatId);
  if (!config) return;
  if (gsJoinVerify) gsJoinVerify.checked = Boolean(config.join_verification_enabled);
  if (gsKeywordFilter) gsKeywordFilter.checked = Boolean(config.keyword_filter_enabled);
  if (gsAdBlock) gsAdBlock.checked = Boolean(config.ad_block_enabled);
  if (gsAntiSpam) gsAntiSpam.checked = Boolean(config.anti_spam_enabled);
  if (gsAutoRecover) gsAutoRecover.checked = Boolean(config.auto_recover_enabled);
  if (gsAi) gsAi.checked = Boolean(config.deepseek_enabled);
  if (gsAiReplyDeleteAfterSeconds) {
    gsAiReplyDeleteAfterSeconds.value = String(Number(config.ai_reply_delete_after_seconds || 0));
  }
  if (gsJoinVerifyFailAction) gsJoinVerifyFailAction.value = config.join_verify_fail_action || "kick";
  if (gsJoinVerifyFailKickMinutes) gsJoinVerifyFailKickMinutes.value = String(Number(config.join_verify_fail_kick_minutes || 1));
  if (gsJoinVerifyFailMuteMinutes) gsJoinVerifyFailMuteMinutes.value = String(Number(config.join_verify_fail_mute_minutes || 30));
  if (gsJoinVerifyFailBanMinutes) gsJoinVerifyFailBanMinutes.value = String(Number(config.join_verify_fail_ban_minutes || 1440));
  if (gsAdBlockAction) gsAdBlockAction.value = config.ad_block_action || "mute";
  if (gsAdBlockDeleteMessage) gsAdBlockDeleteMessage.checked = config.ad_block_delete_message !== false;
  if (gsAdBlockKickMinutes) gsAdBlockKickMinutes.value = String(Number(config.ad_block_kick_minutes || 1));
  if (gsAdBlockMuteMinutes) gsAdBlockMuteMinutes.value = String(Number(config.ad_block_mute_minutes || 30));
  if (gsAdBlockBanMinutes) gsAdBlockBanMinutes.value = String(Number(config.ad_block_ban_minutes || 1440));
  if (gsAntiSpamAction) gsAntiSpamAction.value = config.anti_spam_action || "mute";
  if (gsAntiSpamDeleteMessage) gsAntiSpamDeleteMessage.checked = config.anti_spam_delete_message !== false;
  if (gsAntiSpamWindowSec) gsAntiSpamWindowSec.value = String(Number(config.anti_spam_window_sec || 10));
  if (gsAntiSpamSameTextMax) gsAntiSpamSameTextMax.value = String(Number(config.anti_spam_same_text_max || 3));
  if (gsAntiSpamDifferentTextMax) gsAntiSpamDifferentTextMax.value = String(Number(config.anti_spam_different_text_max || 6));
  if (gsAntiSpamKickMinutes) gsAntiSpamKickMinutes.value = String(Number(config.anti_spam_kick_minutes || 1));
  if (gsAntiSpamMuteMinutes) gsAntiSpamMuteMinutes.value = String(Number(config.anti_spam_mute_minutes || 30));
  if (gsAntiSpamBanMinutes) gsAntiSpamBanMinutes.value = String(Number(config.anti_spam_ban_minutes || 1440));
}

async function loadGroupConfigs() {
  const result = await requestJson("/api/v1/groups");
  if (!result.ok || !Array.isArray(result.data)) {
    showStatus(parseApiMessage(result.data) || t("operation_failed"), true);
    return;
  }
  groupConfigCache.clear();
  for (const item of result.data) {
    groupConfigCache.set(Number(item.chat_id), item);
  }
  applyGroupSettings(gsChatId?.value || "");
}

async function saveGroupSettings() {
  const chatId = gsChatId?.value || "";
  if (!chatId) {
    showStatus(t("select_group"), true);
    return;
  }
  const payload = {
    join_verification_enabled: Boolean(gsJoinVerify?.checked),
    keyword_filter_enabled: Boolean(gsKeywordFilter?.checked),
    ad_block_enabled: Boolean(gsAdBlock?.checked),
    anti_spam_enabled: Boolean(gsAntiSpam?.checked),
    auto_recover_enabled: Boolean(gsAutoRecover?.checked),
    deepseek_enabled: Boolean(gsAi?.checked),
    ai_reply_delete_after_seconds: Number(gsAiReplyDeleteAfterSeconds?.value || 0),
    join_verify_fail_action: gsJoinVerifyFailAction?.value || "kick",
    join_verify_fail_kick_minutes: Number(gsJoinVerifyFailKickMinutes?.value || 1),
    join_verify_fail_mute_minutes: Number(gsJoinVerifyFailMuteMinutes?.value || 30),
    join_verify_fail_ban_minutes: Number(gsJoinVerifyFailBanMinutes?.value || 1440),
    ad_block_action: gsAdBlockAction?.value || "mute",
    ad_block_delete_message: Boolean(gsAdBlockDeleteMessage?.checked),
    ad_block_kick_minutes: Number(gsAdBlockKickMinutes?.value || 1),
    ad_block_mute_minutes: Number(gsAdBlockMuteMinutes?.value || 30),
    ad_block_ban_minutes: Number(gsAdBlockBanMinutes?.value || 1440),
    anti_spam_action: gsAntiSpamAction?.value || "mute",
    anti_spam_delete_message: Boolean(gsAntiSpamDeleteMessage?.checked),
    anti_spam_window_sec: Number(gsAntiSpamWindowSec?.value || 10),
    anti_spam_same_text_max: Number(gsAntiSpamSameTextMax?.value || 3),
    anti_spam_different_text_max: Number(gsAntiSpamDifferentTextMax?.value || 6),
    anti_spam_kick_minutes: Number(gsAntiSpamKickMinutes?.value || 1),
    anti_spam_mute_minutes: Number(gsAntiSpamMuteMinutes?.value || 30),
    anti_spam_ban_minutes: Number(gsAntiSpamBanMinutes?.value || 1440),
  };
  const result = await requestJson(`/api/v1/groups/${encodeURIComponent(chatId)}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!result.ok) {
    showStatus(parseApiMessage(result.data) || t("operation_failed"), true);
    return;
  }
  groupConfigCache.set(Number(chatId), result.data);
  showStatus(t("saved"), false);
}

async function handleSectionEnter(target) {
  if (target === "auto-replies") {
    await loadAutoReplies();
  } else if (target === "keywords") {
    await loadKeywords();
  } else if (target === "ad-keywords") {
    await loadAdKeywords();
  } else if (target === "member-events") {
    await loadMemberEvents();
  } else if (target === "moderation-logs") {
    await loadModerationLogs();
  } else if (target === "bans") {
    await loadBans();
  } else if (target === "community") {
    await loadCommunityConfig();
  } else if (target === "group-settings") {
    await loadGroupConfigs();
  }
}

navItems.forEach((item) => {
  item.addEventListener("click", async () => {
    const target = item.dataset.target;
    if (!target) return;
    if (!document.getElementById(target)) return;
    setActiveNav(target);
    setActiveSection(target);
    try {
      window.localStorage.setItem(ACTIVE_SECTION_KEY, target);
    } catch (err) {
      // ignore
    }
    if (workspaceEl) workspaceEl.scrollTop = 0;
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
restoreCommunityChatId();
handleSectionEnter(initialTarget);

async function pollOnlineUpdateStatus() {
  const result = await requestJson("/api/v1/updates/online-status");
  if (!result.ok || !result.data?.ok) {
    setUpgradeStatus(0, t("update_status_load_failed"), "failed");
    stopPolling();
    if (btnTrigger) btnTrigger.disabled = false;
    return;
  }

  const state = result.data.state || "idle";
  const progress = result.data.progress || 0;
  const message = result.data.message || t("update_status_working");

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
  const result = await requestJson("/api/v1/updates/check");
  if (!result.ok || !result.data?.ok) {
    setUpgradeStatus(0, t("update_check_failed"), "failed");
    return;
  }
  if (result.data.has_update) {
    setUpgradeStatus(0, t("update_available_click"));
  } else {
    setUpgradeStatus(100, t("update_uptodate"), "success");
  }
});

btnTrigger?.addEventListener("click", async () => {
  if (btnTrigger) btnTrigger.disabled = true;
  setUpgradeStatus(2, t("update_starting"));
  const result = await requestJson("/api/v1/updates/online", { method: "POST" });
  if (!result.ok || !result.data?.ok) {
    setUpgradeStatus(0, parseApiMessage(result.data) || t("update_start_failed"), "failed");
    if (btnTrigger) btnTrigger.disabled = false;
    return;
  }
  startPolling();
  await pollOnlineUpdateStatus();
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
  };
}

async function saveRuntime() {
  const result = await requestJson("/api/v1/runtime", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(buildRuntimePayload()),
  });
  if (!result.ok) {
    showStatus(parseApiMessage(result.data) || t("operation_failed"), true);
    return;
  }
  showStatus(t("saved"), false);
}

btnSaveRuntime?.addEventListener("click", saveRuntime);
btnSaveDeepseek?.addEventListener("click", saveRuntime);

btnSaveSecurity?.addEventListener("click", async () => {
  const payload = {
    login_ban_enabled: Boolean(loginBanEnabled?.checked),
    login_max_attempts: Number(loginMaxAttempts?.value || 5),
    login_ban_minutes: Number(loginBanMinutes?.value || 5),
    web_language: (webLanguage?.value || "zh").toLowerCase(),
  };
  const result = await requestJson("/api/v1/security/login", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!result.ok) {
    showStatus(parseApiMessage(result.data) || t("operation_failed"), true);
    return;
  }
  showStatus(t("saved"), false);
  if (result.data.web_language) {
    setTimeout(() => window.location.reload(), 300);
  }
});

btnSavePassword?.addEventListener("click", async () => {
  const payload = {
    current_password: currentPassword?.value || "",
    new_password: newPassword?.value || "",
    confirm_password: confirmPassword?.value || "",
  };
  const result = await requestJson("/api/v1/security/password", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!result.ok) {
    showStatus(`${t("password_change_failed")}: ${parseApiMessage(result.data)}`, true);
    return;
  }
  if (currentPassword) currentPassword.value = "";
  if (newPassword) newPassword.value = "";
  if (confirmPassword) confirmPassword.value = "";
  showStatus(t("password_changed"), false);
});

arOpenAdd?.addEventListener("click", () => {
  resetAutoReplyModal();
  openModal(arModal);
});

function openAutoReplyPreview() {
  const content = arModalReplyText?.value || "";
  const parseMode = (arModalParseMode?.value || "plain").toLowerCase();
  if (!content.trim()) {
    showStatus(t("fill_required_fields"), true);
    return;
  }
  if (arPreviewContent) {
    arPreviewContent.innerHTML = buildAutoReplyPreviewHtml(content, parseMode);
  }
  openModal(arPreviewModal);
}

arModalPreview?.addEventListener("click", openAutoReplyPreview);

arModalCancel?.addEventListener("click", () => closeModal(arModal));
arModalClose?.addEventListener("click", () => closeModal(arModal));
arModal?.addEventListener("click", (event) => {
  if (event.target === arModal) closeModal(arModal);
});
arPreviewClose?.addEventListener("click", () => closeModal(arPreviewModal));
arPreviewOk?.addEventListener("click", () => closeModal(arPreviewModal));
arPreviewModal?.addEventListener("click", (event) => {
  if (event.target === arPreviewModal) closeModal(arPreviewModal);
});

arModalSave?.addEventListener("click", async () => {
  const chatId = arChatId?.value || "";
  if (!chatId) {
    showStatus(t("select_group"), true);
    return;
  }
  const payload = {
    chat_id: Number(chatId),
    keyword: (arModalKeyword?.value || "").trim(),
    reply_text: (arModalReplyText?.value || "").trim(),
    parse_mode: (arModalParseMode?.value || "plain").toLowerCase(),
    delete_after_seconds: Number(arModalDeleteAfter?.value || 0),
    enabled: Boolean(arModalEnabled?.checked),
  };
  if (!payload.keyword || !payload.reply_text) {
    showStatus(t("fill_required_fields"), true);
    return;
  }

  const isEditing = arEditingRuleId !== null;
  const url = isEditing
    ? `/api/v1/groups/${encodeURIComponent(chatId)}/auto-replies/${encodeURIComponent(String(arEditingRuleId))}`
    : `/api/v1/groups/${encodeURIComponent(chatId)}/auto-replies`;
  const method = isEditing ? "PATCH" : "POST";
  const bodyPayload = isEditing
      ? {
        keyword: payload.keyword,
        reply_text: payload.reply_text,
        parse_mode: payload.parse_mode,
        delete_after_seconds: payload.delete_after_seconds,
        enabled: payload.enabled,
      }
    : payload;
  const result = await requestJson(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(bodyPayload),
  });
  if (!result.ok) {
    showStatus(parseApiMessage(result.data) || t("operation_failed"), true);
    return;
  }
  closeModal(arModal);
  showStatus(t("saved"), false);
  await loadAutoReplies();
});

arRefresh?.addEventListener("click", loadAutoReplies);
arChatId?.addEventListener("change", loadAutoReplies);

arTableBody?.addEventListener("click", async (event) => {
  const target = event.target;
  if (!(target instanceof HTMLButtonElement)) return;
  const action = target.dataset.action || "";
  const ruleId = target.dataset.id || "";
  const chatId = arChatId?.value || "";
  if (!action || !ruleId || !chatId) return;

  if (action === "delete") {
    const result = await requestJson(
      `/api/v1/groups/${encodeURIComponent(chatId)}/auto-replies/${encodeURIComponent(ruleId)}`,
      { method: "DELETE" },
    );
    if (!result.ok) {
      showStatus(parseApiMessage(result.data) || t("operation_failed"), true);
      return;
    }
    showStatus(t("saved"), false);
    await loadAutoReplies();
    return;
  }

  if (action === "toggle") {
    const enabled = target.dataset.enabled === "1";
    const result = await requestJson(
      `/api/v1/groups/${encodeURIComponent(chatId)}/auto-replies/${encodeURIComponent(ruleId)}`,
      {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ enabled: !enabled }),
      },
    );
    if (!result.ok) {
      showStatus(parseApiMessage(result.data) || t("operation_failed"), true);
      return;
    }
    showStatus(t("saved"), false);
    await loadAutoReplies();
    return;
  }

  if (action === "edit") {
    const result = await requestJson(`/api/v1/groups/${encodeURIComponent(chatId)}/auto-replies`);
    if (!result.ok || !Array.isArray(result.data)) {
      showStatus(parseApiMessage(result.data) || t("operation_failed"), true);
      return;
    }
    const found = result.data.find((item) => String(item.id) === String(ruleId));
    if (!found) {
      showStatus(t("rule_not_found"), true);
      return;
    }
    arEditingRuleId = found.id;
    if (arModalTitle) arModalTitle.textContent = t("auto_reply_update", "Update Rule");
    if (arModalKeyword) arModalKeyword.value = found.keyword || "";
    if (arModalReplyText) arModalReplyText.value = found.reply_text || "";
    if (arModalParseMode) arModalParseMode.value = (found.parse_mode || "plain").toLowerCase();
    if (arModalDeleteAfter) arModalDeleteAfter.value = String(Number(found.delete_after_seconds || 0));
    if (arModalEnabled) arModalEnabled.checked = Boolean(found.enabled);
    openModal(arModal);
  }
});

kwOpenAdd?.addEventListener("click", () => {
  resetKeywordModal();
  openModal(kwModal);
});

kwModalCancel?.addEventListener("click", () => closeModal(kwModal));
kwModalClose?.addEventListener("click", () => closeModal(kwModal));
kwModal?.addEventListener("click", (event) => {
  if (event.target === kwModal) closeModal(kwModal);
});

kwModalSave?.addEventListener("click", async () => {
  const chatId = kwChatId?.value || "";
  if (!chatId) {
    showStatus(t("select_group"), true);
    return;
  }
  const payload = {
    chat_id: Number(chatId),
    keyword: (kwModalKeyword?.value || "").trim(),
    action: kwModalAction?.value || "delete",
    mute_minutes: Number(kwModalMuteMinutes?.value || 10),
    enabled: Boolean(kwModalEnabled?.checked),
  };
  if (!payload.keyword) {
    showStatus(t("fill_required_fields"), true);
    return;
  }

  const isEditing = kwEditingKeywordId !== null;
  const url = isEditing
    ? `/api/v1/groups/${encodeURIComponent(chatId)}/keywords/${encodeURIComponent(String(kwEditingKeywordId))}`
    : `/api/v1/groups/${encodeURIComponent(chatId)}/keywords`;
  const method = isEditing ? "PATCH" : "POST";
  const bodyPayload = isEditing
    ? {
        keyword: payload.keyword,
        action: payload.action,
        mute_minutes: payload.mute_minutes,
        enabled: payload.enabled,
      }
    : payload;
  const result = await requestJson(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(bodyPayload),
  });
  if (!result.ok) {
    showStatus(parseApiMessage(result.data) || t("operation_failed"), true);
    return;
  }
  closeModal(kwModal);
  showStatus(t("saved"), false);
  await loadKeywords();
});

kwRefresh?.addEventListener("click", loadKeywords);
kwChatId?.addEventListener("change", loadKeywords);

kwTableBody?.addEventListener("click", async (event) => {
  const target = event.target;
  if (!(target instanceof HTMLButtonElement)) return;
  const action = target.dataset.action || "";
  const keywordId = target.dataset.id || "";
  const chatId = kwChatId?.value || "";
  if (!action || !keywordId || !chatId) return;

  if (action === "delete") {
    const result = await requestJson(
      `/api/v1/groups/${encodeURIComponent(chatId)}/keywords/${encodeURIComponent(keywordId)}`,
      { method: "DELETE" },
    );
    if (!result.ok) {
      showStatus(parseApiMessage(result.data) || t("operation_failed"), true);
      return;
    }
    showStatus(t("saved"), false);
    await loadKeywords();
    return;
  }

  if (action === "toggle") {
    const enabled = target.dataset.enabled === "1";
    const result = await requestJson(
      `/api/v1/groups/${encodeURIComponent(chatId)}/keywords/${encodeURIComponent(keywordId)}`,
      {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ enabled: !enabled }),
      },
    );
    if (!result.ok) {
      showStatus(parseApiMessage(result.data) || t("operation_failed"), true);
      return;
    }
    showStatus(t("saved"), false);
    await loadKeywords();
    return;
  }

  if (action === "edit") {
    const result = await requestJson(`/api/v1/groups/${encodeURIComponent(chatId)}/keywords`);
    if (!result.ok || !Array.isArray(result.data)) {
      showStatus(parseApiMessage(result.data) || t("operation_failed"), true);
      return;
    }
    const found = result.data.find((item) => String(item.id) === String(keywordId));
    if (!found) {
      showStatus(t("rule_not_found"), true);
      return;
    }
    kwEditingKeywordId = found.id;
    if (kwModalTitle) kwModalTitle.textContent = t("keyword_update", "Update Keyword Rule");
    if (kwModalKeyword) kwModalKeyword.value = found.keyword || "";
    if (kwModalAction) kwModalAction.value = found.action || "delete";
    if (kwModalMuteMinutes) kwModalMuteMinutes.value = String(Number(found.mute_minutes || 10));
    if (kwModalEnabled) kwModalEnabled.checked = Boolean(found.enabled);
    openModal(kwModal);
  }
});

akOpenAdd?.addEventListener("click", () => {
  resetAdKeywordModal();
  openModal(akModal);
});

akModalCancel?.addEventListener("click", () => closeModal(akModal));
akModalClose?.addEventListener("click", () => closeModal(akModal));
akModal?.addEventListener("click", (event) => {
  if (event.target === akModal) closeModal(akModal);
});

akModalSave?.addEventListener("click", async () => {
  const chatId = akChatId?.value || "";
  if (!chatId) {
    showStatus(t("select_group"), true);
    return;
  }
  const payload = {
    chat_id: Number(chatId),
    keyword: (akModalKeyword?.value || "").trim(),
    enabled: Boolean(akModalEnabled?.checked),
  };
  if (!payload.keyword) {
    showStatus(t("fill_required_fields"), true);
    return;
  }

  const isEditing = akEditingKeywordId !== null;
  const url = isEditing
    ? `/api/v1/groups/${encodeURIComponent(chatId)}/ad-keywords/${encodeURIComponent(String(akEditingKeywordId))}`
    : `/api/v1/groups/${encodeURIComponent(chatId)}/ad-keywords`;
  const method = isEditing ? "PATCH" : "POST";
  const bodyPayload = isEditing ? { keyword: payload.keyword, enabled: payload.enabled } : payload;
  const result = await requestJson(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(bodyPayload),
  });
  if (!result.ok) {
    showStatus(parseApiMessage(result.data) || t("operation_failed"), true);
    return;
  }
  closeModal(akModal);
  showStatus(t("saved"), false);
  await loadAdKeywords();
});

akRefresh?.addEventListener("click", loadAdKeywords);
akChatId?.addEventListener("change", loadAdKeywords);

akTableBody?.addEventListener("click", async (event) => {
  const target = event.target;
  if (!(target instanceof HTMLButtonElement)) return;
  const action = target.dataset.action || "";
  const keywordId = target.dataset.id || "";
  const chatId = akChatId?.value || "";
  if (!action || !keywordId || !chatId) return;

  if (action === "delete") {
    const result = await requestJson(
      `/api/v1/groups/${encodeURIComponent(chatId)}/ad-keywords/${encodeURIComponent(keywordId)}`,
      { method: "DELETE" },
    );
    if (!result.ok) {
      showStatus(parseApiMessage(result.data) || t("operation_failed"), true);
      return;
    }
    showStatus(t("saved"), false);
    await loadAdKeywords();
    return;
  }

  if (action === "toggle") {
    const enabled = target.dataset.enabled === "1";
    const result = await requestJson(
      `/api/v1/groups/${encodeURIComponent(chatId)}/ad-keywords/${encodeURIComponent(keywordId)}`,
      {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ enabled: !enabled }),
      },
    );
    if (!result.ok) {
      showStatus(parseApiMessage(result.data) || t("operation_failed"), true);
      return;
    }
    showStatus(t("saved"), false);
    await loadAdKeywords();
    return;
  }

  if (action === "edit") {
    const result = await requestJson(`/api/v1/groups/${encodeURIComponent(chatId)}/ad-keywords`);
    if (!result.ok || !Array.isArray(result.data)) {
      showStatus(parseApiMessage(result.data) || t("operation_failed"), true);
      return;
    }
    const found = result.data.find((item) => String(item.id) === String(keywordId));
    if (!found) {
      showStatus(t("rule_not_found"), true);
      return;
    }
    akEditingKeywordId = found.id;
    if (akModalTitle) akModalTitle.textContent = t("ad_keyword_update", "Update Ad Rule");
    if (akModalKeyword) akModalKeyword.value = found.keyword || "";
    if (akModalEnabled) akModalEnabled.checked = Boolean(found.enabled);
    openModal(akModal);
  }
});

gsChatId?.addEventListener("change", () => applyGroupSettings(gsChatId.value));
gsSave?.addEventListener("click", saveGroupSettings);
gsRefresh?.addEventListener("click", loadGroupConfigs);

cmChatId?.addEventListener("change", async () => {
  rememberCommunityChatId();
  await loadCommunityConfig();
});
cmSave?.addEventListener("click", saveCommunityConfig);
cmSection?.addEventListener("click", async (event) => {
  const target = event.target;
  if (!(target instanceof Element)) return;
  const button = target.closest(".cm-config-save");
  if (!(button instanceof HTMLButtonElement)) return;
  await saveCommunityConfig();
});
cmRefresh?.addEventListener("click", loadCommunityConfig);
cmNoteSave?.addEventListener("click", saveCommunityNote);
cmRssSave?.addEventListener("click", saveCommunityRss);
cmGbanSave?.addEventListener("click", saveGlobalBan);

cmNotesBody?.addEventListener("click", async (event) => {
  const target = event.target;
  if (!(target instanceof HTMLButtonElement)) return;
  if (target.dataset.action !== "delete-note") return;
  const chatId = getCommunityChatId();
  const name = target.dataset.name || "";
  if (!chatId || !name) return;
  const result = await requestJson(
    `/api/v1/community/${encodeURIComponent(chatId)}/notes/${encodeURIComponent(name)}`,
    { method: "DELETE" },
  );
  if (!result.ok) {
    showStatus(parseApiMessage(result.data) || t("operation_failed"), true);
    return;
  }
  showStatus(t("saved"), false);
  await loadCommunityNotes();
});

cmRssBody?.addEventListener("click", async (event) => {
  const target = event.target;
  if (!(target instanceof HTMLButtonElement)) return;
  if (target.dataset.action !== "delete-rss") return;
  const chatId = getCommunityChatId();
  const url = target.dataset.url || "";
  if (!chatId || !url) return;
  const params = new URLSearchParams({ url });
  const result = await requestJson(`/api/v1/community/${encodeURIComponent(chatId)}/rss?${params.toString()}`, {
    method: "DELETE",
  });
  if (!result.ok) {
    showStatus(parseApiMessage(result.data) || t("operation_failed"), true);
    return;
  }
  showStatus(t("saved"), false);
  await loadCommunityRss();
});

cmGbanBody?.addEventListener("click", async (event) => {
  const target = event.target;
  if (!(target instanceof HTMLButtonElement)) return;
  if (target.dataset.action !== "delete-gban") return;
  const userId = target.dataset.userId || "";
  if (!userId) return;
  const result = await requestJson(`/api/v1/community/global-bans/${encodeURIComponent(userId)}`, {
    method: "DELETE",
  });
  if (!result.ok) {
    showStatus(parseApiMessage(result.data) || t("operation_failed"), true);
    return;
  }
  showStatus(t("saved"), false);
  await loadGlobalBans();
});

evRefresh?.addEventListener("click", loadMemberEvents);
evChatId?.addEventListener("change", loadMemberEvents);

logRefresh?.addEventListener("click", loadModerationLogs);
logChatId?.addEventListener("change", loadModerationLogs);
logEventType?.addEventListener("change", loadModerationLogs);
logLimit?.addEventListener("change", loadModerationLogs);

banRefresh?.addEventListener("click", loadBans);
banChatId?.addEventListener("change", loadBans);
banTableBody?.addEventListener("click", async (event) => {
  const target = event.target;
  if (!(target instanceof HTMLButtonElement)) return;
  if (target.dataset.action !== "unban") return;
  const chatId = target.dataset.chatId || "";
  const userId = target.dataset.userId || "";
  if (!chatId || !userId) return;
  target.disabled = true;
  const result = await requestJson(
    `/api/v1/sanctions/bans/${encodeURIComponent(chatId)}/${encodeURIComponent(userId)}/unban`,
    { method: "POST" },
  );
  if (!result.ok) {
    target.disabled = false;
    showStatus(parseApiMessage(result.data) || t("operation_failed"), true);
    return;
  }
  showStatus(t("saved"), false);
  await loadBans();
});

if (arModal) arModal.hidden = true;
if (akModal) akModal.hidden = true;
if (arPreviewModal) arPreviewModal.hidden = true;

document.addEventListener("keydown", (event) => {
  if (event.key !== "Escape") return;
  if (arModal && !arModal.hidden) closeModal(arModal);
  if (akModal && !akModal.hidden) closeModal(akModal);
  if (arPreviewModal && !arPreviewModal.hidden) closeModal(arPreviewModal);
});

pollOnlineUpdateStatus();

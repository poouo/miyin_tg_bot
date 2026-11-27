const bodyEl = document.body;
const sidebar = document.getElementById("sidebar");
const sidebarOverlay = document.getElementById("sidebar-overlay");
const workspaceEl = document.querySelector(".workspace");
const menuToggle = document.getElementById("mobile-menu-toggle");
const themeToggle = document.getElementById("theme-toggle");
const workspaceTitle = document.getElementById("workspace-title");
const toastRegion = document.getElementById("toast-region");
const navItems = Array.from(document.querySelectorAll(".nav-item"));
const sections = Array.from(document.querySelectorAll(".section"));
const overviewActions = Array.from(document.querySelectorAll("[data-overview-target]"));
const overviewTimes = Array.from(document.querySelectorAll("[data-overview-time]"));

const btnCheck = document.getElementById("check-update");
const btnTrigger = document.getElementById("trigger-update");
const btnSaveSecurity = document.getElementById("save-security");
const btnSaveRuntime = document.getElementById("save-runtime");
const btnSaveAi = document.getElementById("save-ai");
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
const aiProviderRadios = Array.from(document.querySelectorAll('input[name="ai-provider"]'));
const aiProviderPanels = Array.from(document.querySelectorAll("[data-provider-panel]"));
const rtAiTimeoutSec = document.getElementById("rt-ai-timeout-sec");
const rtAiTemperature = document.getElementById("rt-ai-temperature");
const rtAiMaxTokens = document.getElementById("rt-ai-max-tokens");
const rtAiSystemPrompt = document.getElementById("rt-ai-system-prompt");
const rtJoinVerifyTimeoutSec = document.getElementById("rt-join-verify-timeout-sec");
const rtSpamWindowSec = document.getElementById("rt-spam-window-sec");
const rtSpamMaxMessages = document.getElementById("rt-spam-max-messages");

const upgradeFill = document.getElementById("upgrade-fill");
const upgradeTrack = document.querySelector(".upgrade-track");
const upgradeStatus = document.getElementById("upgrade-status");
const dockerUpdateInstructions = document.getElementById("docker-update-instructions");

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
const kwModalDeleteMessage = document.getElementById("kw-modal-delete-message");
const kwModalMuteUser = document.getElementById("kw-modal-mute-user");
const kwModalBanUser = document.getElementById("kw-modal-ban-user");
const kwModalMuteMinutesField = document.getElementById("kw-modal-mute-minutes-field");
const kwModalMuteMinutes = document.getElementById("kw-modal-mute-minutes");
const kwModalBanMinutesField = document.getElementById("kw-modal-ban-minutes-field");
const kwModalBanMinutes = document.getElementById("kw-modal-ban-minutes");
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
const akModalDeleteMessage = document.getElementById("ak-modal-delete-message");
const akModalMuteUser = document.getElementById("ak-modal-mute-user");
const akModalBanUser = document.getElementById("ak-modal-ban-user");
const akModalApplyToMentions = document.getElementById("ak-modal-apply-to-mentions");
const akModalMuteMinutesField = document.getElementById("ak-modal-mute-minutes-field");
const akModalMuteMinutes = document.getElementById("ak-modal-mute-minutes");
const akModalBanMinutesField = document.getElementById("ak-modal-ban-minutes-field");
const akModalBanMinutes = document.getElementById("ak-modal-ban-minutes");
const akModalEnabled = document.getElementById("ak-modal-enabled");
const akModalSave = document.getElementById("ak-modal-save");
const akModalCancel = document.getElementById("ak-modal-cancel");
const akModalClose = document.getElementById("ak-modal-close");
const aktOpen = document.getElementById("akt-open");
const aktModal = document.getElementById("akt-modal");
const aktModalClose = document.getElementById("akt-modal-close");
const aktList = document.getElementById("akt-list");
const aktDeleteMessage = document.getElementById("akt-delete-message");
const aktMuteUser = document.getElementById("akt-mute-user");
const aktBanUser = document.getElementById("akt-ban-user");
const aktMuteMinutesField = document.getElementById("akt-mute-minutes-field");
const aktMuteMinutes = document.getElementById("akt-mute-minutes");
const aktBanMinutesField = document.getElementById("akt-ban-minutes-field");
const aktBanMinutes = document.getElementById("akt-ban-minutes");
const aktApply = document.getElementById("akt-apply");
const aktCancel = document.getElementById("akt-cancel");

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
const gsAiMember = document.getElementById("gs-ai-member");
const gsAiReplyDeleteAfterSeconds = document.getElementById("gs-ai-reply-delete-after-seconds");
const gsJoinVerifyFailAction = document.getElementById("gs-join-verify-fail-action");
const gsJoinVerifyFailKickMinutes = document.getElementById("gs-join-verify-fail-kick-minutes");
const gsJoinVerifyFailMuteMinutes = document.getElementById("gs-join-verify-fail-mute-minutes");
const gsJoinVerifyFailBanMinutes = document.getElementById("gs-join-verify-fail-ban-minutes");
const gsAdBlockAction = document.getElementById("gs-ad-block-action");
const gsAdBlockDeleteMessage = document.getElementById("gs-ad-block-delete-message");
const gsAdBlockApplyToMentions = document.getElementById("gs-ad-block-apply-to-mentions");
const gsAdBlockKickMinutes = document.getElementById("gs-ad-block-kick-minutes");
const gsAdBlockMuteMinutes = document.getElementById("gs-ad-block-mute-minutes");
const gsAdBlockBanMinutes = document.getElementById("gs-ad-block-ban-minutes");
const gsAiAdBlock = document.getElementById("gs-ai-ad-block");
const gsAiAdBlockWindowSec = document.getElementById("gs-ai-ad-block-window-sec");
const gsAiAdBlockHighConfidence = document.getElementById("gs-ai-ad-block-high-confidence");
const gsAiAdBlockHighAction = document.getElementById("gs-ai-ad-block-high-action");
const gsAiAdBlockMidConfidence = document.getElementById("gs-ai-ad-block-mid-confidence");
const gsAiAdBlockMidAction = document.getElementById("gs-ai-ad-block-mid-action");
const gsAiAdBlockMinConfidence = document.getElementById("gs-ai-ad-block-min-confidence");
const gsAiAdBlockMinAction = document.getElementById("gs-ai-ad-block-min-action");
const gsAiAdBlockPunishMentioner = document.getElementById("gs-ai-ad-block-punish-mentioner");
const gsAiAdBlockMentionerWarningLimit = document.getElementById("gs-ai-ad-block-mentioner-warning-limit");
const gsAiAdBlockMentionerAction = document.getElementById("gs-ai-ad-block-mentioner-action");
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

const ACTIVE_SECTION_KEY = "miyin.dashboard.activeSection";
const THEME_KEY = "miyin.dashboard.theme.v2";
const COMMUNITY_CHAT_KEY = "miyin.dashboard.communityChatId";
const AI_MODEL_CACHE_KEY = "miyin.dashboard.aiModels.v1";
let actionStatusTimer = null;
let arEditingRuleId = null;
let kwEditingKeywordId = null;
let akEditingKeywordId = null;
const groupConfigCache = new Map();
const managedGroup = document.getElementById("managed-group");
const managedGroupScope = document.getElementById("managed-group-scope");
const groupStatusBody = document.getElementById("group-status-body");
const managedGroupTargets = new Map([
  ["group-settings", gsChatId], ["auto-replies", arChatId], ["keywords", kwChatId],
  ["ad-keywords", akChatId], ["community", cmChatId], ["member-events", evChatId],
  ["moderation-logs", logChatId], ["bans", banChatId],
]);
const managesAllGroups = new Set(["moderation-logs", "bans"]);
let selectedManagedGroup = "";
let showingAllManagedGroups = false;
let communityLoad = 0;
let communityLoadedChat = "";
let groupsRequest = 0;
let groupSettingsLoadedChat = "";


function t(key, fallback) {
  return i18n[key] || fallback || key;
}

function formatOverviewTimes() {
  const locale = document.documentElement.lang === "en" ? "en-US" : "zh-CN";
  const relative = new Intl.RelativeTimeFormat(locale, { numeric: "auto" });
  const now = Date.now();

  overviewTimes.forEach((timeEl) => {
    const raw = String(timeEl.dataset.overviewTime || "").trim();
    if (!raw) return;
    const normalized = /(?:Z|[+-]\d{2}:\d{2})$/i.test(raw) ? raw : `${raw}Z`;
    const date = new Date(normalized);
    if (Number.isNaN(date.getTime())) return;

    const diffSeconds = Math.round((date.getTime() - now) / 1000);
    const absoluteSeconds = Math.abs(diffSeconds);
    if (absoluteSeconds < 60) {
      timeEl.textContent = relative.format(diffSeconds, "second");
    } else if (absoluteSeconds < 3600) {
      timeEl.textContent = relative.format(Math.round(diffSeconds / 60), "minute");
    } else if (absoluteSeconds < 86400) {
      timeEl.textContent = relative.format(Math.round(diffSeconds / 3600), "hour");
    } else if (absoluteSeconds < 604800) {
      timeEl.textContent = relative.format(Math.round(diffSeconds / 86400), "day");
    } else {
      timeEl.textContent = date.toLocaleDateString(locale, { month: "2-digit", day: "2-digit" });
    }
    timeEl.title = date.toLocaleString(locale, { hour12: false });
  });
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
  const text = String(message || "").trim();
  if (!text || !toastRegion) return;

  while (toastRegion.children.length >= 4) {
    const candidates = Array.from(toastRegion.children);
    const oldest = candidates.find((item) => !item.contains(document.activeElement)) || candidates[0];
    if (oldest?.dismissTimer) window.clearTimeout(oldest.dismissTimer);
    oldest?.remove();
  }

  const toast = document.createElement("div");
  toast.className = `app-toast ${isError ? "error" : "success"}`;
  toast.setAttribute("role", isError ? "alert" : "status");

  const icon = document.createElement("span");
  icon.className = "toast-icon";
  icon.setAttribute("aria-hidden", "true");
  const iconGlyph = document.createElement("i");
  iconGlyph.className = isError ? "ri-error-warning-line" : "ri-checkbox-circle-line";
  icon.append(iconGlyph);

  const messageEl = document.createElement("span");
  messageEl.className = "toast-message";
  messageEl.textContent = text;

  const close = document.createElement("button");
  close.className = "toast-close";
  close.type = "button";
  close.setAttribute("aria-label", t("close", "Close"));
  close.title = t("close", "Close");
  const closeGlyph = document.createElement("i");
  closeGlyph.className = "ri-close-line";
  close.append(closeGlyph);

  toast.append(icon, messageEl, close);
  toastRegion.append(toast);

  let isHovered = false;
  let hasFocus = false;
  const dismiss = () => {
    if (toast.dataset.dismissed === "true") return;
    toast.dataset.dismissed = "true";
    if (toast.dismissTimer) window.clearTimeout(toast.dismissTimer);
    toast.classList.add("is-leaving");
    window.setTimeout(() => toast.remove(), 220);
  };
  const scheduleDismiss = () => {
    if (toast.dataset.dismissed === "true") return;
    if (toast.dismissTimer) window.clearTimeout(toast.dismissTimer);
    toast.dismissTimer = window.setTimeout(dismiss, isError ? 5200 : 3600);
  };

  close.addEventListener("click", dismiss);
  toast.addEventListener("mouseenter", () => {
    isHovered = true;
    window.clearTimeout(toast.dismissTimer);
  });
  toast.addEventListener("mouseleave", () => {
    isHovered = false;
    if (!hasFocus) scheduleDismiss();
  });
  toast.addEventListener("focusin", () => {
    hasFocus = true;
    window.clearTimeout(toast.dismissTimer);
  });
  toast.addEventListener("focusout", (event) => {
    if (event.relatedTarget && toast.contains(event.relatedTarget)) return;
    hasFocus = false;
    if (!isHovered) scheduleDismiss();
  });
  window.requestAnimationFrame(() => toast.classList.add("is-visible"));
  scheduleDismiss();
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
  const message = payload.message || payload.detail || payload.error || "";
  return Array.isArray(message) ? message.map((item) => item.msg).filter(Boolean).join(" ") : message;
}

function setUpgradeStatus(progress, text, type = "normal") {
  const safeProgress = Math.max(0, Math.min(100, Number(progress) || 0));
  if (upgradeFill) {
    upgradeFill.style.width = `${safeProgress}%`;
    upgradeFill.classList.remove("success", "failed");
    if (type === "success") upgradeFill.classList.add("success");
    if (type === "failed") upgradeFill.classList.add("failed");
  }
  if (upgradeTrack) {
    upgradeTrack.hidden = progress === null;
    upgradeTrack.setAttribute("aria-valuenow", String(safeProgress));
  }
  if (upgradeStatus) {
    upgradeStatus.textContent = progress === null ? text : `${safeProgress}% · ${text}`;
    upgradeStatus.dataset.type = type;
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
  if (kwModalDeleteMessage) kwModalDeleteMessage.checked = true;
  if (kwModalMuteUser) kwModalMuteUser.checked = false;
  if (kwModalBanUser) kwModalBanUser.checked = false;
  if (kwModalMuteMinutes) kwModalMuteMinutes.value = "10";
  if (kwModalBanMinutes) kwModalBanMinutes.value = "1440";
  if (kwModalEnabled) kwModalEnabled.checked = true;
  syncKeywordActionFields();
}

function syncKeywordActionFields(preferredPenalty = "") {
  if (preferredPenalty === "mute" && kwModalMuteUser?.checked && kwModalBanUser) {
    kwModalBanUser.checked = false;
  } else if (preferredPenalty === "ban" && kwModalBanUser?.checked && kwModalMuteUser) {
    kwModalMuteUser.checked = false;
  } else if (kwModalMuteUser?.checked && kwModalBanUser?.checked) {
    kwModalMuteUser.checked = false;
  }

  const muteEnabled = Boolean(kwModalMuteUser?.checked);
  const banEnabled = Boolean(kwModalBanUser?.checked);
  if (kwModalMuteMinutesField) kwModalMuteMinutesField.hidden = !muteEnabled;
  if (kwModalMuteMinutes) kwModalMuteMinutes.disabled = !muteEnabled;
  if (kwModalBanMinutesField) kwModalBanMinutesField.hidden = !banEnabled;
  if (kwModalBanMinutes) kwModalBanMinutes.disabled = !banEnabled;
}

function resetAdKeywordModal() {
  akEditingKeywordId = null;
  if (akModalTitle) akModalTitle.textContent = t("ad_keyword_add", "Add Ad Keyword");
  if (akModalKeyword) akModalKeyword.value = "";
  if (akModalDeleteMessage) akModalDeleteMessage.checked = true;
  if (akModalMuteUser) akModalMuteUser.checked = false;
  if (akModalBanUser) akModalBanUser.checked = false;
  if (akModalApplyToMentions) akModalApplyToMentions.checked = false;
  if (akModalMuteMinutes) akModalMuteMinutes.value = "30";
  if (akModalBanMinutes) akModalBanMinutes.value = "1440";
  if (akModalEnabled) akModalEnabled.checked = true;
  syncAdKeywordActionFields();
}

function syncAdKeywordActionFields(preferredPenalty = "") {
  if (preferredPenalty === "mute" && akModalMuteUser?.checked && akModalBanUser) {
    akModalBanUser.checked = false;
  } else if (preferredPenalty === "ban" && akModalBanUser?.checked && akModalMuteUser) {
    akModalMuteUser.checked = false;
  } else if (akModalMuteUser?.checked && akModalBanUser?.checked) {
    akModalMuteUser.checked = false;
  }

  const muteEnabled = Boolean(akModalMuteUser?.checked);
  const banEnabled = Boolean(akModalBanUser?.checked);
  if (akModalMuteMinutesField) akModalMuteMinutesField.hidden = !muteEnabled;
  if (akModalMuteMinutes) akModalMuteMinutes.disabled = !muteEnabled;
  if (akModalBanMinutesField) akModalBanMinutesField.hidden = !banEnabled;
  if (akModalBanMinutes) akModalBanMinutes.disabled = !banEnabled;
}

function isValidModerationDuration(value) {
  return Number.isInteger(value) && value >= 1 && value <= 10080;
}

function formatAdKeywordActions(item) {
  const labels = [];
  const minuteUnit = t("ad_keyword_minutes_unit", "min");
  if (item.delete_message !== false) {
    labels.push(t("action_delete", "Delete message"));
  }
  if (item.mute_user) {
    const minutes = Number(item.mute_minutes || 30);
    labels.push(`${t("action_mute", "Mute")} ${minutes} ${minuteUnit}`);
  }
  if (item.ban_user) {
    const minutes = Number(item.ban_minutes || 1440);
    labels.push(`${t("action_ban", "Ban")} ${minutes} ${minuteUnit}`);
  }
  if (item.apply_to_mentions) {
    labels.push(t("ad_apply_to_mentions_tag", "Mentions included"));
  }
  return labels;
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
  const chatId = arChatId?.value;
  renderAutoReplies([]);
  const result = await requestJson(`/api/v1/groups/${encodeURIComponent(arChatId.value)}/auto-replies`);
  if (chatId !== arChatId?.value) return;
  if (!result.ok) {
    showStatus(parseApiMessage(result.data) || t("operation_failed"), true);
    renderAutoReplies([]);
    return;
  }
  renderAutoReplies(result.data);
}

function keywordActionState(item) {
  const hasExplicitActions = ["delete_message", "mute_user", "ban_user"].some(
    (key) => typeof item[key] === "boolean",
  );
  return {
    deleteMessage: hasExplicitActions ? item.delete_message !== false : true,
    muteUser: hasExplicitActions ? Boolean(item.mute_user) : item.action === "mute",
    banUser: hasExplicitActions ? Boolean(item.ban_user) : item.action === "ban",
  };
}

function formatKeywordActions(item) {
  const labels = [];
  const state = keywordActionState(item);
  const minuteUnit = t("keyword_minutes_unit", "min");
  if (state.deleteMessage) labels.push(t("action_delete", "Delete message"));
  if (state.muteUser) {
    labels.push(`${t("action_mute", "Mute")} ${Number(item.mute_minutes || 10)} ${minuteUnit}`);
  }
  if (state.banUser) {
    labels.push(`${t("action_ban", "Ban")} ${Number(item.ban_minutes || 1440)} ${minuteUnit}`);
  }
  return labels;
}

function renderKeywords(items) {
  if (!kwTableBody) return;
  if (!Array.isArray(items) || !items.length) {
    kwTableBody.innerHTML = `<tr><td colspan="4">${escapeHtml(t("no_data", "No data"))}</td></tr>`;
    return;
  }
  kwTableBody.innerHTML = items
    .map((item) => {
      const statusText = item.enabled ? t("switch_on", "on") : t("switch_off", "off");
      const toggleText = item.enabled ? t("disable", "Disable") : t("enable", "Enable");
      const actionLabels = formatKeywordActions(item);
      const actionHtml = actionLabels.length
        ? actionLabels.map((label) => `<span class="ad-action-tag">${escapeHtml(label)}</span>`).join("")
        : '<span class="ad-action-empty">&mdash;</span>';
      return `<tr>
        <td><div class="cell-keyword">${escapeHtml(item.keyword)}</div></td>
        <td><div class="ad-action-list">${actionHtml}</div></td>
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
  const chatId = kwChatId?.value;
  renderKeywords([]);
  const result = await requestJson(`/api/v1/groups/${encodeURIComponent(kwChatId.value)}/keywords`);
  if (chatId !== kwChatId?.value) return;
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
    akTableBody.innerHTML = `<tr><td colspan="4">${escapeHtml(t("no_data", "No data"))}</td></tr>`;
    return;
  }

  akTableBody.innerHTML = items
    .map((item) => {
      const statusText = item.enabled ? t("switch_on", "on") : t("switch_off", "off");
      const toggleText = item.enabled ? t("disable", "Disable") : t("enable", "Enable");
      const actionLabels = formatAdKeywordActions(item);
      const actionHtml = actionLabels.length
        ? actionLabels.map((label) => `<span class="ad-action-tag">${escapeHtml(label)}</span>`).join("")
        : '<span class="ad-action-empty">&mdash;</span>';
      return `<tr>
        <td><div class="cell-keyword">${escapeHtml(item.keyword)}</div></td>
        <td><div class="ad-action-list">${actionHtml}</div></td>
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
  const chatId = akChatId?.value;
  renderAdKeywords([]);
  const result = await requestJson(`/api/v1/groups/${encodeURIComponent(akChatId.value)}/ad-keywords`);
  if (chatId !== akChatId?.value) return;
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
  const chatId = logChatId?.value;
  renderModerationLogs([]);
  const result = await requestJson(`/api/v1/logs/recent?${params.toString()}`);
  if (chatId !== logChatId?.value) return;
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
  const chatId = evChatId?.value;
  renderMemberEvents([]);
  const result = await requestJson(`/api/v1/logs/member-events?${params.toString()}`);
  if (chatId !== evChatId?.value) return;
  if (!result.ok) {
    renderMemberEvents([]);
    return;
  }
  renderMemberEvents(result.data);
}

function applyTheme(theme) {
  const isDark = theme === "dark";
  bodyEl.classList.toggle("dark", isDark);
  document.documentElement.style.colorScheme = isDark ? "dark" : "light";
  if (!themeToggle) return;
  const icon = themeToggle.querySelector("i");
  const label = themeToggle.querySelector("span");
  const nextLabel = isDark ? t("theme_light", "Light mode") : t("theme_dark", "Dark mode");
  if (icon) icon.className = isDark ? "ri-sun-line" : "ri-moon-line";
  if (label) label.textContent = nextLabel;
  themeToggle.setAttribute("aria-label", nextLabel);
  themeToggle.title = nextLabel;
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
  const chatId = banChatId?.value;
  renderBans([]);
  const result = await requestJson(`/api/v1/sanctions/bans${query ? `?${query}` : ""}`);
  if (chatId !== banChatId?.value) return;
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

function rememberManagedGroup(chatId) {
  if (!chatId) return;
  selectedManagedGroup = chatId;
  try {
    window.localStorage.setItem(COMMUNITY_CHAT_KEY, chatId);
  } catch (err) {
    // Storage may be unavailable in private browsing.
  }
}

function restoreManagedGroup() {
  try {
    selectedManagedGroup = window.localStorage.getItem(COMMUNITY_CHAT_KEY) || "";
  } catch (err) {
    // Storage may be unavailable in private browsing.
  }
}

function currentSection() {
  return sections.find((section) => !section.hidden)?.id || "overview";
}

function syncManagedGroup(target) {
  if (!managedGroup || !managedGroupScope) return;
  const control = managedGroupTargets.get(target);
  managedGroupScope.hidden = !control;
  if (!control) return;
  const allOption = managedGroup.querySelector("[data-all-groups]");
  const allowAll = managesAllGroups.has(target);
  allOption.hidden = !allowAll;
  allOption.disabled = !allowAll;
  const groups = Array.from(managedGroup.options).filter((option) => option.value);
  if (!groups.some((option) => option.value === selectedManagedGroup)) {
    selectedManagedGroup = groups[0]?.value || "";
  }
  managedGroup.value = allowAll && showingAllManagedGroups ? "" : selectedManagedGroup;
  control.value = managedGroup.value;
}

function updateGroupControls(groups) {
  if (!managedGroup) return;
  const allOption = managedGroup.querySelector("[data-all-groups]");
  managedGroup.replaceChildren(allOption, ...groups.map((group) => new Option(group.title || group.chat_id, group.chat_id)));
  managedGroupTargets.forEach((control, target) => {
    if (!control) return;
    const previous = control.value;
    const options = groups.map((group) => new Option(group.title || group.chat_id, group.chat_id));
    if (managesAllGroups.has(target)) options.unshift(new Option(t("all_groups"), ""));
    control.replaceChildren(...options);
    if (options.some((option) => option.value === previous)) control.value = previous;
  });
  syncManagedGroup(currentSection());
}

managedGroup?.addEventListener("change", async () => {
  showingAllManagedGroups = !managedGroup.value;
  rememberManagedGroup(managedGroup.value);
  const target = currentSection();
  syncManagedGroup(target);
  if (target === "group-settings" && groupConfigCache.has(Number(gsChatId.value))) {
    applyGroupSettings(gsChatId.value);
  } else {
    await handleSectionEnter(target);
  }
});

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

function setCommunityReady(ready) {
  cmSection?.querySelectorAll(".cm-config-save, #cm-note-save, #cm-rss-save").forEach((button) => {
    button.disabled = !ready;
  });
}

async function loadCommunityConfig() {
  const chatId = getCommunityChatId();
  const request = ++communityLoad;
  if (communityLoadedChat !== chatId) {
    renderCommunityNotes([]);
    renderCommunityRss([]);
    [cmNoteName, cmNoteText, cmRssUrl, cmRssTitle].forEach((field) => {
      if (field) field.value = "";
    });
  }
  communityLoadedChat = "";
  setCommunityReady(false);
  if (!chatId) return;
  const result = await requestJson(`/api/v1/community/${encodeURIComponent(chatId)}`);
  if (request !== communityLoad || chatId !== getCommunityChatId()) return;
  if (!result.ok) {
    showStatus(parseApiMessage(result.data) || t("operation_failed"), true);
    return;
  }
  applyCommunityConfig(result.data);
  communityLoadedChat = chatId;
  setCommunityReady(true);
  await Promise.all([loadCommunityNotes(), loadCommunityRss()]);
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

const communitySaveFields = {
  rules: ["rules_text"],
  welcome: ["welcome_enabled", "goodbye_enabled", "clean_welcome", "welcome_text", "goodbye_text"],
  warnings: ["warn_limit", "warn_action", "warn_mute_minutes", "warn_ban_minutes", "reports_enabled"],
  locks: ["lock_links", "lock_forwards", "lock_media", "lock_stickers", "lock_commands"],
  logs: ["log_enabled", "log_chat_id"],
  commands: ["disabled_commands"],
};

async function saveCommunityConfig(button) {
  const chatId = getCommunityChatId();
  if (!chatId || chatId !== communityLoadedChat || button.disabled) return;
  const fields = communitySaveFields[button.dataset.scope];
  if (!fields) return;
  const form = buildCommunityPayload();
  const payload = Object.fromEntries(fields.map((field) => [field, form[field]]));
  const request = communityLoad;
  button.disabled = true;
  const result = await requestJson(`/api/v1/community/${encodeURIComponent(chatId)}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (request !== communityLoad || chatId !== getCommunityChatId()) return;
  button.disabled = false;
  if (!result.ok) {
    showStatus(parseApiMessage(result.data) || t("operation_failed"), true);
    return;
  }
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
  const request = communityLoad;
  const result = await requestJson(`/api/v1/community/${encodeURIComponent(chatId)}/notes`);
  if (request === communityLoad && chatId === getCommunityChatId()) renderCommunityNotes(result.ok ? result.data : []);
}

async function saveCommunityNote() {
  const chatId = getCommunityChatId();
  const payload = {
    name: (cmNoteName?.value || "").trim(),
    text: (cmNoteText?.value || "").trim(),
    parse_mode: (cmNoteParseMode?.value || "plain").toLowerCase(),
  };
  if (!chatId || chatId !== communityLoadedChat || !payload.name || !payload.text) {
    showStatus(t("fill_required_fields"), true);
    return;
  }
  const result = await requestJson(`/api/v1/community/${encodeURIComponent(chatId)}/notes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (chatId !== getCommunityChatId()) return;
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
  const request = communityLoad;
  const result = await requestJson(`/api/v1/community/${encodeURIComponent(chatId)}/rss`);
  if (request === communityLoad && chatId === getCommunityChatId()) renderCommunityRss(result.ok ? result.data : []);
}

async function saveCommunityRss() {
  const chatId = getCommunityChatId();
  const payload = {
    url: (cmRssUrl?.value || "").trim(),
    title: (cmRssTitle?.value || "").trim(),
  };
  if (!chatId || chatId !== communityLoadedChat || !payload.url) {
    showStatus(t("fill_required_fields"), true);
    return;
  }
  const result = await requestJson(`/api/v1/community/${encodeURIComponent(chatId)}/rss`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (chatId !== getCommunityChatId()) return;
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
        <td><button class="table-btn" type="button" data-action="delete-gban" data-user-id="${item.user_id}">${escapeHtml(t(item.active === false ? "retry_unban" : "unban"))}</button></td>
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
  groupSettingsLoadedChat = config ? String(chatId) : "";
  if (gsSave) gsSave.disabled = !config;
  if (!config) return;
  if (gsJoinVerify) gsJoinVerify.checked = Boolean(config.join_verification_enabled);
  if (gsKeywordFilter) gsKeywordFilter.checked = Boolean(config.keyword_filter_enabled);
  if (gsAdBlock) gsAdBlock.checked = Boolean(config.ad_block_enabled);
  if (gsAntiSpam) gsAntiSpam.checked = Boolean(config.anti_spam_enabled);
  if (gsAutoRecover) gsAutoRecover.checked = Boolean(config.auto_recover_enabled);
  if (gsAi) gsAi.checked = Boolean(config.deepseek_enabled);
  if (gsAiMember) gsAiMember.checked = config.ai_member_enabled !== false;
  if (gsAiReplyDeleteAfterSeconds) {
    gsAiReplyDeleteAfterSeconds.value = String(Number(config.ai_reply_delete_after_seconds || 0));
  }
  if (gsJoinVerifyFailAction) gsJoinVerifyFailAction.value = config.join_verify_fail_action || "kick";
  if (gsJoinVerifyFailKickMinutes) gsJoinVerifyFailKickMinutes.value = String(Number(config.join_verify_fail_kick_minutes || 1));
  if (gsJoinVerifyFailMuteMinutes) gsJoinVerifyFailMuteMinutes.value = String(Number(config.join_verify_fail_mute_minutes || 30));
  if (gsJoinVerifyFailBanMinutes) gsJoinVerifyFailBanMinutes.value = String(Number(config.join_verify_fail_ban_minutes || 1440));
  if (gsAdBlockAction) gsAdBlockAction.value = config.ad_block_action || "mute";
  if (gsAdBlockDeleteMessage) gsAdBlockDeleteMessage.checked = config.ad_block_delete_message !== false;
  if (gsAdBlockApplyToMentions) {
    gsAdBlockApplyToMentions.checked = Boolean(config.ad_block_apply_to_mentions);
  }
  if (gsAdBlockKickMinutes) gsAdBlockKickMinutes.value = String(Number(config.ad_block_kick_minutes || 1));
  if (gsAdBlockMuteMinutes) gsAdBlockMuteMinutes.value = String(Number(config.ad_block_mute_minutes || 30));
  if (gsAdBlockBanMinutes) gsAdBlockBanMinutes.value = String(Number(config.ad_block_ban_minutes || 1440));
  if (gsAiAdBlock) gsAiAdBlock.checked = Boolean(config.ai_ad_block_enabled);
  if (gsAiAdBlockWindowSec) gsAiAdBlockWindowSec.value = String(Number(config.ai_ad_block_window_sec || 60));
  if (gsAiAdBlockHighConfidence) gsAiAdBlockHighConfidence.value = String(Number(config.ai_ad_block_high_confidence ?? 90));
  if (gsAiAdBlockHighAction) gsAiAdBlockHighAction.value = config.ai_ad_block_high_action || "ban";
  if (gsAiAdBlockMidConfidence) gsAiAdBlockMidConfidence.value = String(Number(config.ai_ad_block_mid_confidence ?? 75));
  if (gsAiAdBlockMidAction) gsAiAdBlockMidAction.value = config.ai_ad_block_mid_action || "mute";
  if (gsAiAdBlockMinConfidence) gsAiAdBlockMinConfidence.value = String(Number(config.ai_ad_block_min_confidence ?? 60));
  if (gsAiAdBlockMinAction) gsAiAdBlockMinAction.value = config.ai_ad_block_min_action || "warn";
  if (gsAiAdBlockPunishMentioner) {
    gsAiAdBlockPunishMentioner.checked = config.ai_ad_block_punish_mentioner !== false;
  }
  if (gsAiAdBlockMentionerWarningLimit) {
    gsAiAdBlockMentionerWarningLimit.value = String(Number(config.ai_ad_block_mentioner_warning_limit ?? 3));
  }
  if (gsAiAdBlockMentionerAction) {
    gsAiAdBlockMentionerAction.value = config.ai_ad_block_mentioner_action || "mute";
  }
  if (gsAntiSpamAction) gsAntiSpamAction.value = config.anti_spam_action || "mute";
  if (gsAntiSpamDeleteMessage) gsAntiSpamDeleteMessage.checked = config.anti_spam_delete_message !== false;
  if (gsAntiSpamWindowSec) gsAntiSpamWindowSec.value = String(Number(config.anti_spam_window_sec || 10));
  if (gsAntiSpamSameTextMax) gsAntiSpamSameTextMax.value = String(Number(config.anti_spam_same_text_max || 3));
  if (gsAntiSpamDifferentTextMax) gsAntiSpamDifferentTextMax.value = String(Number(config.anti_spam_different_text_max || 6));
  if (gsAntiSpamKickMinutes) gsAntiSpamKickMinutes.value = String(Number(config.anti_spam_kick_minutes || 1));
  if (gsAntiSpamMuteMinutes) gsAntiSpamMuteMinutes.value = String(Number(config.anti_spam_mute_minutes || 30));
  if (gsAntiSpamBanMinutes) gsAntiSpamBanMinutes.value = String(Number(config.anti_spam_ban_minutes || 1440));
}

function renderGroupStatuses() {
  if (!groupStatusBody) return;
  const groups = Array.from(groupConfigCache.values());
  const features = [
    "join_verification_enabled", "keyword_filter_enabled", "ad_block_enabled",
    "anti_spam_enabled", "auto_recover_enabled", "deepseek_enabled", "ai_ad_block_enabled",
  ];
  groupStatusBody.innerHTML = groups.length ? groups.map((group) => `<tr>
    <td>${escapeHtml(group.chat_id)}</td><td>${escapeHtml(group.title || "")}</td>
    ${features.map((field) => `<td>${escapeHtml(t(group[field] ? "switch_on" : "switch_off"))}</td>`).join("")}
    <td><button type="button" class="table-btn" data-open-group="${escapeHtml(group.chat_id)}">${escapeHtml(t("nav_group_settings"))}</button></td>
  </tr>`).join("") : `<tr><td colspan="10">${escapeHtml(t("no_group_data"))}</td></tr>`;
}

groupStatusBody?.addEventListener("click", (event) => {
  const button = event.target.closest("[data-open-group]");
  if (!button) return;
  showingAllManagedGroups = false;
  rememberManagedGroup(button.dataset.openGroup);
  navItems.find((item) => item.dataset.target === "group-settings")?.click();
});

async function loadGroupConfigs() {
  const request = ++groupsRequest;
  const result = await requestJson("/api/v1/groups");
  if (request !== groupsRequest) return;
  if (!result.ok || !Array.isArray(result.data)) {
    showStatus(parseApiMessage(result.data) || t("operation_failed"), true);
    return;
  }
  groupConfigCache.clear();
  for (const item of result.data) {
    groupConfigCache.set(Number(item.chat_id), item);
  }
  updateGroupControls(result.data);
  renderGroupStatuses();
  if (currentSection() === "group-settings") applyGroupSettings(gsChatId?.value || "");
}

async function saveGroupSettings() {
  const chatId = gsChatId?.value || "";
  if (!chatId || chatId !== groupSettingsLoadedChat || gsSave?.disabled) {
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
    ai_member_enabled: Boolean(gsAiMember?.checked),
    ai_reply_delete_after_seconds: Number(gsAiReplyDeleteAfterSeconds?.value || 0),
    join_verify_fail_action: gsJoinVerifyFailAction?.value || "kick",
    join_verify_fail_kick_minutes: Number(gsJoinVerifyFailKickMinutes?.value || 1),
    join_verify_fail_mute_minutes: Number(gsJoinVerifyFailMuteMinutes?.value || 30),
    join_verify_fail_ban_minutes: Number(gsJoinVerifyFailBanMinutes?.value || 1440),
    ad_block_action: gsAdBlockAction?.value || "mute",
    ad_block_delete_message: Boolean(gsAdBlockDeleteMessage?.checked),
    ad_block_apply_to_mentions: Boolean(gsAdBlockApplyToMentions?.checked),
    ad_block_kick_minutes: Number(gsAdBlockKickMinutes?.value || 1),
    ad_block_mute_minutes: Number(gsAdBlockMuteMinutes?.value || 30),
    ad_block_ban_minutes: Number(gsAdBlockBanMinutes?.value || 1440),
    ai_ad_block_enabled: Boolean(gsAiAdBlock?.checked),
    ai_ad_block_window_sec: Number(gsAiAdBlockWindowSec?.value || 60),
    ai_ad_block_high_confidence: Number(gsAiAdBlockHighConfidence?.value ?? 90),
    ai_ad_block_high_action: gsAiAdBlockHighAction?.value || "ban",
    ai_ad_block_mid_confidence: Number(gsAiAdBlockMidConfidence?.value ?? 75),
    ai_ad_block_mid_action: gsAiAdBlockMidAction?.value || "mute",
    ai_ad_block_min_confidence: Number(gsAiAdBlockMinConfidence?.value ?? 60),
    ai_ad_block_min_action: gsAiAdBlockMinAction?.value || "warn",
    ai_ad_block_punish_mentioner: Boolean(gsAiAdBlockPunishMentioner?.checked),
    ai_ad_block_mentioner_warning_limit: Number(gsAiAdBlockMentionerWarningLimit?.value || 3),
    ai_ad_block_mentioner_action: gsAiAdBlockMentionerAction?.value || "mute",
    anti_spam_action: gsAntiSpamAction?.value || "mute",
    anti_spam_delete_message: Boolean(gsAntiSpamDeleteMessage?.checked),
    anti_spam_window_sec: Number(gsAntiSpamWindowSec?.value || 10),
    anti_spam_same_text_max: Number(gsAntiSpamSameTextMax?.value || 3),
    anti_spam_different_text_max: Number(gsAntiSpamDifferentTextMax?.value || 6),
    anti_spam_kick_minutes: Number(gsAntiSpamKickMinutes?.value || 1),
    anti_spam_mute_minutes: Number(gsAntiSpamMuteMinutes?.value || 30),
    anti_spam_ban_minutes: Number(gsAntiSpamBanMinutes?.value || 1440),
  };
  gsSave.disabled = true;
  const result = await requestJson(`/api/v1/groups/${encodeURIComponent(chatId)}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (gsChatId.value === chatId) gsSave.disabled = false;
  if (!result.ok) {
    showStatus(parseApiMessage(result.data) || t("operation_failed"), true);
    return;
  }
  groupsRequest++;
  groupConfigCache.set(Number(chatId), result.data);
  renderGroupStatuses();
  showStatus(t("saved"), false);
}

async function handleSectionEnter(target) {
  syncManagedGroup(target);
  if (target === "overview") {
    formatOverviewTimes();
  } else if (target === "auto-replies") {
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
  } else if (target === "global-bans") {
    await loadGlobalBans();
  } else if (target === "group-settings" || target === "groups") {
    if (target === "group-settings") applyGroupSettings(gsChatId?.value || "");
    await loadGroupConfigs();
  }
}

navItems.forEach((item) => {
  item.addEventListener("click", async () => {
    const target = item.dataset.target;
    if (!target) return;
    if (!document.getElementById(target)) return;
    if (target === "overview" && !document.getElementById("overview")?.classList.contains("section-active")) {
      try {
        window.localStorage.setItem(ACTIVE_SECTION_KEY, target);
      } catch (err) {
        // ignore
      }
      window.location.reload();
      return;
    }
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

overviewActions.forEach((button) => {
  button.addEventListener("click", () => {
    const target = button.dataset.overviewTarget;
    const navItem = navItems.find((item) => item.dataset.target === target);
    navItem?.click();
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
restoreManagedGroup();
handleSectionEnter(initialTarget);
window.setInterval(formatOverviewTimes, 60000);

function setUpdateBusy(busy) {
  btnCheck.disabled = busy;
  if (btnTrigger) btnTrigger.disabled = busy;
}

async function pollOnlineUpdateStatus(tracking = false) {
  setUpdateBusy(true);
  const result = await requestJson("/api/v1/updates/online-status");
  if (!result.ok || !result.data?.ok) {
    if (tracking && [0, 502, 503, 504].includes(result.status)) {
      setUpgradeStatus(null, t("update_network_error"));
      window.setTimeout(() => pollOnlineUpdateStatus(true), 2500);
      return;
    }
    setUpgradeStatus(null, t("update_status_load_failed"), "failed");
  } else {
    const { state, progress, code } = result.data;
    if (state === "running") {
      setUpgradeStatus(progress, t(code, t("update_status_working")));
      window.setTimeout(() => pollOnlineUpdateStatus(true), 1500);
      return;
    }
    if (state === "success") {
      setUpgradeStatus(null, t("update_success"), "success");
    } else if (state === "failed") {
      setUpgradeStatus(null, t(code, t("update_failed_retry")), "failed");
    }
  }
  setUpdateBusy(false);
}

btnCheck?.addEventListener("click", async () => {
  setUpdateBusy(true);
  setUpgradeStatus(null, t("update_checking"));
  if (dockerUpdateInstructions) dockerUpdateInstructions.hidden = true;
  const result = await requestJson("/api/v1/updates/check");
  setUpdateBusy(false);
  const data = result.data;
  if (!result.ok || !data?.ok) {
    const detail = parseApiMessage(data);
    const message = [t("update_check_failed"), typeof detail === "string" ? detail : ""].filter(Boolean);
    setUpgradeStatus(null, message.join(" "), "failed");
    return;
  }

  let message = t("update_uptodate");
  if (data.has_update) {
    if (dockerUpdateInstructions) {
      dockerUpdateInstructions.hidden = false;
      message = t(data.compare_mode === "image" ? "update_docker_image_available" : "update_docker_available");
    } else {
      message = t(data.diverged || !btnTrigger ? "update_manual_available" : "update_available_click");
    }
  }
  if (data.local_version && data.remote_version && data.local_version !== data.remote_version) {
    message += ` ${data.local_version} → ${data.remote_version}.`;
  }
  if (data.compare_mode === "version") message += ` ${t("update_version_only")}`;
  setUpgradeStatus(null, message, data.has_update ? "normal" : "success");
});

btnTrigger?.addEventListener("click", async () => {
  setUpdateBusy(true);
  setUpgradeStatus(2, t("update_starting"));
  const result = await requestJson("/api/v1/updates/online", { method: "POST" });
  if (result.data?.ok || result.data?.code === "update_already_running") {
    await pollOnlineUpdateStatus(true);
    return;
  }
  setUpgradeStatus(null, t(result.data?.code, t("update_start_failed")), "failed");
  setUpdateBusy(false);
});

document.querySelectorAll("[data-copy-update]").forEach((button) => {
  button.addEventListener("click", async () => {
    const command = document.getElementById(button.dataset.copyUpdate);
    try {
      await navigator.clipboard.writeText(command.textContent);
      showStatus(t("update_command_copied"));
    } catch {
      const range = document.createRange();
      range.selectNodeContents(command);
      const selection = window.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
      let copied = false;
      try {
        copied = document.execCommand("copy");
      } catch {
        // Leave the command selected for manual copying.
      }
      if (copied) selection.removeAllRanges();
      showStatus(t(copied ? "update_command_copied" : "update_copy_failed"), !copied);
    }
  });
});

function activeAiProvider() {
  const checked = aiProviderRadios.find((radio) => radio.checked);
  return checked ? checked.value : "deepseek";
}

function syncAiProviderPanels() {
  const active = activeAiProvider();
  aiProviderPanels.forEach((panel) => {
    panel.hidden = panel.dataset.providerPanel !== active;
  });
  aiProviderRadios.forEach((radio) => {
    const option = radio.closest(".ai-provider-option");
    if (option) option.classList.toggle("is-active", radio.checked);
  });
}

function initAiProviderSwitch() {
  aiProviderRadios.forEach((radio) => radio.addEventListener("change", syncAiProviderPanels));
  syncAiProviderPanels();
}

const modelControls = new Map();

function readAiModelCache() {
  try {
    const value = JSON.parse(localStorage.getItem(AI_MODEL_CACHE_KEY) || "{}");
    return value && typeof value === "object" && !Array.isArray(value) ? value : {};
  } catch {
    return {};
  }
}

function writeAiModelCache(cache) {
  try {
    localStorage.setItem(AI_MODEL_CACHE_KEY, JSON.stringify(cache));
  } catch {
    // Private browsing and storage limits should not block the settings form.
  }
}

function modelCacheKey(provider, baseUrl) {
  return `${provider}|${providerBaseUrl(provider, baseUrl)}`;
}

function modelField(provider, name) {
  return document.getElementById(`rt-${provider}-${name}`);
}

function providerBaseUrl(provider, value) {
  return value.trim() || (provider === "deepseek" ? "https://api.deepseek.com" : "");
}

function initModelPickers() {
  aiProviderPanels.forEach((panel) => {
    const provider = panel.dataset.providerPanel;
    const button = modelField(provider, "fetch-models");
    const picker = modelField(provider, "model-picker");
    const input = modelField(provider, "model");
    const toggle = modelField(provider, "manual-mode");
    const manualField = modelField(provider, "manual-field");
    const feedback = modelField(provider, "models-status");
    const saved = modelField(provider, "saved-model");
    const apiKey = modelField(provider, "api-key");
    const baseUrl = modelField(provider, "base-url");
    modelControls.set(provider, { picker, input, toggle, saved, apiKey, baseUrl });
    let request = null;
    let cache = readAiModelCache();
    let cacheEntry = cache[modelCacheKey(provider, baseUrl.value)];

    function setFeedback(text, isError = false) {
      feedback.textContent = text;
      feedback.classList.toggle("is-error", isError);
    }

    function syncMode() {
      manualField.hidden = !toggle.checked;
      input.disabled = !toggle.checked;
      picker.disabled = toggle.checked || picker.options.length < 2;
    }

    function persistState() {
      const key = modelCacheKey(provider, baseUrl.value);
      cache = readAiModelCache();
      cache[key] = {
        models: Array.from(picker.options).map((option) => option.value).filter(Boolean),
        selected: picker.value,
        manual: toggle.checked,
        manualModel: input.value.trim(),
      };
      writeAiModelCache(cache);
      cacheEntry = cache[key];
    }

    function restoreState() {
      if (!cacheEntry || !Array.isArray(cacheEntry.models)) return;
      const models = [...new Set(cacheEntry.models.filter((model) => typeof model === "string" && model.trim()))];
      if (!models.length) return;
      picker.replaceChildren(new Option(t("ai_select_model"), ""), ...models.map((model) => new Option(model, model)));
      const savedModel = saved.dataset.model || "";
      const selected = models.includes(cacheEntry.selected) ? cacheEntry.selected : models.includes(savedModel) ? savedModel : "";
      picker.value = selected;
      toggle.checked = Boolean(cacheEntry.manual);
      if (toggle.checked) input.value = cacheEntry.manualModel || savedModel;
    }

    toggle.addEventListener("change", () => {
      if (toggle.checked && !input.value) input.value = picker.value || saved.dataset.model;
      syncMode();
      persistState();
      if (toggle.checked) input.focus();
    });
    picker.addEventListener("change", persistState);
    input.addEventListener("input", persistState);
    [apiKey, baseUrl].forEach((field) => {
      field.addEventListener("input", () => {
        request?.abort();
        request = null;
        button.disabled = false;
        cache = readAiModelCache();
        Object.keys(cache)
          .filter((key) => key.startsWith(`${provider}|`))
          .forEach((key) => delete cache[key]);
        cacheEntry = null;
        writeAiModelCache(cache);
        picker.replaceChildren(new Option(t("ai_models_fetch_first"), ""));
        setFeedback("");
        syncMode();
      });
    });
    button.addEventListener("click", async () => {
      const controller = new AbortController();
      request = controller;
      button.disabled = true;
      setFeedback(t("ai_models_fetching"));
      const result = await requestJson("/api/v1/ai/models", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ provider, api_key: apiKey.value, base_url: providerBaseUrl(provider, baseUrl.value) }),
        signal: controller.signal,
      });
      if (request !== controller) return;
      request = null;
      button.disabled = false;
      if (!result.ok) {
        setFeedback(parseApiMessage(result.data) || t("ai_models_failed"), true);
        return;
      }

      const models = Array.isArray(result.data?.models) ? result.data.models : [];
      const previous = picker.value || saved.dataset.model;
      const selected = models.includes(previous) ? previous : saved.dataset.model;
      const placeholder = models.length ? t("ai_select_model") : t("ai_models_empty");
      picker.replaceChildren(new Option(placeholder, ""), ...models.map((model) => new Option(model, model)));
      picker.value = models.includes(selected) ? selected : "";
      syncMode();
      persistState();
      setFeedback(models.length ? `${t("ai_models_loaded")} (${models.length})` : "");
    });
    restoreState();
    syncMode();
  });
}

async function saveRuntimeFields(button, payload) {
  button.disabled = true;
  const result = await requestJson("/api/v1/runtime", {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  button.disabled = false;
  if (!result.ok) {
    const detail = parseApiMessage(result.data);
    const message = Array.isArray(detail) ? detail.map((item) => item.msg).filter(Boolean).join(" ") : detail;
    showStatus(message || t("operation_failed"), true);
    return null;
  }
  showStatus(t("saved"), false);
  return result.data;
}

btnSaveRuntime?.addEventListener("click", () => {
  saveRuntimeFields(btnSaveRuntime, {
    telegram_bot_token: rtTelegramBotToken?.value || "",
    telegram_bot_username: rtTelegramBotUsername?.value || "",
    telegram_admin_ids: rtTelegramAdminIds?.value || "",
    join_verify_timeout_sec: Number(rtJoinVerifyTimeoutSec?.value || 180),
    spam_window_sec: Number(rtSpamWindowSec?.value || 10),
    spam_max_messages: Number(rtSpamMaxMessages?.value || 6),
  });
});

btnSaveAi?.addEventListener("click", async () => {
  const active = activeAiProvider();
  const payload = {
    deepseek_timeout_sec: Number(rtAiTimeoutSec?.value || 30),
    ai_provider: active,
    ai_temperature: Number(rtAiTemperature?.value || 0.3),
    ai_max_tokens: Number(rtAiMaxTokens?.value || 0),
    ai_system_prompt: rtAiSystemPrompt?.value || "",
  };
  for (const [provider, fields] of modelControls) {
    const { picker, input, toggle, saved, apiKey, baseUrl } = fields;
    const model = toggle.checked ? input.value.trim() : picker.value;
    if (!model && (toggle.checked || (provider === active && (!saved.dataset.model || picker.options.length > 1)))) {
      showStatus(t(toggle.checked ? "ai_model_manual_required" : "ai_model_required"), true);
      aiProviderRadios.find((radio) => radio.value === provider).checked = true;
      syncAiProviderPanels();
      const target = toggle.checked ? input : picker.disabled ? modelField(provider, "fetch-models") : picker;
      target.focus();
      return;
    }
    if (model) payload[`${provider}_model`] = model;
    payload[`${provider}_api_key`] = apiKey.value;
    payload[`${provider}_base_url`] = providerBaseUrl(provider, baseUrl.value);
  }
  const config = await saveRuntimeFields(btnSaveAi, payload);
  if (!config) return;
  modelControls.forEach(({ saved }, provider) => {
    const model = config[`${provider}_model`];
    saved.dataset.model = model;
    saved.textContent = model || t("ai_no_saved_model");
  });
});

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
kwModalMuteUser?.addEventListener("change", () => syncKeywordActionFields("mute"));
kwModalBanUser?.addEventListener("change", () => syncKeywordActionFields("ban"));

kwModalSave?.addEventListener("click", async () => {
  const chatId = kwChatId?.value || "";
  if (!chatId) {
    showStatus(t("select_group"), true);
    return;
  }
  const muteMinutesRaw = (kwModalMuteMinutes?.value || "").trim();
  const banMinutesRaw = (kwModalBanMinutes?.value || "").trim();
  const payload = {
    chat_id: Number(chatId),
    keyword: (kwModalKeyword?.value || "").trim(),
    delete_message: Boolean(kwModalDeleteMessage?.checked),
    mute_user: Boolean(kwModalMuteUser?.checked),
    mute_minutes: Number(muteMinutesRaw || 10),
    ban_user: Boolean(kwModalBanUser?.checked),
    ban_minutes: Number(banMinutesRaw || 1440),
    enabled: Boolean(kwModalEnabled?.checked),
  };
  if (!payload.keyword) {
    showStatus(t("fill_required_fields"), true);
    return;
  }
  if (!payload.delete_message && !payload.mute_user && !payload.ban_user) {
    showStatus(t("keyword_actions_required"), true);
    return;
  }
  if (
    (payload.mute_user && (!muteMinutesRaw || !isValidModerationDuration(payload.mute_minutes))) ||
    (payload.ban_user && (!banMinutesRaw || !isValidModerationDuration(payload.ban_minutes)))
  ) {
    showStatus(t("keyword_duration_invalid"), true);
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
        delete_message: payload.delete_message,
        mute_user: payload.mute_user,
        mute_minutes: payload.mute_minutes,
        ban_user: payload.ban_user,
        ban_minutes: payload.ban_minutes,
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
    const actionState = keywordActionState(found);
    if (kwModalDeleteMessage) kwModalDeleteMessage.checked = actionState.deleteMessage;
    if (kwModalMuteUser) kwModalMuteUser.checked = actionState.muteUser;
    if (kwModalBanUser) kwModalBanUser.checked = actionState.banUser;
    if (kwModalMuteMinutes) kwModalMuteMinutes.value = String(Number(found.mute_minutes || 10));
    if (kwModalBanMinutes) kwModalBanMinutes.value = String(Number(found.ban_minutes || 1440));
    if (kwModalEnabled) kwModalEnabled.checked = Boolean(found.enabled);
    syncKeywordActionFields(actionState.banUser ? "ban" : actionState.muteUser ? "mute" : "");
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
akModalMuteUser?.addEventListener("change", () => syncAdKeywordActionFields("mute"));
akModalBanUser?.addEventListener("change", () => syncAdKeywordActionFields("ban"));

akModalSave?.addEventListener("click", async () => {
  const chatId = akChatId?.value || "";
  if (!chatId) {
    showStatus(t("select_group"), true);
    return;
  }
  const muteMinutesRaw = (akModalMuteMinutes?.value || "").trim();
  const banMinutesRaw = (akModalBanMinutes?.value || "").trim();
  const payload = {
    chat_id: Number(chatId),
    keyword: (akModalKeyword?.value || "").trim(),
    delete_message: Boolean(akModalDeleteMessage?.checked),
    mute_user: Boolean(akModalMuteUser?.checked),
    mute_minutes: Number(muteMinutesRaw || 30),
    ban_user: Boolean(akModalBanUser?.checked),
    ban_minutes: Number(banMinutesRaw || 1440),
    apply_to_mentions: Boolean(akModalApplyToMentions?.checked),
    enabled: Boolean(akModalEnabled?.checked),
  };
  if (!payload.keyword) {
    showStatus(t("fill_required_fields"), true);
    return;
  }
  if (payload.apply_to_mentions && !payload.mute_user && !payload.ban_user) {
    showStatus(t("ad_keyword_mentions_penalty_required"), true);
    return;
  }
  if (!payload.delete_message && !payload.mute_user && !payload.ban_user) {
    showStatus(t("ad_keyword_actions_required"), true);
    return;
  }
  if (
    (payload.mute_user && (!muteMinutesRaw || !isValidModerationDuration(payload.mute_minutes))) ||
    (payload.ban_user && (!banMinutesRaw || !isValidModerationDuration(payload.ban_minutes)))
  ) {
    showStatus(t("ad_keyword_duration_invalid"), true);
    return;
  }

  const isEditing = akEditingKeywordId !== null;
  const url = isEditing
    ? `/api/v1/groups/${encodeURIComponent(chatId)}/ad-keywords/${encodeURIComponent(String(akEditingKeywordId))}`
    : `/api/v1/groups/${encodeURIComponent(chatId)}/ad-keywords`;
  const method = isEditing ? "PATCH" : "POST";
  const bodyPayload = isEditing
    ? {
        keyword: payload.keyword,
        delete_message: payload.delete_message,
        mute_user: payload.mute_user,
        mute_minutes: payload.mute_minutes,
        ban_user: payload.ban_user,
        ban_minutes: payload.ban_minutes,
        apply_to_mentions: payload.apply_to_mentions,
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
  closeModal(akModal);
  showStatus(t("saved"), false);
  await loadAdKeywords();
});

akRefresh?.addEventListener("click", loadAdKeywords);
akChatId?.addEventListener("change", loadAdKeywords);

function syncAdTemplateActionFields(preferredPenalty = "") {
  if (preferredPenalty === "mute" && aktMuteUser?.checked && aktBanUser) {
    aktBanUser.checked = false;
  } else if (preferredPenalty === "ban" && aktBanUser?.checked && aktMuteUser) {
    aktMuteUser.checked = false;
  } else if (aktMuteUser?.checked && aktBanUser?.checked) {
    aktMuteUser.checked = false;
  }

  const muteEnabled = Boolean(aktMuteUser?.checked);
  const banEnabled = Boolean(aktBanUser?.checked);
  if (aktMuteMinutesField) aktMuteMinutesField.hidden = !muteEnabled;
  if (aktMuteMinutes) aktMuteMinutes.disabled = !muteEnabled;
  if (aktBanMinutesField) aktBanMinutesField.hidden = !banEnabled;
  if (aktBanMinutes) aktBanMinutes.disabled = !banEnabled;
}

function resetAdTemplateModal() {
  if (aktDeleteMessage) aktDeleteMessage.checked = true;
  if (aktMuteUser) aktMuteUser.checked = false;
  if (aktBanUser) aktBanUser.checked = false;
  if (aktMuteMinutes) aktMuteMinutes.value = "30";
  if (aktBanMinutes) aktBanMinutes.value = "1440";
  syncAdTemplateActionFields();
}

async function loadAdTemplates() {
  if (!aktList) return;
  const chatId = akChatId?.value || "";
  if (!chatId) {
    aktList.innerHTML = "";
    return;
  }
  const result = await requestJson(`/api/v1/groups/${encodeURIComponent(chatId)}/ad-keywords/templates`);
  if (!result.ok || !Array.isArray(result.data)) {
    showStatus(parseApiMessage(result.data) || t("operation_failed"), true);
    aktList.innerHTML = "";
    return;
  }
  aktList.innerHTML = result.data
    .map((item) => {
      const strict = item.risk === "strict";
      const name = t(`ad_tpl_${item.id}_name`, item.id);
      const desc = t(`ad_tpl_${item.id}_desc`, "");
      const riskLabel = t(strict ? "ad_template_risk_strict" : "ad_template_risk_standard");
      const imported =
        item.imported_count > 0
          ? ` · ${t("ad_template_imported")} ${item.imported_count}/${item.keyword_count}`
          : "";
      return `<label class="check-card check-card-detail">
        <input type="checkbox" class="akt-template-check" value="${escapeHtml(item.id)}" />
        <span class="check-card-copy">
          <span>${escapeHtml(name)} <span class="ad-action-tag${strict ? " ad-template-strict" : ""}">${escapeHtml(riskLabel)}</span></span>
          <small>${escapeHtml(desc)}</small>
          <small>${item.keyword_count} ${escapeHtml(t("ad_template_words"))}${escapeHtml(imported)}</small>
        </span>
      </label>`;
    })
    .join("");
}

aktOpen?.addEventListener("click", async () => {
  if (!akChatId?.value) {
    showStatus(t("select_group"), true);
    return;
  }
  resetAdTemplateModal();
  openModal(aktModal);
  await loadAdTemplates();
});

aktCancel?.addEventListener("click", () => closeModal(aktModal));
aktModalClose?.addEventListener("click", () => closeModal(aktModal));
aktModal?.addEventListener("click", (event) => {
  if (event.target === aktModal) closeModal(aktModal);
});
aktMuteUser?.addEventListener("change", () => syncAdTemplateActionFields("mute"));
aktBanUser?.addEventListener("change", () => syncAdTemplateActionFields("ban"));

aktApply?.addEventListener("click", async () => {
  const chatId = akChatId?.value || "";
  if (!chatId) {
    showStatus(t("select_group"), true);
    return;
  }
  const templateIds = Array.from(aktList?.querySelectorAll(".akt-template-check:checked") || []).map((el) => el.value);
  if (!templateIds.length) {
    showStatus(t("ad_template_none_selected"), true);
    return;
  }
  const muteMinutesRaw = (aktMuteMinutes?.value || "").trim();
  const banMinutesRaw = (aktBanMinutes?.value || "").trim();
  const payload = {
    template_ids: templateIds,
    delete_message: Boolean(aktDeleteMessage?.checked),
    mute_user: Boolean(aktMuteUser?.checked),
    mute_minutes: Number(muteMinutesRaw || 30),
    ban_user: Boolean(aktBanUser?.checked),
    ban_minutes: Number(banMinutesRaw || 1440),
    apply_to_mentions: false,
  };
  if (!payload.delete_message && !payload.mute_user && !payload.ban_user) {
    showStatus(t("ad_keyword_actions_required"), true);
    return;
  }
  if (
    (payload.mute_user && (!muteMinutesRaw || !isValidModerationDuration(payload.mute_minutes))) ||
    (payload.ban_user && (!banMinutesRaw || !isValidModerationDuration(payload.ban_minutes)))
  ) {
    showStatus(t("ad_keyword_duration_invalid"), true);
    return;
  }

  const result = await requestJson(`/api/v1/groups/${encodeURIComponent(chatId)}/ad-keywords/templates/apply`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!result.ok) {
    showStatus(parseApiMessage(result.data) || t("operation_failed"), true);
    return;
  }
  closeModal(aktModal);
  const summary = result.data || {};
  showStatus(
    `${t("ad_template_done")}: ${summary.added_keywords || 0} ${t("ad_template_added")} ` +
      `(${summary.created_rules || 0} ${t("ad_template_rules")}), ${t("ad_template_skipped")} ${summary.skipped_keywords || 0}`,
    false,
  );
  await loadAdKeywords();
});

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
    if (akModalDeleteMessage) akModalDeleteMessage.checked = found.delete_message !== false;
    if (akModalMuteUser) akModalMuteUser.checked = Boolean(found.mute_user);
    if (akModalBanUser) akModalBanUser.checked = Boolean(found.ban_user);
    if (akModalApplyToMentions) akModalApplyToMentions.checked = Boolean(found.apply_to_mentions);
    if (akModalMuteMinutes) akModalMuteMinutes.value = String(Number(found.mute_minutes || 30));
    if (akModalBanMinutes) akModalBanMinutes.value = String(Number(found.ban_minutes || 1440));
    if (akModalEnabled) akModalEnabled.checked = Boolean(found.enabled);
    syncAdKeywordActionFields(found.ban_user ? "ban" : found.mute_user ? "mute" : "");
    openModal(akModal);
  }
});

gsChatId?.addEventListener("change", () => applyGroupSettings(gsChatId.value));
gsSave?.addEventListener("click", saveGroupSettings);
gsRefresh?.addEventListener("click", loadGroupConfigs);

cmChatId?.addEventListener("change", async () => {
  await loadCommunityConfig();
});
cmSection?.addEventListener("click", async (event) => {
  const target = event.target;
  if (!(target instanceof Element)) return;
  const button = target.closest(".cm-config-save");
  if (!(button instanceof HTMLButtonElement)) return;
  await saveCommunityConfig(button);
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
  if (!chatId || chatId !== communityLoadedChat || !name) return;
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
  if (!chatId || chatId !== communityLoadedChat || !url) return;
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
  if (result.data?.failed?.length) {
    showStatus(`${t("global_unban_partial")} (${result.data.failed.length})`, true);
  }
  if (result.data?.legacy_groups?.length) {
    showStatus(`${t("global_unban_legacy")} · ${result.data.legacy_groups.slice(0, 10).join(", ")}`, true);
  }
  if (!result.data?.failed?.length && !result.data?.legacy_groups?.length) {
    showStatus(t("saved"), false);
  }
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

initAiProviderSwitch();
initModelPickers();

if (btnTrigger) pollOnlineUpdateStatus();

let checkingRuntimeHealth = false;

function renderHealth(id, state, timestamp) {
  const label = document.getElementById(id);
  if (!label) return;
  const labels = {
    online: "overview_online",
    not_configured: "overview_not_configured",
    starting: "health_starting",
    error: "health_error",
    untested: "health_untested",
  };
  let description = t(labels[state] || "overview_unknown");
  if (timestamp) {
    const date = new Date(timestamp);
    if (Number.isFinite(date.valueOf())) description += ` · ${date.toLocaleString()}`;
  }
  label.textContent = description;
  label.closest("li")?.querySelectorAll(".overview-status-dot, .overview-service-icon").forEach((indicator) => {
    indicator.classList.toggle("is-good", state === "online");
    indicator.classList.toggle("is-warning", state !== "online");
  });
}

async function refreshRuntimeHealth() {
  if (checkingRuntimeHealth || document.hidden) return;
  checkingRuntimeHealth = true;
  const result = await requestJson("/api/v1/status");
  checkingRuntimeHealth = false;
  const healthy = result.ok && result.data?.database && result.data?.bot?.state !== "error"
    && result.data?.ai?.state !== "error";
  for (const id of ["health-summary", "health-overview"]) {
    const element = document.getElementById(id);
    if (element) {
      element.textContent = t(healthy ? "system_running" : "health_degraded");
      element.dataset.state = healthy ? "online" : "error";
    }
  }
  renderHealth("health-database", result.data?.database ? "online" : "error");
  renderHealth("health-bot", result.data?.bot?.state, result.data?.bot?.last_success);
  renderHealth("health-ai", result.data?.ai?.state, result.data?.ai?.checked_at);
}

refreshRuntimeHealth();
window.setInterval(refreshRuntimeHealth, 15000);

from typing import Any


SUPPORTED_LANGS = {"zh", "en"}
DEFAULT_LANG = "zh"

TRANSLATIONS: dict[str, dict[str, str]] = {
    "zh": {
        "dashboard_title": "Miyin TG 机器人后台",
        "admin_dashboard": "管理后台",
        "logout": "退出登录",
        "groups": "群组数量",
        "keyword_rules": "关键词规则",
        "moderation_logs": "风控日志",
        "update_control": "更新控制",
        "check_update": "检查更新",
        "online_update": "在线升级",
        "ready": "就绪",
        "login_protection": "登录安全",
        "token_expire_desc": "登录成功后 token 有效期为 10 天。",
        "enable_temp_ban": "开启连续登录失败临时封禁",
        "max_failed_attempts": "最大失败次数",
        "ban_minutes": "封禁分钟数",
        "save_login_security": "保存登录安全设置",
        "web_language": "Web 显示语言",
        "lang_zh": "中文",
        "lang_en": "英文",
        "connected_groups": "已接入群组",
        "chat_id": "群组ID",
        "title": "标题",
        "join_verify": "入群验证",
        "keyword_filter": "关键词过滤",
        "ad_block": "广告拦截",
        "anti_spam": "防刷屏",
        "auto_recover": "自动恢复",
        "ai": "AI",
        "switch_on": "开",
        "switch_off": "关",
        "no_group_data": "暂无群组数据。",
        "login_title": "Miyin TG 管理登录",
        "admin_login": "管理员登录",
        "password_label": "密码",
        "login_btn": "登录",
        "login_error_password": "密码错误",
        "login_error_too_many_attempts": "登录失败次数过多，请 {minutes} 分钟后再试。",
        "update_status_load_failed": "加载升级状态失败。",
        "update_status_working": "升级进行中...",
        "update_success_refreshing": "升级成功，正在刷新页面...",
        "update_failed_retry": "升级失败，请重试。",
        "update_ready": "就绪。",
        "update_checking": "正在检查版本...",
        "update_check_failed": "版本检查失败。",
        "update_available_click": "发现新版本，点击在线升级。",
        "update_uptodate": "当前已是最新版本。",
        "update_starting": "正在启动在线升级...",
        "update_start_failed": "启动在线升级失败。",
        "update_network_error": "网络错误，无法获取升级状态。",
        "security_saving": "保存中...",
    },
    "en": {
        "dashboard_title": "Miyin TG Bot Dashboard",
        "admin_dashboard": "Admin dashboard",
        "logout": "Logout",
        "groups": "Groups",
        "keyword_rules": "Keyword Rules",
        "moderation_logs": "Moderation Logs",
        "update_control": "Update Control",
        "check_update": "Check Update",
        "online_update": "Online Update",
        "ready": "Ready",
        "login_protection": "Login Protection",
        "token_expire_desc": "Token expires in 10 days after successful login.",
        "enable_temp_ban": "Enable temporary ban after multiple failed logins",
        "max_failed_attempts": "Max failed attempts",
        "ban_minutes": "Ban minutes",
        "save_login_security": "Save Login Security",
        "web_language": "Web Language",
        "lang_zh": "Chinese",
        "lang_en": "English",
        "connected_groups": "Connected Groups",
        "chat_id": "Chat ID",
        "title": "Title",
        "join_verify": "Join Verify",
        "keyword_filter": "Keyword Filter",
        "ad_block": "Ad Block",
        "anti_spam": "Anti Spam",
        "auto_recover": "Auto Recover",
        "ai": "AI",
        "switch_on": "on",
        "switch_off": "off",
        "no_group_data": "No group data yet.",
        "login_title": "Miyin TG Admin Login",
        "admin_login": "Admin Login",
        "password_label": "Password",
        "login_btn": "Login",
        "login_error_password": "Incorrect password",
        "login_error_too_many_attempts": "Too many failed attempts. Try again in {minutes} minutes.",
        "update_status_load_failed": "Failed to load update status.",
        "update_status_working": "Update is running...",
        "update_success_refreshing": "Update successful. Refreshing...",
        "update_failed_retry": "Update failed. Please retry.",
        "update_ready": "Ready.",
        "update_checking": "Checking versions...",
        "update_check_failed": "Version check failed.",
        "update_available_click": "Update available. Click Online Update.",
        "update_uptodate": "Already up to date.",
        "update_starting": "Starting online update...",
        "update_start_failed": "Failed to start update.",
        "update_network_error": "Network error while checking update status.",
        "security_saving": "Saving...",
    },
}


def normalize_language(lang: str | None) -> str:
    if not lang:
        return DEFAULT_LANG
    candidate = lang.strip().lower()
    if candidate not in SUPPORTED_LANGS:
        return DEFAULT_LANG
    return candidate


def get_translations(lang: str) -> dict[str, str]:
    normalized = normalize_language(lang)
    return TRANSLATIONS.get(normalized, TRANSLATIONS[DEFAULT_LANG]).copy()


def tr(lang: str, key: str, **kwargs: Any) -> str:
    bundle = get_translations(lang)
    template = bundle.get(key, key)
    if kwargs:
        try:
            return template.format(**kwargs)
        except Exception:
            return template
    return template


import re
from html import escape

from aiogram.types import Message

TELEGRAM_TEXT_LIMIT = 4096
AI_REPLY_LIMIT = 3800


def _format_inline(text: str) -> str:
    escaped = escape(text)
    escaped = re.sub(r"`([^`\n]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*\n]+)\*\*", r"<b>\1</b>", escaped)
    escaped = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<i>\1</i>", escaped)
    return escaped


def ai_text_to_html(text: str) -> str:
    raw = (text or "").strip()
    if not raw:
        return "<i>AI 没有返回内容。</i>"

    parts = re.split(r"(```[\s\S]*?```)", raw[:AI_REPLY_LIMIT])
    output: list[str] = ["<b>AI 回复</b>"]

    for part in parts:
        if not part:
            continue
        if part.startswith("```") and part.endswith("```"):
            code = part[3:-3].strip()
            if "\n" in code:
                first_line, rest = code.split("\n", 1)
                if first_line.strip() and re.fullmatch(r"[A-Za-z0-9_+.#-]{1,24}", first_line.strip()):
                    code = rest
            output.append(f"<pre><code>{escape(code[:3000])}</code></pre>")
            continue

        lines: list[str] = []
        for line in part.splitlines():
            stripped = line.strip()
            if not stripped:
                lines.append("")
                continue
            heading = re.match(r"^(#{1,4})\s+(.+)$", stripped)
            if heading:
                lines.append(f"<b>{_format_inline(heading.group(2))}</b>")
                continue
            bullet = re.match(r"^[-*]\s+(.+)$", stripped)
            if bullet:
                lines.append(f"- {_format_inline(bullet.group(1))}")
                continue
            numbered = re.match(r"^\d+[.)]\s+(.+)$", stripped)
            if numbered:
                lines.append(f"- {_format_inline(numbered.group(1))}")
                continue
            lines.append(_format_inline(line))
        output.append("\n".join(lines).strip())

    return "\n\n".join(item for item in output if item).strip()[:TELEGRAM_TEXT_LIMIT]


async def reply_ai_text(message: Message, text: str) -> Message | None:
    html = ai_text_to_html(text)
    try:
        return await message.reply(html, parse_mode="HTML")
    except Exception:
        return await message.reply((text or "AI 没有返回内容。")[:AI_REPLY_LIMIT])

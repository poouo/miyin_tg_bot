import logging

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.services.runtime_config_service import get_runtime_config
from apps.api.app.services.runtime_health import record_ai

logger = logging.getLogger(__name__)


class DeepSeekClient:
    """OpenAI compatible chat client.

    The provider used at runtime (DeepSeek official / OpenCode / any OpenAI
    compatible endpoint) is chosen in the dashboard and resolved from the
    runtime configuration, so adding a provider needs no code change here.
    """

    async def ask(self, question: str, system_prompt: str | None = None, db: AsyncSession | None = None) -> str:
        runtime = await get_runtime_config(db)
        credentials = runtime.ai_credentials

        if not credentials.api_key:
            return f"{credentials.label} API Key 未配置，请先在后台「AI 接口配置」中填写。"
        if not credentials.base_url:
            return f"{credentials.label} Base URL 未配置，请先在后台「AI 接口配置」中填写。"

        prompt = (system_prompt or credentials.system_prompt or "").strip()
        messages: list[dict[str, str]] = []
        if prompt:
            messages.append({"role": "system", "content": prompt})
        messages.append({"role": "user", "content": question})

        payload: dict[str, object] = {
            "model": credentials.model,
            "messages": messages,
            "temperature": credentials.temperature,
        }
        if credentials.max_tokens > 0:
            payload["max_tokens"] = credentials.max_tokens

        headers = {
            "Authorization": f"Bearer {credentials.api_key}",
            "Content-Type": "application/json",
        }
        url = f"{credentials.base_url.rstrip('/')}/chat/completions"

        try:
            async with httpx.AsyncClient(timeout=credentials.timeout_sec) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as exc:
            record_ai(credentials, False)
            logger.warning("AI request failed (%s %s): HTTP %s", credentials.label, url, exc.response.status_code)
            return (
                f"{credentials.label} 接口返回错误（HTTP {exc.response.status_code}），"
                "请检查 API Key、Base URL 与模型名称。"
            )
        except Exception as exc:
            record_ai(credentials, False)
            logger.warning("AI request failed (%s %s): %s", credentials.label, url, exc)
            return f"{credentials.label} 接口请求失败，请检查 Base URL、网络与超时设置。"

        try:
            content = data["choices"][0]["message"]["content"]
            if not isinstance(content, str) or not content.strip():
                raise ValueError("empty AI content")
            record_ai(credentials, True)
            return content.strip()
        except (KeyError, IndexError, TypeError, AttributeError, ValueError):
            record_ai(credentials, False)
            logger.warning("Unexpected AI response from %s: %s", url, str(data)[:400])
            return "AI 返回格式异常，请确认该接口兼容 OpenAI Chat Completions 协议。"

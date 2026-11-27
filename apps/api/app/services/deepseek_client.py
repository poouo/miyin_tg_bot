import logging
from typing import Literal

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.services.runtime_config_service import get_runtime_config
from apps.api.app.services.runtime_health import record_ai

logger = logging.getLogger(__name__)
CompletionMode = Literal["chat", "review_json", "review_text"]
OFFICIAL_DEEPSEEK_ENDPOINTS = {"https://api.deepseek.com", "https://api.deepseek.com/v1"}


class AICompletionError(RuntimeError):
    def __init__(self, message: str, *, retry_review: bool = False) -> None:
        super().__init__(message)
        self.retry_review = retry_review


class DeepSeekClient:
    """OpenAI compatible chat client.

    The provider used at runtime (DeepSeek official / OpenCode / any OpenAI
    compatible endpoint) is chosen in the dashboard and resolved from the
    runtime configuration, so adding a provider needs no code change here.
    """

    async def ask(
        self,
        question: str,
        system_prompt: str | None = None,
        db: AsyncSession | None = None,
        *,
        mode: CompletionMode = "chat",
    ) -> str:
        try:
            return await self.complete(question, system_prompt, db, mode=mode)
        except AICompletionError as exc:
            if mode != "chat":
                raise
            return str(exc)

    async def complete(
        self,
        question: str,
        system_prompt: str | None = None,
        db: AsyncSession | None = None,
        *,
        mode: CompletionMode = "chat",
    ) -> str:
        runtime = await get_runtime_config(db)
        credentials = runtime.ai_credentials

        if not credentials.api_key:
            raise AICompletionError(f"{credentials.label} API Key 未配置，请先在后台「AI 接口配置」中填写。")
        if not credentials.base_url:
            raise AICompletionError(f"{credentials.label} Base URL 未配置，请先在后台「AI 接口配置」中填写。")
        if not credentials.model:
            raise AICompletionError(f"{credentials.label} 模型未配置，请先在后台「AI 接口配置」中选择模型。")

        prompt = (system_prompt or credentials.system_prompt or "").strip()
        messages: list[dict[str, str]] = []
        if prompt:
            messages.append({"role": "system", "content": prompt})
        messages.append({"role": "user", "content": question})

        payload: dict[str, object] = {
            "model": credentials.model,
            "messages": messages,
        }
        base_url = credentials.base_url.rstrip("/")
        if mode == "chat":
            payload["temperature"] = credentials.temperature
            if credentials.max_tokens > 0:
                payload["max_tokens"] = credentials.max_tokens
        elif mode == "review_json":
            payload["max_tokens"] = 2048
            payload["response_format"] = {"type": "json_object"}
            if base_url.lower() in OFFICIAL_DEEPSEEK_ENDPOINTS:
                payload["thinking"] = {"type": "disabled"}
        else:
            payload["max_tokens"] = 4096

        headers = {
            "Authorization": f"Bearer {credentials.api_key}",
            "Content-Type": "application/json",
        }
        url = f"{base_url}/chat/completions"

        try:
            async with httpx.AsyncClient(timeout=credentials.timeout_sec) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as exc:
            record_ai(credentials, False)
            status = exc.response.status_code
            logger.warning("AI request failed (%s %s, %s): HTTP %s", credentials.label, credentials.model, mode, status)
            raise AICompletionError(
                f"{credentials.label} 接口返回错误（HTTP {status}），请检查 API Key、Base URL 与模型名称。",
                retry_review=status in {400, 415, 422},
            ) from exc
        except Exception as exc:
            record_ai(credentials, False)
            logger.warning("AI request failed (%s %s, %s): %s", credentials.label, credentials.model, mode, type(exc).__name__)
            raise AICompletionError(f"{credentials.label} 接口请求失败，请检查 Base URL、网络与超时设置。") from exc

        try:
            choice = data["choices"][0]
            content = choice["message"]["content"]
            finish_reason = choice.get("finish_reason")
        except (KeyError, IndexError, TypeError, AttributeError) as exc:
            record_ai(credentials, False)
            logger.warning("Invalid AI response structure (%s %s, %s)", credentials.label, credentials.model, mode)
            raise AICompletionError("AI 返回格式异常，请确认该接口兼容 OpenAI Chat Completions 协议。") from exc

        empty = not isinstance(content, str) or not content.strip()
        if finish_reason == "length" and (mode != "chat" or empty):
            record_ai(credentials, False)
            raise AICompletionError("AI 输出达到 Token 上限，请检查模型和输出 Token 设置。", retry_review=True)
        if finish_reason == "content_filter":
            record_ai(credentials, False)
            raise AICompletionError("AI 服务商的内容过滤拦截了这次请求。")
        if empty:
            record_ai(credentials, False)
            raise AICompletionError("AI 服务商返回了空回复，请检查模型和输出 Token 设置。", retry_review=True)

        record_ai(credentials, True)
        return content.strip()

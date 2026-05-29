import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.services.runtime_config_service import get_runtime_config


class DeepSeekClient:
    async def ask(self, question: str, system_prompt: str | None = None, db: AsyncSession | None = None) -> str:
        runtime = await get_runtime_config(db)
        if not runtime.deepseek_api_key:
            return "DeepSeek API Key 未配置，请先在后台设置。"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": question})

        payload = {
            "model": runtime.deepseek_model,
            "messages": messages,
            "temperature": 0.3,
        }

        headers = {
            "Authorization": f"Bearer {runtime.deepseek_api_key}",
            "Content-Type": "application/json",
        }

        url = f"{runtime.deepseek_base_url.rstrip('/')}/chat/completions"
        async with httpx.AsyncClient(timeout=runtime.deepseek_timeout_sec) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
        return data["choices"][0]["message"]["content"].strip()

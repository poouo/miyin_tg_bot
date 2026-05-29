import httpx

from packages.shared.shared.config.settings import settings


class DeepSeekClient:
    def __init__(self) -> None:
        self.base_url = settings.deepseek_base_url.rstrip("/")
        self.api_key = settings.deepseek_api_key
        self.model = settings.deepseek_model
        self.timeout = settings.deepseek_timeout_sec

    async def ask(self, question: str, system_prompt: str | None = None) -> str:
        if not self.api_key:
            return "DeepSeek API Key 未配置，请先在 .env 中设置 DEEPSEEK_API_KEY。"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": question})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        url = f"{self.base_url}/chat/completions"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
        return data["choices"][0]["message"]["content"].strip()


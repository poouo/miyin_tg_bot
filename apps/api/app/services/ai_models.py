"""Discover the model catalog of an OpenAI compatible endpoint."""

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT_SEC = 15
# Path segments some gateways keep outside the OpenAI compatible prefix.
OPENAI_PREFIX_MARKERS = ("/openai/v1", "/openai")


def _candidate_model_urls(base_url: str) -> list[str]:
    base = (base_url or "").strip().rstrip("/")
    if not base:
        return []
    urls = [f"{base}/models"]
    for marker in OPENAI_PREFIX_MARKERS:
        if base.endswith(marker):
            # OpenCode example: .../inference/openai/v1 -> .../inference/v1/models
            urls.append(f"{base[: -len(marker)]}/v1/models")
            break
    unique: list[str] = []
    for url in urls:
        if url not in unique:
            unique.append(url)
    return unique


def _extract_model_ids(payload: Any) -> list[str]:
    items: Any = None
    if isinstance(payload, dict):
        for key in ("data", "models", "items"):
            if isinstance(payload.get(key), list):
                items = payload[key]
                break
        if items is None and isinstance(payload.get("id"), str):
            items = [payload]
    elif isinstance(payload, list):
        items = payload
    if not isinstance(items, list):
        return []

    model_ids: list[str] = []
    for item in items:
        if isinstance(item, str):
            candidate = item.strip()
        elif isinstance(item, dict):
            raw = item.get("id") or item.get("name") or item.get("model")
            candidate = str(raw).strip() if raw else ""
        else:
            candidate = ""
        if candidate and candidate not in model_ids:
            model_ids.append(candidate)
    return model_ids


async def fetch_model_ids(
    base_url: str,
    api_key: str = "",
    timeout: float = DEFAULT_TIMEOUT_SEC,
) -> tuple[list[str], str]:
    """Return (sorted_model_ids, url_that_answered) for an OpenAI compatible endpoint."""
    candidates = _candidate_model_urls(base_url)
    if not candidates:
        raise ValueError("Base URL 未配置")

    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    last_error = ""
    async with httpx.AsyncClient(timeout=timeout) as client:
        for url in candidates:
            try:
                response = await client.get(url, headers=headers)
            except Exception as exc:  # network / timeout / invalid host
                logger.warning("Model list request failed (%s): %s", url, exc)
                last_error = "请求失败"
                continue
            if response.status_code >= 400:
                last_error = f"HTTP {response.status_code}"
                continue
            try:
                payload = response.json()
            except Exception:
                last_error = "返回内容不是 JSON"
                continue
            model_ids = _extract_model_ids(payload)
            if model_ids:
                return sorted(model_ids, key=str.lower), url
            last_error = "返回内容中没有模型列表"

    raise ValueError(f"无法获取模型列表（{last_error or '接口无响应'}）")

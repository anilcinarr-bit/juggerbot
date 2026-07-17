import httpx

from app.config import settings


async def generate(prompt: str, system: str | None = None) -> str:
    """Ollama /api/generate endpoint'ine istek atar, düz metin döner."""
    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
    }
    if system:
        payload["system"] = system

    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(f"{settings.ollama_base_url}/api/generate", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "").strip()

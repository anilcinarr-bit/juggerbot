from app.llm.ollama_client import generate

DEFAULT_SYSTEM_PROMPT = (
    "Sen bir Telegram içerik editörüsün. Sana verilen mesajı, kullanıcının talimatına göre "
    "yeniden yaz. Sadece nihai metni döndür, açıklama ekleme."
)


async def process_text(text: str, custom_prompt: str | None) -> str:
    if not text:
        return text

    instruction = custom_prompt or "Bu mesajı öz ve akıcı hale getir, anlamını değiştirme."
    prompt = f"Talimat: {instruction}\n\nMesaj:\n{text}"
    result = await generate(prompt, system=DEFAULT_SYSTEM_PROMPT)
    return result or text

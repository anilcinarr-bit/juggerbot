"""İlk kurulumda bir kere çalıştır: telefon no + kod (+ gerekirse 2FA şifresi) ister,
   sonucunda app/config.py'deki TG_SESSION_NAME ile bir .session dosyası oluşturur.

   Kullanım: python scripts/login_session.py
"""
import asyncio

from telethon import TelegramClient

from app.config import settings


async def main() -> None:
    client = TelegramClient(settings.tg_session_name, settings.tg_api_id, settings.tg_api_hash)
    await client.start()
    me = await client.get_me()
    print(f"Giriş başarılı: {me.first_name} (@{me.username})")
    print(f"Oturum dosyası oluşturuldu: {settings.tg_session_name}.session")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

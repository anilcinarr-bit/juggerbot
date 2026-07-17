# Junction Clone

Telegram forwarding/otomasyon aracı — Junction Bot benzeri, kendi altyapında (Ollama +
Qwen3) çalışan sürüm.

## Mimari

```
app/
  config.py            -> .env okur (pydantic-settings)
  database.py          -> SQLAlchemy async engine/session
  models.py             -> SourceChannel, TargetChannel, ForwardRule, FilterRule,
                            MessageLog, PendingModeration
  schemas.py             -> API request/response modelleri
  main.py                 -> FastAPI giriş noktası

  telegram/
    userbot.py            -> Telethon client, kaynak kanalları dinler
    forwarder.py            -> filtre -> LLM -> moderasyon -> gönderim akışı

  filters/engine.py         -> keyword/media filtre motoru
  llm/ollama_client.py       -> Ollama /api/generate wrapper
  llm/processor.py            -> rewrite/özet prompt mantığı
  moderation/queue.py          -> manuel onay kuyruğu

  api/routes_*.py                -> CRUD + moderasyon onay/red endpoint'leri

scripts/login_session.py           -> ilk kurulumda Telegram hesabına giriş (.session oluşturur)
```

## Kurulum

1. **Telegram API bilgileri**: https://my.telegram.org/apps üzerinden `api_id` ve
   `api_hash` al (senin zaten hazır olduğunu söyledin).

2. `.env.example` dosyasını `.env` olarak kopyala ve doldur:
   ```bash
   cp .env.example .env
   ```

3. Bağımlılıkları kur:
   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. Ollama'da kullanacağın modelin çekili olduğundan emin ol:
   ```bash
   ollama pull qwen3        # veya .env'deki OLLAMA_MODEL neyse
   ```
   Not: Qwen3-Coder 30B kod odaklı bir model; genel metin rewrite/özet işleri için
   `qwen3` (coder olmayan) ya da benzeri bir chat modeli daha tutarlı sonuç verir.
   İkisini de Ollama'da yan yana tutabilirsin, `.env`'de `OLLAMA_MODEL` ile seçersin.

5. İlk Telegram girişini yap (telefon no + kod ister, tek seferlik):
   ```bash
   python scripts/login_session.py
   ```
   Bu işlem `TG_SESSION_NAME.session` dosyasını oluşturur — bir daha login istemez.

6. Sunucuyu başlat:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   Bu hem FastAPI dashboard API'sini (http://localhost:8000/docs) hem de arka planda
   Telethon userbot'unu (mesaj dinleyici) ayağa kaldırır.

## Kullanım akışı

1. `POST /sources/` ile bir kaynak kanal ekle (kanalın telegram_id'si gerekli — bağlı
   hesabın üye/erişimi olan herhangi bir kanal/grup olabilir, davet linki şart değil).
2. `POST /targets/` ile hedef kanal ekle (`kind: user` bağlı hesap üzerinden, `kind: bot`
   ileride bot token entegrasyonu eklersen).
3. `POST /rules/` ile kaynak→hedef eşleşmesi kur; `use_llm: true` yaparsan LLM ile
   yeniden yazım devreye girer, `require_moderation: true` yaparsan mesajlar önce
   onay kuyruğuna düşer.
4. Onay kuyruğunu `GET /moderation/pending`, onaylamak için
   `POST /moderation/{id}/approve`, reddetmek için `POST /moderation/{id}/reject`.

Kanal telegram_id'lerini bulmak için: bağlı hesapla `python -c` içinde
`client.get_dialogs()` çekip listeleyebilirsin — istersen ayrı bir `list_dialogs.py`
scripti de ekleyebilirim.

## Sonraki adımlar (henüz yok, MVP'nin dışında bırakıldı)

- Web dashboard (şu an sadece REST API + `/docs` var, React/basit HTML panel eklenebilir)
- Watermark overlay, history copying (geçmiş mesaj toplu aktarımı)
- Topic mapping (forum grupları arası konu eşleştirme)
- Folders forwarding (Telegram klasörlerinden toplu kaynak ekleme)
- Bot token ile hibrit gönderim (şu an sadece userbot üzerinden gönderiyor)
- Rate limiting / flood-wait yönetimi (Telegram limitleri için, prod'a çıkmadan şart)

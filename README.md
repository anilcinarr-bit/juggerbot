# Architecture

```
app/
├── config.py
│   └── Loads application configuration from `.env` using Pydantic Settings.
│
├── database.py
│   └── SQLAlchemy async engine and session management.
│
├── models/
│   └── Database models (SourceChannel, TargetChannel, ForwardRule,
│       FilterRule, MessageLog, PendingModeration).
│
├── schemas/
│   └── Pydantic request/response schemas.
│
├── main.py
│   └── FastAPI application entry point.
│
├── telegram/
│   ├── client.py
│   │   └── Shared Telethon client.
│   ├── listener.py
│   │   └── Listens for incoming Telegram messages.
│   ├── handlers.py
│   │   └── Telegram event handlers.
│   ├── forwarder.py
│   │   └── Message forwarding service.
│   └── userbot.py
│       └── Userbot initialization.
│
├── pipeline/
│   ├── pipeline.py
│   ├── pipeline_manager.py
│   ├── forward_engine.py
│   ├── telegram_sender.py
│   └── steps.py
│
├── filters/
│   └── Keyword and media filtering engine.
│
├── llm/
│   ├── ollama_client.py
│   └── Prompt processing and message rewriting.
│
├── moderation/
│   └── Manual approval queue.
│
└── api/
    └── REST API endpoints.

scripts/
└── login_session.py
    └── One-time Telegram authentication.
```

---

# Installation

## 1. Create a Telegram Application

Visit:

https://my.telegram.org/apps

Create an application and obtain:

- `API_ID`
- `API_HASH`

---

## 2. Configure Environment Variables

Copy the example configuration:

```bash
cp .env.example .env
```

Fill in the required values inside the `.env` file.

---

## 3. Install Dependencies

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

**Windows**

```bash
.venv\Scripts\activate
```

**Linux / macOS**

```bash
source .venv/bin/activate
```

Install project dependencies:

```bash
pip install -r requirements.txt
```

---

## 4. Download an Ollama Model

Example:

```bash
ollama pull qwen3
```

Or download the model specified by `OLLAMA_MODEL` inside your `.env` file.

> **Recommendation**
>
> The standard **Qwen3** model generally performs better for message rewriting and summarization.
> **Qwen3-Coder** is optimized for software development tasks.
> Both models can coexist locally, allowing easy switching through the `.env` configuration.

---

## 5. Authenticate Your Telegram Account

Run the login script once:

```bash
python scripts/login_session.py
```

The script will ask for your phone number and Telegram verification code.

After successful authentication, Telethon creates:

```
<TG_SESSION_NAME>.session
```

This session is reused automatically on future launches.

---

## 6. Start the Application

```bash
uvicorn app.main:app --reload --port 8000
```

This starts:

- FastAPI REST API
- Swagger UI
- Telegram Listener
- Background Processing Pipeline

Swagger documentation:

```
http://localhost:8000/docs
```

---

# Workflow

1. Register one or more **Source Channels**.

2. Register one or more **Target Channels**.

3. Create forwarding rules between sources and targets.

4. Configure optional processing:

- LLM Rewrite
- Keyword Filtering
- Media Filtering
- Manual Moderation

5. Incoming messages are processed through the pipeline and forwarded to the configured destination(s).

---

# Finding Telegram Chat IDs

Telegram Chat IDs can be retrieved using the authenticated account.

Example:

```python
client.get_dialogs()
```

A dedicated `list_dialogs.py` helper utility may be added in future releases.

---

# Roadmap

The following features are planned but are intentionally excluded from the current MVP:

- Web Dashboard (React)
- Bulk History Migration
- Watermark / Branding Engine
- Topic-to-Topic Mapping
- Folder-Based Source Import
- Hybrid Userbot + Bot API Delivery
- Telegram Flood-Wait & Rate Limit Management
- Scheduling & Delayed Delivery
- Multi-Pipeline Management
- Multi-Tenant Workspace Support
- Plugin System
- Webhooks & External Integrations

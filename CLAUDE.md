# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Backend

```bash
# Activate virtual environment (Windows)
venv\Scripts\activate

# Run backend (dev)
python app/main.py

# Run a single query (CLI)
python app/main.py --query "your query here"

# Run GAIA benchmark (all questions)
python app/main.py --gaia

# Check all Python files compile
python -m compileall . -q
```

### Frontend

```bash
cd frontend
npm install       # install deps
npm run dev       # dev server (port 5173, proxies API to port 8000)
npm run build     # production build → frontend/dist
```

### Desktop App (dev)

```bash
# GUI mode — native window with system tray
python desktop/app.py

# CLI mode — query via desktop entry point
python desktop/app.py --query "your query here"
python desktop/app.py --gaia

# Enable DevTools (Edge inspector alongside the window)
DESKGENIE_DEBUG=1 python desktop/app.py
```

### Production Build (exe)

```bash
# Builds frontend + packages everything into dist/DeskGenie/DeskGenie.exe
python desktop/build.py
```

### Production (web server only)

Build frontend first (`npm run build`), then `python app/main.py` serves both API and static files on port 8000.

## Architecture

DeskGenie is a desktop AI assistant. The user sends natural language commands via a React UI or CLI. A LangGraph agent backed by Google Gemini processes the request using 25+ tools (file ops, PDF, images, media, web search, HTTP requests, Python execution, classical ciphers), streaming logs back to the UI in real time.

```
React UI / CLI
    ↓
FastAPI (app/genie_api.py)  ←→  SSE log streaming
    ↓
MyGAIAAgents (agents/agents.py)
    ↓
LangGraphAgent (agents/langgraphagent.py)  ←  Google Gemini
    ↓
Tools (tools/desktop_tools.py, tools/custom_tools.py)
```

### Key flows

- **Async chat**: POST `/api/chat` → returns `task_id` → frontend polls `/api/task/{id}` for result, streams logs via SSE at `/api/task/{id}/logs/stream`.
- **Benchmark easter egg**: type `/gaia` in chat (all questions) or `/gaia 1,3,5` (specific 1-based indices). CLI equivalent: `--gaia` / `--gaia 1,3,5`.
- **Agent loop**: LangGraphAgent builds a LangGraph state machine. State tracks `question`, `messages`, `answer`, `step_count`, `file_name`. Max 25 steps per iteration, recursion limit 100.

### Important files

| File | Purpose |
|------|---------|
| `app/genie_api.py` | All REST endpoints, task store, SSE streaming |
| `app/config.py` | Internal engine constants (timeouts, retry, limits, ports) |
| `agents/langgraphagent.py` | Core LangGraph agent with Gemini |
| `agents/agents.py` | `MyGAIAAgents` wrapper — the single public interface |
| `tools/desktop_tools.py` | PDF, image, file, document, media tools |
| `tools/custom_tools.py` | Web search, Wikipedia, ArXiv, YouTube, HTTP requests, Python execution, classical ciphers, rate-limit wait, advisor |
| `utils/log_streamer.py` | `LogStreamer` (UI) and `ConsoleLogger` (CLI) |
| `utils/chat_storage.py` | JSON chat persistence (platform-specific dirs) |
| `resources/ui_strings.py` | All backend-facing strings (no hardcoding) |
| `frontend/src/uiStrings.js` | All frontend-facing strings (no hardcoding) |
| `resources/system_prompt.py` | Agent system prompt |
| `external/scorer.py` | GAIA benchmark scorer — **do not modify** |
| `desktop/app.py` | Desktop app entry point (GUI + CLI modes) |
| `desktop/server.py` | Port management and uvicorn server thread |
| `desktop/single_instance.py` | Sentinel socket for single-instance enforcement |
| `desktop/tray.py` | System tray icon (pystray) |
| `desktop/icon.py` | Runtime icon generation (Pillow, no external file) |
| `desktop/desktop.spec` | PyInstaller build spec |
| `desktop/build.py` | One-command production build (frontend + exe) |

## Coding Conventions (from `.clinerules`)

- **No hardcoded strings** — all user-facing strings go in `resources/ui_strings.py` (backend) or `frontend/src/uiStrings.js` / `frontend/src/consoleStrings.js` (frontend).
- All function signatures must have **type hints** (`Optional[]`, `List[]`, `Dict[]`, `Tuple[]`).
- Private methods prefixed with `_underscore`. Constants in `UPPER_SNAKE_CASE`. Classes in `PascalCase`.
- Public functions get Google-style docstrings (Args, Returns, Raises). Private functions get a one-liner.
- All agents implement the `__call__(question, file_name)` interface.
- Internal engine constants (timeouts, retry limits, ports) live in `app/config.py`. User-facing settings (LLM provider/keys, MCP servers, agent tuning, observability) live in `config.json`.

## Configuration

All user-facing settings live in `config.json` (platform config dir — Windows: `%LOCALAPPDATA%\DeskGenie\config.json`). See `config.json.example` at the repo root for the full schema. Key sections:

- `llm` — active provider, API keys, model names, temperature, timeout
- `mcpServers` — MCP server definitions (same schema as Claude Code `settings.json`)
- `agent` — maxSteps, maxRetries, search result limits
- `observability.langfuse` — Langfuse tracing keys
- `logging.level` — Python log level (DEBUG/INFO/WARNING/ERROR)
- `folder_aliases` — short names resolved in natural language commands
- `preferences` — default output dir, image quality, PDF DPI

## Multi-Model Architecture

DeskGenie deliberately routes different workloads to different models:

- **Agent reasoning / orchestration** — controlled by `llm.activeProvider` in `config.json`. Supports `google`, `anthropic`, `ollama`, `huggingface`.
- **Vision workloads** (image analysis, video understanding, YouTube Q&A) — always Google Gemini (`genai.Client` in `tools/custom_tools.py`), regardless of active provider.

The two layers are independent: switching the primary LLM has no effect on vision tool behaviour.

## LLM Configuration

Set via `config.json` → `llm`. Google provider has three model slots: `agentModel` (main loop), `visionModel` (image/video tools), `advisorModel` (hard-problem escalation). Temperature defaults to `0` (deterministic). LLM call timeout: 300s. Retry logic: 3 retries, 2s initial delay, 2× backoff (handles `504 DEADLINE_EXCEEDED`).

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

# Run GAIA benchmark (default filter)
python app/main.py --test

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

### Production

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
- **Sync chat**: POST `/api/chat/sync` (used by CLI/benchmark).
- **Agent loop**: LangGraphAgent builds a LangGraph state machine. State tracks `question`, `messages`, `answer`, `step_count`, `file_name`. Max 25 steps per iteration, recursion limit 100.

### Important files

| File | Purpose |
|------|---------|
| `app/genie_api.py` | All REST endpoints, task store, SSE streaming |
| `app/config.py` | Centralized constants (model, retry, limits) |
| `agents/langgraphagent.py` | Core LangGraph agent with Gemini |
| `agents/agents.py` | `MyGAIAAgents` wrapper — the single public interface |
| `tools/desktop_tools.py` | PDF, image, file, document, media tools |
| `tools/custom_tools.py` | Web search, Wikipedia, ArXiv, YouTube, HTTP requests, Python execution, classical ciphers, rate-limit wait |
| `utils/log_streamer.py` | `LogStreamer` (UI) and `ConsoleLogger` (CLI) |
| `utils/chat_storage.py` | JSON chat persistence (platform-specific dirs) |
| `resources/ui_strings.py` | All backend-facing strings (no hardcoding) |
| `frontend/src/uiStrings.js` | All frontend-facing strings (no hardcoding) |
| `resources/system_prompt.py` | Agent system prompt |
| `external/scorer.py` | GAIA benchmark scorer — **do not modify** |

## Coding Conventions (from `.clinerules`)

- **No hardcoded strings** — all user-facing strings go in `resources/ui_strings.py` (backend) or `frontend/src/uiStrings.js` / `frontend/src/consoleStrings.js` (frontend).
- All function signatures must have **type hints** (`Optional[]`, `List[]`, `Dict[]`, `Tuple[]`).
- Private methods prefixed with `_underscore`. Constants in `UPPER_SNAKE_CASE`. Classes in `PascalCase`.
- Public functions get Google-style docstrings (Args, Returns, Raises). Private functions get a one-liner.
- All agents implement the `__call__(question, file_name)` interface.
- Configuration constants live in `app/config.py` only.

## Environment Variables

Required:
- `GOOGLE_API_KEY` — Google Gemini API key (from aistudio.google.com)

Optional:
- `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` — observability tracing
- `DESKGENIE_OUTPUT_DIR` — output directory (default: `~/Desktop_Agent_Output`)
- `HOST` / `PORT` — server binding (default: `0.0.0.0:8000`)

See `.env.example` for the full list. User-specific folder aliases and preferences go in the platform config dir (Windows: `%LOCALAPPDATA%\DeskGenie\config.json`).

## Multi-Model Architecture

DeskGenie deliberately routes different workloads to different models:

- **Agent reasoning / orchestration** — configurable via `DEFAULT_MODEL_PROVIDER` in `app/config.py`. Supports Google Gemini, Anthropic Claude, HuggingFace, and Ollama.
- **Vision workloads** (image analysis, video understanding, YouTube Q&A) — always use Google Gemini (`genai.Client` in `tools/custom_tools.py`), regardless of the primary provider. Gemini is hardcoded here because it has native multimodal support.

This means the two layers are independent: switching the primary LLM to Claude does not affect vision tool behaviour.

## LLM Configuration

Primary model: `gemini-2.5-flash` (set in `app/config.py` as `GEMINI_MODEL_2_5`, resolved via `get_default_model_name()` in `utils/utils.py`). Temperature `0` for both agent LLM and vision/analysis tools (deterministic). LLM call timeout: 300s. Retry logic: 3 retries, 2s initial delay, 2× backoff (handles `504 DEADLINE_EXCEEDED`).

Note: `GEMINI_MODEL_3_1 = "gemini-3.1-pro-preview"` is defined in `config.py` but not currently wired into the agent.

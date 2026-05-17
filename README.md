# DeskGenie 🧞‍♂️

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)

**DeskGenie** lets you control your desktop through plain English — rename files, manipulate PDFs, convert images, extract audio, search the web, and run Python code, all from a single chat interface.

Under the hood: a LangGraph agent with multi-model support (Gemini, Claude, Ollama, HuggingFace), 25+ tools, and MCP server integration.

> Started as a hobbyist project to learn agentic AI in practice. Now a tool I actually use daily and where I prototype ideas before writing about them.

---

## Download (Windows)

The easiest way to get started on Windows — no Python or Git required:

1. Go to the [Releases page](https://github.com/hemantvirmani/DeskGenie/releases)
2. Download `DeskGenie-vX.X.X-windows.zip` from the latest release
3. Extract and run `DeskGenie.exe`
4. Add your API key to `config.json` — place it next to `DeskGenie.exe` (simple) or at `%LOCALAPPDATA%\DeskGenie\config.json` (cleaner — keeps config separate from the app). If both exist, the `%LOCALAPPDATA%` one takes priority.

> Need to build from source, run on macOS/Linux, or contribute? Follow the Quick Start below.

---

## Run from Source

### 1. Clone the repo

```bash
git clone https://github.com/hemantvirmani/DeskGenie.git
cd DeskGenie
```

### 2. Run setup

**Linux / macOS:**
```bash
chmod +x setup.sh && ./setup.sh
```

**Windows (Git Bash):**
```bash
bash setup.sh
```

> Don't have Git Bash? Install [Git for Windows](https://git-scm.com/downloads/win) — it includes Git Bash.

The script creates a virtual environment, installs all dependencies, and places a `config.json` template in the right location.

### 3. Add your API key

Open `config.json` from the platform config directory:

| Platform | Path |
|----------|------|
| Windows  | `%LOCALAPPDATA%\DeskGenie\config.json` |
| macOS    | `~/Library/Application Support/DeskGenie/config.json` |
| Linux    | `~/.local/share/DeskGenie/config.json` |

Set `llm.activeProvider` and fill in the API key for that provider:

| Provider | Where to get a key |
|----------|--------------------|
| `google` (default) | [Google AI Studio](https://aistudio.google.com) — free tier available |
| `anthropic` | [Anthropic Console](https://console.anthropic.com) |
| `ollama` | No key needed — run [Ollama](https://ollama.com) locally |
| `huggingface` | [HuggingFace Settings](https://huggingface.co/settings/tokens) |

### 4. Run

```bash
# Activate the venv first
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows

# Desktop app (recommended — native window, system tray)
python desktop/app.py

# Or: web UI only
python app/main.py
# Then open http://localhost:8000
```

---

## What can you ask it?

Just type in plain English. Some examples:

```
Combine all images in my Downloads folder into a single PDF
Extract the last 3 pages from report.pdf and save as summary.pdf
Convert all HEIC photos in iPhone_Backup to JPG
Compress movie.mp4 to under 100MB
Organize my Desktop folder by file type
Extract audio from interview.mp4 as MP3
What papers on arXiv are there about diffusion models this week?
Rename all files matching IMG_* to vacation_{n}.jpg
Find duplicate files in my Documents folder
Check my Gmail for unread messages from John this week  (requires Gmail MCP)
```

---

## What it can do

### 📄 PDF
- Extract, delete, merge, or split pages
- Convert pages to images (PNG/JPG)

### 🖼️ Images
- Convert between formats: HEIC, PNG, JPG, WebP, BMP, GIF, TIFF
- Resize, compress, batch convert
- Combine images into a PDF

### 📁 Files
- Batch rename with patterns (`{n}`, `{date}`, etc.)
- Organize a folder by file type, extension, or date
- Find duplicate files

### 📝 Documents
- Word (.docx) to PDF
- Extract text from PDF
- OCR — extract text from images or scans

### 🎬 Media
- Extract audio from video
- Compress video to a target size
- Get media file info (duration, resolution, codec)

### 🔍 Web & Research
- Web search (DuckDuckGo)
- Wikipedia, ArXiv, YouTube
- Fetch and read web pages
- HTTP requests (GET/POST/PUT/DELETE)

### 🛠️ Utilities
- Run Python code for calculations or data tasks
- Classical cipher encryption/decryption

---

## Configuration

All settings live in `config.json` (see path above). The full schema with explanations is in `config.json.example` at the repo root.

### Key settings

| Setting | What it does |
|---------|-------------|
| `llm.activeProvider` | Which LLM drives the agent |
| `llm.providers.*` | API keys and model names per provider |
| `agent.maxSteps` | Max tool calls per query (default: 25) |
| `logging.level` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |
| `folder_aliases` | Short names you can use in chat |
| `preferences` | Default output dir, image quality, PDF DPI |

### Folder aliases

Define shortcuts for long paths:

```json
"folder_aliases": {
  "work": "C:/Users/YourName/Work",
  "photos": "D:/Photos/2024"
}
```

Then use them in chat: `"Convert all images in photos to JPG"`

### Adding MCP servers

DeskGenie can load tools from any MCP-compatible server. Add entries under `mcpServers` in `config.json` — same format as Claude Code's `settings.json`:

```json
"mcpServers": {
  "home_assistant": {
    "transport": "stdio",
    "command": "uvx",
    "args": ["ha-mcp@latest"],
    "env": { "HOMEASSISTANT_URL": "...", "HOMEASSISTANT_TOKEN": "..." }
  }
}
```

---

## Running modes

### Desktop app (recommended)

Native window with a system tray icon. No browser tab, no terminal visible.

```bash
python desktop/app.py
```

- Minimize to tray with the close button
- Right-click tray icon → **Open** / **Quit**
- Single instance — double-launching focuses the existing window

---

## System dependencies

These are optional — only needed for specific features:

| Dependency | Feature | Install |
|------------|---------|---------|
| [FFmpeg](https://ffmpeg.org/) | Audio/video extraction and compression | `brew install ffmpeg` / `choco install ffmpeg` / `apt install ffmpeg` |
| [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) | OCR (extract text from images) | `brew install tesseract` / `apt install tesseract-ocr` / [Windows installer](https://github.com/UB-Mannheim/tesseract/wiki) |
| LibreOffice | Word→PDF on Linux/macOS | `brew install --cask libreoffice` / `apt install libreoffice` |

---

## For Developers

### Manual setup (without setup.sh)

```bash
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cd frontend && npm install && cd ..
```

Copy `config.json.example` to the platform config path and fill in your values.

### Build the Windows exe

```bash
python desktop/build.py
# Output: dist/DeskGenie/DeskGenie.exe
```

End users run the exe directly — no Python required.

### CI / CD

Two GitHub Actions workflows run automatically:

- **`ci.yml`** — on every push/PR to `main`: Python compile check + frontend build
- **`release.yml`** — on `v*` tags: full Windows build, smoke test, draft GitHub Release

To release:

```bash
git tag v1.2.0
git push origin v1.2.0
# Then review and publish the draft release on GitHub
```

### Multi-model architecture

| Role | Default model | Config key |
|------|--------------|------------|
| Agent (reasoning + tools) | Gemini 2.5 Flash | `llm.activeProvider` |
| Advisor (escalation for hard problems) | Gemini 2.5 Pro | `llm.providers.google.advisorModel` |
| Vision (images, video, YouTube) | Gemini 2.5 Flash | `llm.providers.google.visionModel` |

Swapping the primary LLM doesn't affect vision tool behaviour — those always use Google Gemini.

### Project structure

```
DeskGenie/
├── app/                    # FastAPI backend
├── agents/                 # LangGraph agent
├── tools/
│   ├── core/files.py       # File-ops logic (shared)
│   ├── desktop_tools.py    # Agent tool definitions
│   ├── custom_tools.py     # Web, search, Python execution
│   └── mcp_tools.py        # MCP server loader
├── mcp_servers/
│   └── file_ops_server.py  # Standalone MCP server (optional)
├── desktop/                # Native app (PyInstaller)
├── frontend/               # React + Tailwind UI
├── utils/                  # Logging, config, storage helpers
├── resources/              # Strings, system prompt
└── config.json.example     # Full config reference
```

---

## Roadmap

- [ ] Memory Support
- [ ] Comprehensive test suite
- [ ] LiteLLM for enhanced routing to different providers
- [x] MCP server support (Home Assistant integrated)
- [x] Multi-provider LLM support (Gemini, Claude, Ollama, HuggingFace)
- [x] Windows desktop app (exe)
- [x] CI/CD with automatic GitHub Releases

---

## FAQ

**Q. Can I run DeskGenie without the desktop app?**

Yes — two other modes are available:

- **Web UI**: `python app/main.py` → open `http://localhost:8000`. For dev hot-reload, run `python app/main.py` and `cd frontend && npm run dev` in separate terminals, then open `http://localhost:5173`.
- **CLI**: `python app/main.py --query "Merge all PDFs in my Downloads folder"`

**Q. Can I use the file-ops tools from Claude Desktop or another MCP client?**

Yes. The PDF, image, and file tools are built into DeskGenie automatically, but they are also exposed as a standalone MCP server:

```bash
python mcp_servers/file_ops_server.py
```

Add this to your client's MCP config (e.g. Claude Desktop's `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "deskgenie-files": {
      "command": "C:/path/to/DeskGenie/.venv/Scripts/python.exe",
      "args": ["C:/path/to/DeskGenie/mcp_servers/file_ops_server.py"]
    }
  }
}
```

> You do NOT need this in DeskGenie's own `config.json` — the tools are already loaded directly by the agent.

**Q. Something isn't working — how do I debug?**

**HEIC conversion fails**

- `pip install pillow-heif`

**Video processing fails**

- Install FFmpeg and ensure it's in your system PATH

**OCR not working**

- Install Tesseract and ensure it's in PATH (Windows: also set `TESSDATA_PREFIX`)

**Word to PDF fails on Linux/macOS**

- Install LibreOffice (see system dependencies above)

**Agent says it can't do something**

- Set `logging.level: "DEBUG"` in `config.json` and re-run to see the full tool call trace

**Q. How do I run the GAIA benchmark?**

```bash
python app/main.py --gaia          # all questions
python app/main.py --gaia 2,4,6   # specific questions (1-based)
```

Or type `/gaia` / `/gaia 2,4,6` directly in the chat UI.

---

## Contributing

Issues and PRs are welcome. For questions or suggestions, open an issue on GitHub.

## License

MIT — see [LICENSE](LICENSE).

## Disclaimer

Provided as-is for educational and hobbyist use. Always back up important files before running file manipulation tools.

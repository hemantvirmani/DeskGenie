# DeskGenie — Quick Start

## 1. Configure

Rename `config.json.example` to `config.json` (it's in this folder), then open it and set two things:

- `llm.activeProvider` — which AI provider to use
- The API key for that provider under `llm.providers.<provider>.apiKey`

| Provider | `activeProvider` value | Where to get a key |
| -------- | ---------------------- | ------------------ |
| Google Gemini (default, free tier) | `google` | https://aistudio.google.com |
| Anthropic Claude | `anthropic` | https://console.anthropic.com |
| Ollama (local, no key needed) | `ollama` | https://ollama.com |
| HuggingFace | `huggingface` | https://huggingface.co/settings/tokens |

**Tip:** You can also place `config.json` at `%LOCALAPPDATA%\DeskGenie\config.json` to keep it separate from the app. If both exist, the `%LOCALAPPDATA%` one takes priority.

## 2. Run

Double-click `DeskGenie.exe`. A native window opens with a chat interface.

- Close the window → minimizes to system tray
- Right-click tray icon → **Open** / **Quit**

## 3. Optional system dependencies

Only needed if you use specific features:

| Feature | Dependency | Install |
| ------- | ---------- | ------- |
| Audio/video extraction | FFmpeg | https://ffmpeg.org / `choco install ffmpeg` |
| OCR (text from images) | Tesseract | https://github.com/UB-Mannheim/tesseract/wiki |
| Word → PDF | LibreOffice | https://libreoffice.org |

## Help & source code

https://github.com/hemantvirmani/DeskGenie

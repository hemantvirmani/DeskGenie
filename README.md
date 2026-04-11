# DeskGenie 🧞‍♂️

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)

**Your Intelligent Desktop Assistant** - An AI-powered desktop agent that performs file operations, document manipulation, media processing, and more using natural language commands.

> **Note**: This is a hobbyist open-source project for educational purposes. It demonstrates how to build AI agents that can interact with desktop environments using natural language.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Installation

### Prerequisites

- Python 3.10+
- Node.js 18+ (for the frontend)
- [FFmpeg](https://ffmpeg.org/) (for audio/video processing)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) (optional, for OCR features)

### Automated Setup (Recommended)

A setup script handles everything: virtual environment, Python & Node dependencies, and config file.

**Linux / macOS:**
```bash
git clone https://github.com/hemantvirmani/DeskGenie.git
cd DeskGenie
chmod +x setup.sh
./setup.sh
```

**Windows (Git Bash):**
```bash
git clone https://github.com/hemantvirmani/DeskGenie.git
cd DeskGenie
bash setup.sh
```

> **Windows without Git Bash?** Install [Git for Windows](https://git-scm.com/downloads/win) — it includes Git Bash. Alternatively, use WSL.

The script will:
1. Verify Python 3.10+
2. Create and activate a virtual environment
3. Install all Python dependencies
4. Install frontend (npm) dependencies
5. Copy `config.sample.json` to the correct platform-specific location
6. Prompt for your Google API key and save it to `.env`

---

### Manual Setup

1. **Clone the repository**:
```bash
git clone https://github.com/hemantvirmani/DeskGenie.git
cd DeskGenie
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**:
```bash
# Required for AI features — set the key for your chosen provider
export GOOGLE_API_KEY="your_google_api_key"       # Google Gemini
export ANTHROPIC_API_KEY="your_anthropic_api_key" # Anthropic Claude (alternative)

# Optional: Langfuse observability
export LANGFUSE_PUBLIC_KEY="pk-lf-..."
export LANGFUSE_SECRET_KEY="sk-lf-..."
```

> **Switching providers**: Set `DEFAULT_MODEL_PROVIDER` in `app/config.py` to `ModelProviders.GOOGLE` or `ModelProviders.ANTHROPIC` (also supports `HUGGINGFACE` and `OLLAMA`).

5. **Run DeskGenie**:

**Development Mode** (with hot reload):

```bash
# Terminal 1 - Backend
python app/main.py

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
```
Open <http://localhost:5173> (Vite proxies API calls to port 8000)

**Production Mode**:

```bash
# Build frontend first
cd frontend
npm install
npm run build
cd ..

# Start server (serves both API and frontend)
python app/main.py
```
Open http://localhost:8000

### System Dependencies

#### FFmpeg (for audio/video)
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows (via Chocolatey)
choco install ffmpeg
```

#### Tesseract OCR (optional)
```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# Windows
# Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
```

---

## Features

### 📄 PDF Operations
- **Extract Pages**: "Extract the last 2 pages from report.pdf"
- **Delete Pages**: "Delete pages 5-7 from document.pdf"
- **Merge PDFs**: "Combine invoice1.pdf and invoice2.pdf"
- **Split PDFs**: "Split presentation.pdf into individual pages"
- **Convert to Images**: "Convert each page of brochure.pdf to PNG"

### 🖼️ Image Processing
- **Format Conversion**: "Convert photo.heic to jpg" (supports HEIC, PNG, JPG, WebP, BMP, GIF, TIFF)
- **Resize Images**: "Resize image.png to 800x600"
- **Compress Images**: "Compress photo.jpg to under 500KB"
- **Batch Convert**: "Convert all images in Downloads to JPG"

### 📁 File Management
- **Batch Rename**: "Rename all files matching 'IMG_*' to 'vacation_{n}.jpg'"
- **Organize Files**: "Organize my Downloads folder by file type"
- **Find Duplicates**: "Find duplicate files in my Documents"

### 📝 Document Tools
- **Word to PDF**: "Convert report.docx to PDF"
- **Extract Text**: "Extract all text from manual.pdf"
- **OCR**: "Extract text from screenshot.png using OCR"

### 🎬 Media Tools
- **Extract Audio**: "Extract audio from video.mp4 as MP3"
- **Compress Video**: "Compress movie.mp4 to under 100MB"
- **Media Info**: "Get details about video.mp4"

### 🔍 Research & Web Tools

- Web search via DuckDuckGo
- Wikipedia integration
- ArXiv academic paper search
- YouTube video analysis
- Web page content extraction
- HTTP requests (GET/POST/PUT/DELETE) for API interactions

### 🛠️ Utility Tools

- Python code execution (sandboxed, for calculations and data processing)
- Classical cipher encryption/decryption (Playfair, Bifid)
- Home directory file read/write (for credential and config persistence)
- Rate-limit aware waiting (`wait_seconds` for 429 handling)


## Usage

DeskGenie can be used in two ways:

### Web UI

**Development** (hot reload, frontend at port 5173):

```bash
# Terminal 1
python app/main.py

# Terminal 2
cd frontend && npm run dev
```

Open <http://localhost:5173>

**Production** (single server, frontend built into the backend):

```bash
cd frontend && npm run build && cd ..
python app/main.py        # serves everything at http://localhost:8000
```

Type any natural language command in the chat window. Examples:

```text
"Delete the last 2 pages from my thesis.pdf and save as thesis_trimmed.pdf"
"Convert all HEIC photos in my iPhone_Photos folder to JPG"
"Extract the audio from my_video.mp4 and save it as podcast.mp3"
"Organize my Downloads folder by file type"
"What's the duration and resolution of video.mp4?"
```

### Command Line (`--query`)

Run a single query directly without starting the UI:

```bash
python app/main.py --query "Convert all HEIC photos in my Downloads to JPG"
python app/main.py --query "What is the capital of France?"
python app/main.py --query "Fetch https://example.com/api and summarize the response"
```

## Usage Examples

### Using Individual Tools

```python
from desktop_tools import (
    pdf_extract_pages,
    image_convert,
    video_to_audio,
    organize_files_by_type
)

# Extract last 3 pages from PDF
pdf_extract_pages.invoke({
    "input_pdf": "document.pdf",
    "output_pdf": "last_pages.pdf",
    "page_range": "last3"
})

# Convert HEIC to JPG
image_convert.invoke({
    "input_image": "photo.heic",
    "output_image": "photo.jpg",
    "quality": 85
})

# Extract audio from video
video_to_audio.invoke({
    "input_video": "movie.mp4",
    "output_audio": "soundtrack.mp3"
})

# Organize files by type
organize_files_by_type.invoke({
    "source_dir": "/Users/me/Downloads",
    "organize_by": "type"
})
```

## Available Tools

### PDF Tools
| Tool | Description |
|------|-------------|
| `pdf_extract_pages` | Extract specific pages from PDF (supports "last2", "first5", "1-10", "1,3,5") |
| `pdf_delete_pages` | Delete pages from PDF |
| `pdf_merge` | Combine multiple PDFs into one |
| `pdf_split` | Split PDF into multiple files |
| `pdf_to_images` | Convert PDF pages to images (PNG/JPG) |

### Image Tools
| Tool | Description |
|------|-------------|
| `image_convert` | Convert between formats (HEIC, PNG, JPG, WebP, etc.) |
| `image_resize` | Resize images with aspect ratio control |
| `image_compress` | Compress to target file size |
| `batch_convert_images` | Convert all images in a directory |

### File Management Tools
| Tool | Description |
|------|-------------|
| `batch_rename_files` | Rename files using patterns ({n} for numbers, {date} for date) |
| `organize_files_by_type` | Organize into folders by extension, type, or date |
| `find_duplicate_files` | Find duplicate files by size or content |

### Document Tools
| Tool | Description |
|------|-------------|
| `word_to_pdf` | Convert Word documents to PDF |
| `extract_text_from_pdf` | Extract all text from PDF |
| `ocr_image` | Extract text from images using OCR |

### Media Tools
| Tool | Description |
|------|-------------|
| `video_to_audio` | Extract audio track from video |
| `compress_video` | Compress video to target size |
| `get_media_info` | Get detailed media file information |

## Multi-Model Architecture

DeskGenie uses different models for different tasks:

| Role | Model | Configurable? |
|------|-------|---------------|
| Agent reasoning & orchestration | Gemini 2.5 Flash, Claude Sonnet, HuggingFace, or Ollama | ✅ via `DEFAULT_MODEL_PROVIDER` in `config.py` |
| Image analysis, video understanding, YouTube Q&A | Google Gemini 2.5 Flash | ❌ fixed — best-in-class multimodal model |

This means you can run the main agent on Claude (or any other provider) while all vision-intensive work is still handled by Gemini, which has native multimodal capabilities. The two layers operate independently — swapping the primary LLM has no effect on vision tool quality.

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_API_KEY` | - | Google API key (required when using Gemini) |
| `ANTHROPIC_API_KEY` | - | Anthropic API key (required when using Claude) |
| `DESKGENIE_OUTPUT_DIR` | `~/Desktop_Agent_Output` | Default output directory |

Set the active provider in `app/config.py` via `DEFAULT_MODEL_PROVIDER`. Supported providers: `GOOGLE` (Gemini 2.5 Flash), `ANTHROPIC` (Claude Sonnet), `HUGGINGFACE`, `OLLAMA`.

### User Configuration (config.json)

DeskGenie supports user-defined folder aliases and preferences via a JSON config file.

**Config Location:**
| Platform | Path |
|----------|------|
| Windows | `%LOCALAPPDATA%\DeskGenie\config.json` |
| macOS | `~/Library/Application Support/DeskGenie/config.json` |
| Linux | `~/.local/share/DeskGenie/config.json` |

**Setup:**
1. Copy `config.sample.json` to the config location above
2. Edit the file to add your folder aliases and preferences

**Example config.json:**
```json
{
  "folder_aliases": {
    "prax": "C:/Users/YourName/Projects/Prax",
    "finance": "C:/Users/YourName/Documents/Finance",
    "work": "C:/Users/YourName/Work",
    "photos": "D:/Photos/2024"
  },
  "preferences": {
    "default_output_dir": "downloads",
    "image_quality": 85,
    "pdf_dpi": 200
  }
}
```

**Using Folder Aliases:**

Once configured, you can use aliases in natural language commands:
```
"List files in prax"
"Convert all images in finance to PDF"
"Move report.pdf to work"
```

The agent will automatically resolve aliases like `prax` to their full paths.

**Available Preferences:**
| Key | Default | Description |
|-----|---------|-------------|
| `default_output_dir` | `downloads` | Default directory for output files |
| `image_quality` | `85` | Default JPEG/WebP quality (1-100) |
| `pdf_dpi` | `200` | Default DPI for PDF operations |

## Project Structure

```
DeskGenie/
├── app/
│   ├── main.py             # Main application entry point (renamed from app.py)
│   ├── config.py           # Configuration settings
│   └── genie_api.py        # FastAPI backend (REST API)
│
├── agents/
│   ├── agents.py           # Agent wrapper/factory
│   ├── langgraphagent.py   # Custom LangGraph agent
│
├── tools/
│   ├── custom_tools.py     # Web search, analysis tools
│   └── desktop_tools.py    # PDF, image, file, document, media tools
│
├── utils/
│   ├── utils.py            # Helper functions
│   ├── langfuse_tracking.py # Observability
│   ├── log_streamer.py     # Logging functionality
│   ├── result_formatter.py # Result formatting utilities
│   ├── validators.py       # Input validation utilities
│   ├── data_dir.py         # Cross-platform directory paths
│   ├── user_config.py      # User preferences and folder aliases
│   └── chat_storage.py     # Chat persistence
│
├── runners/
│   ├── agent_runner.py     # Execution orchestrator
│   └── question_runner.py  # Benchmark runner
│
├── resources/
│   ├── state_strings.py    # State-related strings
│   ├── error_strings.py    # Error messages
│   ├── ui_strings.py       # UI-related strings
│   └── system_prompt.py    # Agent instructions
│
├── external/
│   └── scorer.py           # Third-party GAIA scorer
│
├── frontend/               # React + Tailwind CSS frontend
│   ├── src/
│   │   ├── App.jsx         # Main React app
│   │   ├── components/     # UI components (ChatWindow, Sidebar, etc.)
│   │   └── index.css       # Tailwind CSS
│   ├── package.json        # Node.js dependencies
│   └── vite.config.js      # Vite bundler config
│
├── files/                  # Data files
│   ├── metadata.jsonl      # Metadata
│   └── questions.json      # Benchmark questions
│
├── setup.sh                # Automated setup script (Linux/macOS/Git Bash)
├── requirements.txt        # Python dependencies
├── config.sample.json      # Sample user configuration
└── README.md               # This file
```

## GAIA Benchmark Mode

DeskGenie retains full GAIA benchmark capabilities. To run benchmark evaluations:

```bash
# Run all benchmark questions
python app/main.py --test all

# Run default filter (quick test)
python app/main.py --test

# Run specific question indices
python app/main.py --test 2,4,6

# Run a single query (same as UI chat)
python app/main.py --query "What is the capital of France?"

```

See the original [GAIA Agent documentation](https://github.com/hemantvirmani/GAIA_Benchmark_Agent) for benchmark details.

## Troubleshooting

### Common Issues

**"HEIC conversion fails"**
- Ensure pillow-heif is installed: `pip install pillow-heif`

**"Video processing fails"**
- Install FFmpeg (see installation section)
- Ensure FFmpeg is in your system PATH

**"OCR not working"**
- Install Tesseract OCR (see installation section)
- On Windows, add Tesseract to PATH or set `TESSDATA_PREFIX`

**"Word to PDF fails on Linux/Mac"**
- docx2pdf requires LibreOffice on non-Windows systems
- Install: `sudo apt-get install libreoffice` or `brew install --cask libreoffice`

### Performance Tips

- For large PDF operations, process in batches
- Use batch operations for multiple files

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## Acknowledgments

This project builds upon several excellent open-source libraries and frameworks:

- **LangGraph** by LangChain - Agent framework
- **Google Gemini** - LLM provider (Gemini 2.5 Flash)
- **Anthropic Claude** - LLM provider (Claude Sonnet)
- **FastAPI** - Modern web framework for APIs
- **React** - UI library
- **Tailwind CSS** - Utility-first CSS framework
- **LangChain** - Framework for LLM applications
- **FFmpeg** - Multimedia processing framework
- **Tesseract OCR** - Optical character recognition engine
- **Pillow** - Python imaging library
- **Uvicorn** - ASGI server

Special thanks to the open-source community for making these tools available.

## Disclaimer

This project is provided as-is for educational and hobbyist purposes. The authors are not responsible for any damages or data loss that may occur while using this software. Always backup your important files before using file manipulation tools.

## Roadmap

- [ ] Improve Web search tools
- [x] Add MCP Server Support — Home Assistant MCP integrated and tested
- [x] Make LLM provider support configurable (Google Gemini, Anthropic Claude, HuggingFace, Ollama)
- [ ] Create simple plugin system for custom tools. does not need to be drag n drop
- [ ] Add comprehensive test suite
- [ ] Improve documentation and tutorials
- [ ] Make it easy to access it, other than chat interface. Ideas TBD.

## Contact

For questions, issues, or suggestions, please open an issue on GitHub.

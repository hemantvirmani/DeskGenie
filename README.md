---
title: DeskGenie - Desktop AI Agent
emoji: 🧞‍♂️
app_file: app.py
---

# DeskGenie 🧞‍♂️

**Your Intelligent Desktop Assistant** - An AI-powered desktop agent that performs file operations, document manipulation, media processing, and more using natural language commands.

Originally built on top of my own learning code [GAIA Benchmark Agent](https://github.com/hemantvirmani/GAIA_Benchmark_Agent), DeskGenie extends the intelligent agent capabilities to everyday desktop tasks.

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

### 💬 Ollama Chat Integration
- **Chat**: Natural conversation with local LLMs
- **Summarize**: "Summarize this article"
- **Translate**: "Translate this to Spanish"
- **Code Explanation**: "Explain this Python code"
- **Rewrite**: "Rewrite this email professionally"

### 🔍 Research & Web Tools (from GAIA Agent)
- Web search via DuckDuckGo
- Wikipedia integration
- ArXiv academic paper search
- YouTube video analysis
- Web page content extraction

## Installation

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) (for local LLM chat features)
- [FFmpeg](https://ffmpeg.org/) (for audio/video processing)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) (optional, for OCR features)

### Quick Start

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
# Required for AI features
export GOOGLE_API_KEY="your_google_api_key"

# Optional: Ollama configuration (defaults shown)
export OLLAMA_BASE_URL="http://localhost:11434"
export OLLAMA_MODEL="llama3.2"

# Optional: Langfuse observability
export LANGFUSE_PUBLIC_KEY="pk-lf-..."
export LANGFUSE_SECRET_KEY="sk-lf-..."
```

5. **Start Ollama** (for chat features):
```bash
ollama serve
ollama pull llama3.2  # or your preferred model
```

6. **Run DeskGenie**:

**Development Mode** (with hot reload):

```bash
# Terminal 1 - Backend
python app.py

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
```
Open http://localhost:5173 (Vite proxies API calls to port 8000)

**Production Mode**:

```bash
# Build frontend first
cd frontend
npm install
npm run build
cd ..

# Start server (serves both API and frontend)
python app.py
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

## Usage Examples

### Using Natural Language

DeskGenie understands natural language commands. Here are some examples:

```
"Delete the last 2 pages from my thesis.pdf and save as thesis_trimmed.pdf"

"Convert all HEIC photos in my iPhone_Photos folder to JPG"

"Extract the audio from my_video.mp4 and save it as podcast.mp3"

"Organize my Downloads folder by file type"

"Summarize this research paper using Ollama"

"What's the duration and resolution of video.mp4?"
```

### Programmatic Usage

```python
from agents import MyGAIAAgents
from desktop_tools import get_desktop_tools_list
from ollama_chat import get_ollama_tools_list

# Initialize agent with desktop tools
agent = MyGAIAAgents()

# PDF operations
result = agent("Extract pages 1-5 from report.pdf and save as summary.pdf")

# Image conversion
result = agent("Convert photo.heic to photo.jpg with 90% quality")

# Ollama chat
result = agent("Using Ollama, explain what this Python code does: [code]")
```

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

### Ollama Chat Examples

```python
from ollama_chat import (
    ollama_chat,
    ollama_summarize,
    ollama_translate,
    ollama_code_explain
)

# Chat with local LLM
response = ollama_chat.invoke({
    "message": "What's the best way to learn Python?",
    "model": "llama3.2"
})

# Summarize text
summary = ollama_summarize.invoke({
    "text": long_article,
    "style": "bullet"  # or "detailed", "brief"
})

# Translate
translated = ollama_translate.invoke({
    "text": "Hello, how are you?",
    "target_language": "Japanese"
})

# Explain code
explanation = ollama_code_explain.invoke({
    "code": "def fibonacci(n): return n if n < 2 else fibonacci(n-1) + fibonacci(n-2)",
    "language": "python"
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

### Ollama Tools
| Tool | Description |
|------|-------------|
| `ollama_chat` | Chat with local LLM |
| `ollama_list_models` | List installed Ollama models |
| `ollama_model_info` | Get model details |
| `ollama_summarize` | Summarize text (concise/detailed/brief) |
| `ollama_translate` | Translate to any language |
| `ollama_code_explain` | Explain code snippets |
| `ollama_rewrite` | Rewrite in different styles |

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_API_KEY` | - | Google API key for Gemini model |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3.2` | Default Ollama model |
| `DESKGENIE_MODE` | `desktop` | App mode: 'desktop' or 'benchmark' |
| `DESKGENIE_OUTPUT_DIR` | `~/DeskGenie_Output` | Default output directory |
| `ENABLE_OLLAMA` | `true` | Enable Ollama features |
| `ENABLE_DESKTOP_TOOLS` | `true` | Enable desktop tools |
| `ENABLE_OCR` | `true` | Enable OCR features |

### Recommended Ollama Models

| Model | Best For | Size |
|-------|----------|------|
| `llama3.2` | General chat, instructions | 2GB |
| `llama3.2:1b` | Fast responses, simple tasks | 1.3GB |
| `mistral` | Balanced performance | 4GB |
| `codellama` | Code explanation & generation | 4GB |
| `llama3.2-vision` | Image understanding | 5GB |

## Project Structure

```
DeskGenie/
├── app.py                  # Main application entry point
├── genie_api.py            # FastAPI backend (REST API)
├── config.py               # Configuration settings
├── agents.py               # Agent wrapper/factory
├── agent_runner.py         # Execution orchestrator
│
├── frontend/               # React + Tailwind CSS frontend
│   ├── src/
│   │   ├── App.jsx         # Main React app
│   │   ├── components/     # UI components (ChatWindow, Sidebar, etc.)
│   │   └── index.css       # Tailwind CSS
│   ├── package.json        # Node.js dependencies
│   └── vite.config.js      # Vite bundler config
│
├── DESKTOP TOOLS:
├── desktop_tools.py        # PDF, image, file, document, media tools
├── ollama_chat.py          # Ollama LLM chat integration
│
├── ORIGINAL GAIA TOOLS:
├── custom_tools.py         # Web search, analysis tools
├── system_prompt.py        # Agent instructions
│
├── AGENT IMPLEMENTATIONS:
├── langgraphagent.py       # Custom LangGraph agent
├── reactlanggraphagent.py  # LangGraph ReAct agent
│
├── UTILITIES:
├── utils.py                # Helper functions
├── langfuse_tracking.py    # Observability
│
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## GAIA Benchmark Mode

DeskGenie retains full GAIA benchmark capabilities. To run benchmark evaluations:

```bash
# Run all benchmark questions
python app.py --test all

# Run default filter (quick test)
python app.py --test

# Run specific question indices
python app.py --test 2,4,6

# Run a single query (same as UI chat)
python app.py --testq "What is the capital of France?"

# Use a specific agent
python app.py --test all --agent reactlangg
```

See the original [GAIA Agent documentation](https://github.com/hemantvirmani/GAIA_Benchmark_Agent) for benchmark details.

## Troubleshooting

### Common Issues

**"Ollama is not running"**
- Start Ollama: `ollama serve`
- Or ensure the Ollama app is running

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

- Use `llama3.2:1b` for faster Ollama responses
- For large PDF operations, process in batches
- Enable GPU acceleration in Ollama for better performance

## Contributing

Contributions are welcome! Areas for improvement:

- Add more file format support
- Improve natural language understanding
- Add cloud storage integration (Google Drive, Dropbox)
- Create a native desktop UI
- Add scheduled/automated tasks
- Improve error handling and recovery

## License

This project is open-source and available under the MIT License.

## Acknowledgments

- Built on [GAIA Benchmark Agent](https://github.com/hemantvirmani/GAIA_Benchmark_Agent)
- Uses Google's Gemini model via LangGraph
- Local LLM support via [Ollama](https://ollama.ai/)
- LangGraph framework by LangChain
- React + Tailwind CSS for web interface
- FastAPI + Uvicorn for backend API
- Claude Code for help with the code

## Contact

For questions, issues, or suggestions, please open an issue on GitHub.

# DeskGenie 🧞‍♂️

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)

**Your Intelligent Desktop Assistant** - An AI-powered desktop agent that performs file operations, document manipulation, media processing, and more using natural language commands.

> **Note**: This is a hobbyist open-source project for educational purposes. It demonstrates how to build AI agents that can interact with desktop environments using natural language.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

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

### 🔍 Research & Web Tools (from GAIA Agent)
- Web search via DuckDuckGo
- Wikipedia integration
- ArXiv academic paper search
- YouTube video analysis
- Web page content extraction

## Installation

### Prerequisites

- Python 3.10+
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

# Optional: Langfuse observability
export LANGFUSE_PUBLIC_KEY="pk-lf-..."
export LANGFUSE_SECRET_KEY="sk-lf-..."
```

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
Open http://localhost:5173 (Vite proxies API calls to port 8000)

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

## Usage Examples

### Using Natural Language

DeskGenie understands natural language commands. Here are some examples:

```
"Delete the last 2 pages from my thesis.pdf and save as thesis_trimmed.pdf"

"Convert all HEIC photos in my iPhone_Photos folder to JPG"

"Extract the audio from my_video.mp4 and save it as podcast.mp3"

"Organize my Downloads folder by file type"

"What's the duration and resolution of video.mp4?"
```

### Programmatic Usage

```python
from agents import MyGAIAAgents
from desktop_tools import get_desktop_tools_list

# Initialize agent with desktop tools
agent = MyGAIAAgents()

# PDF operations
result = agent("Extract pages 1-5 from report.pdf and save as summary.pdf")

# Image conversion
result = agent("Convert photo.heic to photo.jpg with 90% quality")
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

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_API_KEY` | - | Google API key for Gemini model |
| `DESKGENIE_OUTPUT_DIR` | `~/DeskGenie_Output` | Default output directory |

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
│   └── reactlanggraphagent.py # LangGraph ReAct agent
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
│   └── validators.py       # Input validation utilities
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
├── requirements.txt        # Python dependencies
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
python app/main.py --testq "What is the capital of France?"

# Use a specific agent
python app/main.py --test all --agent reactlangg
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
- **Google Gemini** - LLM provider for natural language processing
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

- [ ] Add more file format conversions
- [ ] Improve batch processing performance
- [ ] Add more web search and research tools
- [ ] Implement user preferences and settings
- [ ] Add support for more LLM providers
- [ ] Create plugin system for custom tools
- [ ] Add comprehensive test suite
- [ ] Improve documentation and tutorials

## Contact

For questions, issues, or suggestions, please open an issue on GitHub.

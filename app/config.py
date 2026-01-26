"""Configuration settings for DeskGenie - Desktop AI Agent."""

import os
from resources.state_strings import ModelProviders

# =============================================================================
# DeskGenie Desktop Agent Configuration
# =============================================================================

# Desktop Agent Settings
DESKTOP_FILES_DIR = os.getenv("DESKGENIE_FILES_DIR", os.path.expanduser("~/Desktop"))
DESKTOP_DOWNLOADS_DIR = os.getenv("DESKGENIE_DOWNLOADS_DIR", os.path.expanduser("~/Downloads"))
DESKTOP_OUTPUT_DIR = os.getenv("DESKGENIE_OUTPUT_DIR", os.path.expanduser("~/DeskGenie_Output"))

# Tool Categories (for UI organization)
TOOL_CATEGORIES = {
    "pdf": ["pdf_extract_pages", "pdf_delete_pages", "pdf_merge", "pdf_split", "pdf_to_images"],
    "image": ["image_convert", "image_resize", "image_compress", "batch_convert_images"],
    "file": ["batch_rename_files", "organize_files_by_type", "find_duplicate_files"],
    "document": ["word_to_pdf", "extract_text_from_pdf", "ocr_image"],
    "media": ["video_to_audio", "compress_video", "get_media_info"],
}

# =============================================================================
# Configuration (Original)
# =============================================================================

AGENT_TIMEOUT_SECONDS = 180  # 3 minutes max per question

# File Paths
QUESTIONS_FILE = "files/questions2.json"
METADATA_FILE = "files/metadata.jsonl"
FILES_DIR = "files"

# API Timeouts (in seconds)
FETCH_TIMEOUT = 15
SUBMIT_TIMEOUT = 60
WEBPAGE_TIMEOUT = 30

# Test Configuration
DEFAULT_TEST_FILTER = (4, 7, 15)  # Q2, Q5, Q8, Q16

# Display Configuration
QUESTION_PREVIEW_LENGTH = 200  # Characters to show in question preview
ERROR_MESSAGE_LENGTH = 100  # Characters to show in error messages
SEPARATOR_WIDTH = 60  # Width of separator lines

# Environment Variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACEHUB_API_TOKEN")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")

# Agent Type Constants
AGENT_LANGGRAPH = "LangGraph"
AGENT_REACT_LANGGRAPH = "ReActLangGraph"

ACTIVE_AGENT = AGENT_LANGGRAPH  # Active agent to use by default

# Model Configuration
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_TEMPERATURE = 0
GEMINI_MAX_TOKENS = 1024

OLLAMA_QWEN_MODEL = "qwen2.5:7b-instruct"
HUGGINGFACE_LLAMA_MODEL = "meta-llama/Llama-3.1-8B-Instruct"

ACTIVE_AGENT_LLM_MODEL = GEMINI_MODEL
DEFAULT_MODEL_PROVIDER = ModelProviders.GOOGLE

# Retry Configuration for 504 DEADLINE_EXCEEDED errors
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 2.0  # seconds
RETRY_BACKOFF_FACTOR = 2.0

# =============================================================================
# Feature Flags
# =============================================================================

ENABLE_OCR = "true"  # Requires Tesseract

# =============================================================================
# Langfuse Observability
# =============================================================================

# Project name for Langfuse tagging (helps distinguish from other projects)
LANGFUSE_PROJECT_NAME = "DeskGenie"


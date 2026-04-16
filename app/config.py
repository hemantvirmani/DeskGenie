"""Configuration settings for Desktop AI Agent.

LLM settings, MCP servers, and log level have moved to config.json.
Edit %LOCALAPPDATA%\\DeskGenie\\config.json (or the config.json next to the
exe) to change those values.  See config.json.example for the full schema.

This file now holds only internal engine constants that end-users do not
need to touch: timeouts, retry logic, search limits, benchmark settings, etc.
"""

import os

# =============================================================================
# Desktop Agent Configuration
# =============================================================================

# Desktop Agent Settings
DESKTOP_FILES_DIR = os.getenv("DESKGENIE_FILES_DIR", os.path.expanduser("~/Desktop"))
DESKTOP_DOWNLOADS_DIR = os.getenv("DESKGENIE_DOWNLOADS_DIR", os.path.expanduser("~/Downloads"))
DESKTOP_OUTPUT_DIR = os.getenv("DESKGENIE_OUTPUT_DIR", os.path.expanduser("~/Desktop_Agent_Output"))
DESKTOP_APP_PORT = 41955       # Preferred port for the desktop app (uncommon to avoid conflicts)

# Tool Categories (for UI organization)
TOOL_CATEGORIES = {
    "pdf": ["pdf_extract_pages", "pdf_delete_pages", "pdf_merge", "pdf_split", "pdf_to_images"],
    "image": ["image_convert", "image_resize", "image_compress", "batch_convert_images"],
    "file": ["batch_rename_files", "organize_files_by_type", "find_duplicate_files"],
    "document": ["word_to_pdf", "extract_text_from_pdf", "ocr_image"],
    "media": ["video_to_audio", "compress_video", "get_media_info"],
}

# =============================================================================
# Internal Engine Constants
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

# Display Configuration
QUESTION_PREVIEW_LENGTH = 200  # Characters to show in question preview
ERROR_MESSAGE_LENGTH = 100  # Characters to show in error messages
SEPARATOR_WIDTH = 60  # Width of separator lines

# Search Tool Limits
WEBSEARCH_MAX_RESULTS = 8   # DuckDuckGo results per query (was 5)
WIKI_MAX_DOCS = 5            # Wikipedia docs per query (was 3)
ARXIV_MAX_DOCS = 5           # ArXiv docs per query (unchanged)
ARXIV_TIMEOUT_SECONDS = 30  # Max wait for ArXiv loader before giving up

# Retry Configuration for 504 DEADLINE_EXCEEDED errors
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 2.0  # seconds
RETRY_BACKOFF_FACTOR = 2.0

# Retry configuration for silent empty LLM responses (longer delays needed)
EMPTY_RESPONSE_RETRY_DELAY = 15.0  # seconds (initial delay before first retry)
EMPTY_RESPONSE_RETRY_BACKOFF = 2.0  # multiplier for subsequent retries

# Agent Step / Recursion Limits
AGENT_MAX_STEPS = 25
AGENT_RECURSION_LIMIT = 100
INTER_QUESTION_PAUSE_SECONDS = 5  # Pause between questions in batch mode (0 to disable)

# Scorer Configuration
SCORER = "llm"  # Options: "llm" (Ollama LLM judge) | "generous" (rule-based matching)

# =============================================================================
# Langfuse Observability
# =============================================================================

# Project name for Langfuse tagging (helps distinguish from other projects)
LANGFUSE_PROJECT_NAME = "Desktop-Agent"
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY", "")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", "")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://us.cloud.langfuse.com")


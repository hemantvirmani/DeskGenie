"""Configuration settings for Desktop AI Agent."""

import os
from resources.state_strings import ModelProviders

# =============================================================================
# Desktop Agent Configuration
# =============================================================================

# Desktop Agent Settings
DESKTOP_FILES_DIR = os.getenv("DESKGENIE_FILES_DIR", os.path.expanduser("~/Desktop"))
DESKTOP_DOWNLOADS_DIR = os.getenv("DESKGENIE_DOWNLOADS_DIR", os.path.expanduser("~/Downloads"))
DESKTOP_OUTPUT_DIR = os.getenv("DESKGENIE_OUTPUT_DIR", os.path.expanduser("~/Desktop_Agent_Output"))

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

# Search Tool Limits
WEBSEARCH_MAX_RESULTS = 8   # DuckDuckGo results per query (was 5)
WIKI_MAX_DOCS = 5            # Wikipedia docs per query (was 3)
ARXIV_MAX_DOCS = 3           # ArXiv docs per query (unchanged)
ARXIV_TIMEOUT_SECONDS = 30  # Max wait for ArXiv loader before giving up

# Environment Variables
GOOGLE_API_KEY = os.getenv("GOOGLE_DESKGENIE_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_DESKGENIE_KEY", "")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACEHUB_DESKGENIE_TOKEN", "")
OLLAMA_BASE_URL = os.getenv("OLLAMA_HOST", os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"))

# Model Configuration
GEMINI_MODEL_2_5 = "gemini-2.5-flash"
GEMINI_TEMPERATURE = 0       # Temperature for vision/analysis tools (keep deterministic)
AGENT_LLM_TEMPERATURE = 0.1  # Slight randomness for agent LLM — improves tool/URL selection diversity
GEMINI_MAX_TOKENS = 1024

GEMINI_MODEL_3_1 = "gemini-3.1-pro-preview"

OLLAMA_QWEN_MODEL = "qwen3.5:2b"
HUGGINGFACE_LLAMA_MODEL = "meta-llama/Llama-3.1-8B-Instruct"
ANTHROPIC_MODEL = "claude-sonnet-4-5-20250929"

DEFAULT_MODEL_PROVIDER = ModelProviders.GOOGLE

# LLM client timeout — increase for long-context calls (e.g. 16-question exam)
LLM_CALL_TIMEOUT = 300  # seconds

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
# MCP Server Configuration
# =============================================================================
# Each entry: server_name → transport config
# transport: "stdio" (local process) or "sse" (HTTP/SSE remote)
# To disable all MCP servers, set MCP_SERVERS = {}
MCP_SERVERS: dict = {
    # Required env vars: HOMEASSISTANT_URL, HOMEASSISTANT_TOKEN
    "home_assistant": {
        "transport": "stdio",
        "command": "uvx",
        "args": ["ha-mcp@latest"],
        # Optional whitelist: only expose these tools to the LLM.
        # Remove the "tools" key entirely to expose all tools from this server.
        # Keeping a focused subset prevents overwhelming Gemini with 90+ HA tools.
        "tools": [
            "ha_get_state",
            "ha_get_states",
            "ha_call_service",
            "ha_search_entities",
            "ha_get_overview",
            "ha_config_list_areas",
            "ha_get_history",
            "ha_bulk_control",
            "ha_get_entity",
            "ha_list_services",
            "ha_get_logbook",
            "ha_restart",
        ],
    }
}

# =============================================================================
# Langfuse Observability
# =============================================================================

# Project name for Langfuse tagging (helps distinguish from other projects)
LANGFUSE_PROJECT_NAME = "Desktop-Agent"
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY", "")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", "")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://us.cloud.langfuse.com")


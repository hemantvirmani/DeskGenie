"""Configuration settings for Desktop AI Agent.

LLM settings, MCP servers, and log level have moved to config.json.
Edit %LOCALAPPDATA%\\DeskGenie\\config.json (or the config.json next to the
exe) to change those values.  See config.json.example for the full schema.

This file now holds only internal engine constants that end-users do not
need to touch: timeouts, retry logic, search limits, benchmark settings, etc.
"""

# =============================================================================
# Desktop Agent Configuration
# =============================================================================

DESKTOP_APP_PORT = 41955       # Preferred port for the desktop app (uncommon to avoid conflicts)

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

ARXIV_TIMEOUT_SECONDS = 30  # Max wait for ArXiv loader before giving up

# Retry Configuration for 504 DEADLINE_EXCEEDED errors
INITIAL_RETRY_DELAY = 2.0  # seconds
RETRY_BACKOFF_FACTOR = 2.0

# Retry configuration for silent empty LLM responses (longer delays needed)
EMPTY_RESPONSE_RETRY_DELAY = 15.0  # seconds (initial delay before first retry)
EMPTY_RESPONSE_RETRY_BACKOFF = 2.0  # multiplier for subsequent retries

# Agent Step / Recursion Limits
AGENT_RECURSION_LIMIT = 100
INTER_QUESTION_PAUSE_SECONDS = 5  # Pause between questions in batch mode (0 to disable)

# Scorer Configuration
SCORER = "llm"  # Options: "llm" (Ollama LLM judge) | "generous" (rule-based matching)

# Langfuse observability keys have moved to config.json → observability.langfuse.*


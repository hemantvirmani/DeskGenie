"""Configuration settings for GAIA Benchmark Agent."""

import os

# API Configuration
DEFAULT_API_URL = "https://agents-course-unit4-scoring.hf.space"
AGENT_TIMEOUT_SECONDS = 180  # 3 minutes max per question

# File Paths
QUESTIONS_FILE = "files/questions.json"
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
SPACE_HOST = os.getenv("SPACE_HOST")
SPACE_ID = os.getenv("SPACE_ID")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Agent Type Constants
AGENT_LANGGRAPH = "LangGraph"
AGENT_REACT_LANGGRAPH = "ReActLangGraph"
AGENT_LLAMAINDEX = "LLamaIndex"
AGENT_SMOL = "SMOL"

ACTIVE_AGENT = AGENT_REACT_LANGGRAPH  # Active agent to use by default

# Model Configuration
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_TEMPERATURE = 0
GEMINI_MAX_TOKENS = 1024

ACTIVE_AGENT_LLM_MODEL = GEMINI_MODEL

# Retry Configuration for 504 DEADLINE_EXCEEDED errors
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 2.0  # seconds
RETRY_BACKOFF_FACTOR = 2.0

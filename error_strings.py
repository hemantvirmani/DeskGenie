"""Centralized error strings for DeskGenie.

This module contains all error messages returned by agents and tools.
Separating errors from success messages allows for:
- Easier error tracking and monitoring
- Consistent error message formatting
- Potential future localization of error messages
"""


class AgentErrors:
    """Error strings for agent operations."""

    NO_ANSWER = "Error: No answer generated"
    MAX_ITERATIONS = "Error: Maximum iteration limit reached"
    AGENT_FAILED = "Error: Agent failed - {error}"
    AGENT_FAILED_RETRIES = "Error: Agent failed after {max_retries} retries - {error}"
    GENERIC = "Error: {error}"


class ToolErrors:
    """Error strings for tool operations."""

    # Calculator
    DIVIDE_BY_ZERO = "Cannot divide by zero"

    # Time
    TIME_FETCH = "Error fetching time for timezone '{timezone}': {error}"

    # Web Search
    SEARCH_NO_RESULTS = "No results found. Try search with a different query."
    SEARCH_FAILED = "Search error (try again): {error}"

    # Wikipedia
    WIKI_SEARCH = "Error performing wikipedia search: {error}. try again."

    # ArXiv
    ARXIV_SEARCH = "Error performing arxiv search: {error}. try again."

    # Webpage
    WEBPAGE_FETCH = "get_webpage_content failed: {error}"

    # Excel
    EXCEL_READ = "Error: Failed to read Excel file. {data}"
    EXCEL_READ_REASON = "Error: Failed to read the Excel file. Reason: {error}"

    # Python Script
    PYTHON_READ = "Error: Failed to read Python script. {data}"
    PYTHON_READ_REASON = "Error: Failed to read the Python script. Reason: {error}"

    # Audio
    AUDIO_READ = "Error: Failed to read audio file. {data}"
    AUDIO_API = "Error: Could not request results from Google Web Speech API; {error}"
    AUDIO_FFMPEG = "Error: Failed to process audio. Reason: {error}. Ensure ffmpeg is installed and in your system's PATH."
    AUDIO_PARSE = "Error: Failed to parse the audio file. Reason: {error}"

    # Image/Video Analysis
    API_KEY_NOT_SET = "Error: GOOGLE_API_KEY environment variable not set"
    IMAGE_READ = "Error: Failed to read image file. {image_data}"


class DesktopToolErrors:
    """Error strings for desktop tool operations."""

    # PDF Operations
    PDF_INVALID_PAGE_RANGE = "Error: Invalid page range '{page_range}'. Total pages: {total_pages}"
    PDF_EXTRACT = "Error extracting PDF pages: {error}"
    PDF_DELETE = "Error deleting PDF pages: {error}"
    PDF_DELETE_ALL = "Error: Cannot delete all pages from PDF"
    PDF_FILE_NOT_FOUND = "Error: File not found: {pdf_path}"
    PDF_MERGE = "Error merging PDFs: {error}"
    PDF_SPLIT = "Error splitting PDF: {error}"
    PDF_TO_IMAGES = "Error converting PDF to images: {error}"
    PDF_TEXT_EXTRACT = "Error extracting text from PDF: {error}"

    # Image Operations
    IMAGE_CONVERT = "Error converting image: {error}"
    IMAGE_RESIZE_NO_DIMENSIONS = "Error: Must specify at least width or height"
    IMAGE_RESIZE = "Error resizing image: {error}"
    IMAGE_COMPRESS = "Error compressing image: {error}"

    # Batch Operations
    BATCH_CONVERT = "Error in batch conversion: {error}"
    BATCH_RENAME_NO_MATCH = "No files matched pattern '{pattern}'"
    BATCH_RENAME = "Error in batch rename: {error}"

    # File Operations
    FILE_ORGANIZE = "Error organizing files: {error}"
    FILE_DUPLICATES = "Error finding duplicates: {error}"

    # Document Operations
    DOCX_TO_PDF = "Error converting Word to PDF: {error}"

    # OCR
    OCR_NOT_INSTALLED = "Error: Tesseract OCR is not installed. Install with: pip install pytesseract and install Tesseract-OCR"
    OCR_FAILED = "Error performing OCR: {error}"

    # Video/Audio Operations
    VIDEO_NO_AUDIO = "Error: Video '{input_video}' has no audio track"
    AUDIO_EXTRACT = "Error extracting audio: {error}"
    VIDEO_COMPRESS = "Error compressing video: {error}"
    MEDIA_INFO = "Error getting media info: {error}"

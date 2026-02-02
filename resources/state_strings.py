"""Centralized state keys and success return strings for Desktop AI Agent.

This module contains:
1. State keys used in LangGraph agent states
2. Success/info return strings (non-error messages)

Error messages are in error_strings.py.
"""


class StateKeys:
    """Keys used in agent state dictionaries."""
    QUESTION = "question"
    MESSAGES = "messages"
    ANSWER = "answer"
    STEP_COUNT = "step_count"
    FILE_NAME = "file_name"


class ModelProviders:
    """Model provider identifiers for LLM client creation."""
    GOOGLE = "google"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"


class AgentReturns:
    """Non-error return strings for agent operations."""

    # File reference note
    FILE_REFERENCE_NOTE = "\n\nNote: This question references a file: {file_name}"


class ToolReturns:
    """Success return strings for tool operations."""

    # Time
    TIME_RESULT = "The current local time in {timezone} is: {local_time}"
    WIKI_RESULTS = "wiki_results"
    ARVIX_RESULTS = "arvix_results"


class DesktopToolReturns:
    """Success return strings for desktop tool operations."""

    # PDF Operations
    PDF_EXTRACT_SUCCESS = "Successfully extracted pages {page_range} from '{input_pdf}' to '{output_pdf}' ({pages_count} pages)"
    PDF_DELETE_SUCCESS = "Successfully deleted pages {page_range} from '{input_pdf}'. Saved to '{output_pdf}' ({pages_kept} pages remaining)"
    PDF_MERGE_SUCCESS = "Successfully merged {count} PDFs into '{output_pdf}' ({total_pages} total pages)"
    PDF_SPLIT_SUCCESS = "Successfully split '{input_pdf}' into {count} files in '{output_dir}'"
    PDF_TO_IMAGES_SUCCESS = "Successfully converted {count} pages to {format} images in '{output_dir}'"
    PDF_TEXT_EXTRACT_SUCCESS = "Successfully extracted text to '{output_txt}' ({char_count} characters)"

    # Image Operations
    IMAGE_CONVERT_SUCCESS = "Successfully converted '{input_image}' ({input_size:.1f}KB) to '{output_image}' ({output_size:.1f}KB)"
    IMAGE_RESIZE_SUCCESS = "Successfully resized '{input_image}' from {original_size} to {new_size}"
    IMAGE_COMPRESS_SUCCESS = "Compressed '{input_image}' ({original_size:.1f}KB) to '{output_image}' ({final_size:.1f}KB) at quality {quality}"

    # Batch Operations
    BATCH_CONVERT_SUCCESS = "Batch conversion complete: {converted} images converted, {failed} failed"

    # File Operations
    FILE_NO_DUPLICATES = "No duplicate files found"

    # Document Operations
    DOCX_TO_PDF_SUCCESS = "Successfully converted '{input_docx}' to '{output_pdf}'"
    OCR_SUCCESS = "Successfully extracted text to '{output_txt}' ({char_count} characters)"

    # Video/Audio Operations
    AUDIO_EXTRACT_SUCCESS = "Successfully extracted audio from '{input_video}' to '{output_audio}' (duration: {duration:.1f}s)"
    VIDEO_COMPRESS_SUCCESS = "Compressed '{input_video}' ({original_size:.1f}MB) to '{output_video}' ({final_size:.1f}MB)"

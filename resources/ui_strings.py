"""Centralized UI strings for DeskGenie.

All user-facing strings displayed in the UI log panel and console are defined here.
This makes it easy to update messaging and enables future localization.
"""


class AgentStrings:
    """Strings for agent operations."""

    # Separators
    LINE_SEPARATOR = "=" * 60

    # Initialization
    ERROR_INSTANTIATING_AGENT = "Failed to Create Agent: {error}"
    GOOGLE_API_KEY_NOT_FOUND = "GOOGLE_API_KEY Not Found"

    # Execution
    RUNNING_AGENT_ON_QUESTIONS = "Processing {total} Questions..."
    SKIPPING_MISSING_DATA = "Skipping Invalid Questions: {item}"
    TASK_RESULT = "Task {task_id} Complete: {answer}"
    QUESTION_TEXT = "Q{num}: {question}"
    EXCEPTION_RUNNING_AGENT = "Agent Error (Task {task_id}): {error}"

    # LangGraph Agent
    LANGGRAPH_STARTING = "LangGraph Agent Starting: {question}"
    LANGGRAPH_FILE = "File: {file_name}"
    LANGGRAPH_REQUESTING_TOOLS = "Requesting {count} Tool(s): {tools}"
    LANGGRAPH_MAX_STEPS = "Maximum Steps Reached (40)"
    LANGGRAPH_NULL_ANSWER = "Agent Returned No Answer"

    # ReAct Agent
    REACT_STARTING = "ReAct Agent Starting: {question}"
    REACT_NO_MESSAGES = "Agent Returned No Messages"
    REACT_NULL_ANSWER = "Agent Returned No Answer"

    # LLM Calls
    STEP_CALLING_LLM = "Step {step}: Calling LLM with {count} messages"
    RETRY_ATTEMPT = "Retry {attempt}/{max_retries}: Timeout"
    RETRY_WAITING = "Retrying in {delay:.1f} seconds..."
    RETRIES_EXHAUSTED = "Retries Exhausted ({max_retries})"
    LLM_INVOCATION_FAILED_RETRIES = "LLM Failed After Retries: {error}"
    LLM_INVOCATION_FAILED = "LLM Failed: {error}"
    AGENT_INVOCATION_FAILED_RETRIES = "Agent Failed After Retries: {error}"
    AGENT_INVOCATION_FAILED = "Agent Failed: {error}"

    # Results
    FINAL_ANSWER = "Final Answer: {answer}"


class ToolStrings:
    """Strings for tool operations."""

    # Web Search
    WEBSEARCH_CALLED = "WebSearch: {query}"
    WEBSEARCH_RESULTS = "Web Search Results: {count}"

    # Wikipedia
    WIKI_SEARCH_CALLED = "Wikipedia: {query}"
    WIKI_RESULTS = "Wikipedia Results: {count} characters"

    # ArXiv
    ARXIV_SEARCH_CALLED = "ArXivSearch: {query}"
    ARXIV_RESULTS = "ArXiv Results: {count} characters"

    # YouTube
    YOUTUBE_TRANSCRIPT_CALLED = "YouTube Transcript: {url}"
    YOUTUBE_TRANSCRIPT_RESULT = "YouTube Transcript Results: {count} characters"
    YOUTUBE_TRANSCRIPT_ERROR = "Failed to Get Transcript: {url}"
    ANALYZE_YOUTUBE_CALLED = "Analyzing YouTube Video: {url}"
    ANALYZE_YOUTUBE_ERROR = "Error Analyzing YouTube Video: {url}"

    # Webpage
    WEBPAGE_CONTENT_CALLED = "Webpage: {url}"
    WEBPAGE_CONTENT_RESULT = "Webpage Content: {count} characters"

    # Files
    READ_EXCEL_CALLED = "Excel: {file_name}"
    READ_PYTHON_CALLED = "Python Script: {file_name}"
    PARSE_AUDIO_CALLED = "Audio File: {file_name}"

    # Image Analysis
    ANALYZE_IMAGE_CALLED = "Analyzing Image: {file_name}"
    ANALYZE_IMAGE_ERROR = "Error Analyzing Image: {file_name}"


class QuestionRunnerStrings:
    """Strings for question runner operations."""

    # Loading
    LOADED_QUESTIONS = "Loaded {count} questions from {file_path}"
    ERROR_LOADING_GROUND_TRUTH = "Error loading ground truth: {error}"
    ERROR_LOADING_QUESTIONS = "Error loading questions: {error}"

    # Validation
    INVALID_QUESTIONS_DATA = "Invalid questions data: {error}"
    INVALID_FILTER = "Invalid filter: {error}"

    # Processing
    PROCESSING_HEADER = "=== Processing GAIA Questions ==="
    RUNNING_SELECTED = "Processing {count} Selected Questions"
    RUNNING_ALL = "Processing All {count} Questions"
    COMPLETED_HEADER = "=== Completed GAIA Questions ==="
    ERROR_INITIALIZING_AGENT = "Error initializing agent."

    # Verification
    VERIFICATION_HEADER = "=== Verification Results ==="
    VERIFYING_RESULTS = "Verifying {results} results against {truth} ground truth entries"
    QUESTION_CORRECT = "Q{num}: ✓ Correct ({match_type}) (expected: {expected}, got: {actual})"
    QUESTION_INCORRECT = "Q{num}: ✗ Incorrect (expected: {expected}, got: {actual})"
    QUESTION_NO_TRUTH = "Q{num}: No ground truth found"

    # Summary
    SUMMARY = "SUMMARY: {correct}/{total} correct ({accuracy:.1f}%)"
    RUNTIME = "Runtime: {minutes}m {seconds}s"


class DesktopToolStrings:
    """Strings for desktop tool operations."""

    # PDF Tools
    PDF_EXTRACT_PAGES = "Extracting PDF Pages: {input_pdf}"
    PDF_DELETE_PAGES = "Deleting PDF Pages: {input_pdf}"
    PDF_MERGE = "Merging PDFs: {output_pdf}"
    PDF_SPLIT = "Splitting PDF: {input_pdf}"
    PDF_TO_IMAGES = "Converting PDF to Images: {input_pdf}"
    EXTRACT_TEXT_PDF = "Extracting Text from PDF: {input_pdf}"

    # Image Tools
    IMAGE_CONVERT = "Converting Image: {input_image}"
    IMAGE_RESIZE = "Resizing Image: {input_image}"
    IMAGE_COMPRESS = "Compressing Image: {input_image}"
    BATCH_CONVERT = "Batch Converting Images: {input_dir}"

    # File Management Tools
    BATCH_RENAME = "Renaming Files: {directory}"
    ORGANIZE_FILES = "Organizing Files: {source_dir}"
    FIND_DUPLICATES = "Finding Duplicates: {directory}"

    # Document Tools
    WORD_TO_PDF = "Converting Word to PDF: {input_docx}"
    OCR_IMAGE = "Extracting Text via OCR: {input_image}"

    # Media Tools
    VIDEO_TO_AUDIO = "Extracting Audio: {input_video}"
    COMPRESS_VIDEO = "Compressing Video: {input_video}"
    GET_MEDIA_INFO = "Media Info: {file_path}"


class APIStrings:
    """Strings for API operations."""

    # Chat
    CHAT_COMPLETED_WITH_TIME = "Chat completed in {minutes}m {seconds}s"
    CHAT_FAILED = "Chat task failed: {error}"

    # Benchmark
    BENCHMARK_COMPLETED = "GAIA Benchmark completed"
    BENCHMARK_FAILED = "GAIA Benchmark failed: {error}"
    BENCHMARK_RESULT_SUMMARY = "{correct}/{total} correct ({accuracy:.1f}%)"
    BENCHMARK_RESULT_FALLBACK = "Benchmark completed - see logs for details"

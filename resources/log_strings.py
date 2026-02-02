"""Centralized log strings for DeskGenie.

This module contains all informational and diagnostic log messages
used throughout the application. These messages are used with print()
statements and logger instances to provide consistent, professional
messaging to users and developers.

Benefits of centralizing log strings:
- Consistent messaging across the application
- Easy maintenance and updates
- Professional, well-formatted messages
- Potential for future localization
- Easier testing and validation
"""


class LogSeparators:
    """Visual separator strings for log output."""
    
    HEADER = '=' * 60
    SECTION = '-' * 74
    SUBSECTION = '-' * 50


class CLIMessages:
    """Messages for command-line interface operations."""
    
    # Query execution
    QUERY_HEADER = f"\n{LogSeparators.HEADER}"
    QUERY_PREFIX = "Query: {query}"
    QUERY_SEPARATOR = f"\n{LogSeparators.HEADER}\n"
    
    # Execution timing
    COMPLETED_IN = "Completed in {minutes}m {seconds}s"
    RESPONSE_PREFIX = "Response: {result}"
    RESPONSE_SEPARATOR = f"\n{LogSeparators.HEADER}\n{LogSeparators.HEADER}\n"
    
    # Startup messages
    SECTION_SEPARATOR = f"\n{LogSeparators.SECTION}\n"
    LAUNCHING_UI = "Launching DeskGenie Web UI..."
    BACKEND_API = "  Backend API: http://localhost:8000"
    FRONTEND_PRODUCTION = "  Frontend:    http://localhost:8000 (production) or http://localhost:5173 (dev)"
    DEV_INSTRUCTIONS = "\nFor development, run 'cd frontend && npm run dev' in a separate terminal."
    
    # Benchmark mode
    RUNNING_BENCHMARK = "Running GAIA benchmark on {count} questions..."
    
    # Error messages
    ERROR_PREFIX = "Error: {error}"


class APIMessages:
    """Messages for API server operations."""
    
    # Server lifecycle
    SERVER_STARTING = "[API] Server starting..."
    SERVER_SHUTTING_DOWN = "[API] Server shutting down, cancelling background tasks..."
    SHUTDOWN_COMPLETE = "[API] Shutdown complete."


class LangGraphMessages:
    """Messages for LangGraph agent operations."""
    
    # API configuration
    GOOGLE_API_KEY_NOT_FOUND = "GOOGLE_API_KEY environment variable not set"
    
    # Retry logic
    RETRY_ATTEMPT = "Retry attempt {attempt}/{max_retries}..."
    RETRY_WAITING = "Waiting {delay} seconds before retry..."
    RETRIES_EXHAUSTED = "All {max_retries} retry attempts exhausted"
    
    # LLM invocation
    LLM_INVOCATION_FAILED = "LLM invocation failed: {error}"
    LLM_INVOCATION_FAILED_RETRIES = "LLM invocation failed after retries: {error}"
    
    # Execution limits
    MAX_STEPS_REACHED = "Maximum step limit (40) reached"
    FILE_REFERENCE = "Processing file: {file_name}"
    NULL_ANSWER_WARNING = "Agent returned null answer, returning NO_ANSWER"
    AGENT_INVOCATION_FAILED = "Agent invocation failed: {error}"


class ReactMessages:
    """Messages for ReAct LangGraph agent operations."""
    
    # Execution
    NO_MESSAGES_WARNING = "No messages in state, returning NO_ANSWER"
    NULL_ANSWER_WARNING = "Agent returned null answer, returning NO_ANSWER"
    
    # Retry logic
    RETRY_ATTEMPT = "Retry attempt {attempt}/{max_retries}..."
    RETRY_WAITING = "Waiting {delay} seconds before retry..."
    RETRIES_EXHAUSTED = "All {max_retries} retry attempts exhausted"
    
    # Errors
    AGENT_INVOCATION_FAILED_RETRIES = "Agent failed after retries: {error}"
    AGENT_INVOCATION_FAILED = "Agent invocation failed: {error}"


class AgentRunnerMessages:
    """Messages for agent runner operations."""
    
    # Initialization
    ERROR_INSTANTIATING_AGENT = "Failed to instantiate agent: {error}"
    RUNNING_AGENT_ON_QUESTIONS = "Running agent on {total} questions..."
    
    # Question processing
    SKIPPING_MISSING_DATA = "Skipping question {item} due to missing task_id or question_text"
    LINE_SEPARATOR = f"\n{LogSeparators.HEADER}"
    QUESTION_TEXT = "Question {num}: {question}"
    EXCEPTION_RUNNING_AGENT = "Exception while running agent for task {task_id}: {error}"


class QuestionRunnerMessages:
    """Messages for question runner operations."""
    
    # Loading
    LOADED_QUESTIONS = "Loaded {count} questions from {file_path}"
    ERROR_LOADING_GROUND_TRUTH = "Failed to load ground truth: {error}"
    
    # Verification
    VERIFICATION_HEADER = f"\n{LogSeparators.HEADER}\nVERIFICATION RESULTS\n{LogSeparators.HEADER}"
    VERIFYING_RESULTS = "Verifying {results} results against {truth} ground truth entries"
    QUESTION_CORRECT = "Question {num}: ✓ Correct"
    QUESTION_INCORRECT = "Question {num}: ✗ Incorrect\n  Expected: {expected}\n  Got: {answer}"
    QUESTION_NO_TRUTH = "Question {num}: ⚠ No ground truth available"
    
    # Runtime
    RUNTIME = "Total runtime: {minutes}m {seconds}s"
    
    # Processing
    PROCESSING_HEADER = f"\n{LogSeparators.HEADER}\nPROCESSING QUESTIONS\n{LogSeparators.HEADER}"
    ERROR_LOADING_QUESTIONS = "Failed to load questions: {error}"
    INVALID_QUESTIONS_DATA = "Invalid questions data: {error}"
    INVALID_FILTER = "Invalid filter specified: {error}"
    RUNNING_SELECTED = "Running {count} selected questions"
    RUNNING_ALL = "Running all {count} questions"
    ERROR_INITIALIZING_AGENT = "Failed to initialize agent"


class ConfigMessages:
    """Messages for configuration operations."""

    # Config loading
    CONFIG_PARSE_ERROR = "[WARNING] Invalid JSON in config.json: {error}. Using default settings."
    CONFIG_READ_ERROR = "[WARNING] Could not read config.json: {error}. Using default settings."
    CONFIG_PATH_INFO = "  Config location: {path}"


class LangfuseMessages:
    """Messages for Langfuse tracking operations."""

    # Installation check
    NOT_INSTALLED = "[INFO] Langfuse not installed. Tracking is disabled. Install with: pip install langfuse"
    
    # Configuration
    TRACKING_ENABLED = "[LANGFUSE] Tracking enabled (project: {project_name}, host: {host})"
    TRACKING_DISABLED = "[LANGFUSE] Tracking disabled. Set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY to enable."


class ResultFormatterMessages:
    """Messages for result formatter operations."""
    
    # Note: These are handled via colorama formatting, not direct strings
    # The actual messages are generated dynamically in the formatter


class UtilityMessages:
    """Messages for utility functions."""
    
    # Retry logic
    RETRY_FAILED = "[RETRY] Attempt {attempt}/{max_retries} failed: {error}"
    RETRY_WAITING = "[RETRY] Retrying in {delay:.1f} seconds..."
    RETRY_EXHAUSTED = "[RETRY] All {max_retries} retries exhausted"
    
    # Content conversion
    CONTENT_DICT_WARNING = "[WARNING] Content was dict without 'text' field, converting to string"


class AgentLogging:
    """Logging strings for agent operations."""

    # Separators
    LINE_SEPARATOR = "=" * 60

    # Initialization
    ERROR_INSTANTIATING_AGENT = "Error instantiating agent: {error}"
    GOOGLE_API_KEY_NOT_FOUND = "GOOGLE_API_KEY not found - analyze_youtube_video will fail"

    # Execution
    RUNNING_AGENT_ON_QUESTIONS = "Running agent on {total} questions..."
    SKIPPING_MISSING_DATA = "Skipping item with missing task_id or question: {item}"
    TASK_RESULT = "Task {task_id}: {answer}"
    QUESTION_TEXT = "Q{num}: {question}"
    EXCEPTION_RUNNING_AGENT = "Exception running agent on task {task_id}: {error}"

    # LangGraph Agent
    LANGGRAPH_STARTING = "LangGraph Agent starting - Question: {question}"
    LANGGRAPH_FILE = "File: {file_name}"
    LANGGRAPH_REQUESTING_TOOLS = "Agent requesting {count} tool(s): {tools}"
    LANGGRAPH_MAX_STEPS = "Max steps (40) reached, forcing termination"
    LANGGRAPH_NULL_ANSWER = "Agent completed but returned None as answer"

    # ReAct Agent
    REACT_STARTING = "ReAct Agent starting - Question: {question}"
    REACT_NO_MESSAGES = "Agent completed but returned no messages"
    REACT_NULL_ANSWER = "Agent completed but returned None as answer"

    # LLM Calls
    STEP_CALLING_LLM = "Step {step}: Calling LLM with {count} messages"
    RETRY_ATTEMPT = "Attempt {attempt}/{max_retries} failed with 504 DEADLINE_EXCEEDED"
    RETRY_WAITING = "Retrying in {delay:.1f} seconds..."
    RETRIES_EXHAUSTED = "All {max_retries} retries exhausted for 504 error"
    LLM_INVOCATION_FAILED_RETRIES = "LLM invocation failed after retries: {error}"
    LLM_INVOCATION_FAILED = "LLM invocation failed: {error}"
    AGENT_INVOCATION_FAILED_RETRIES = "Agent invocation failed after retries: {error}"
    AGENT_INVOCATION_FAILED = "Agent invocation failed: {error}"

    # Results
    FINAL_ANSWER = "Final answer: {answer}"


class ToolLogging:
    """Logging strings for tool operations."""

    # Web Search
    WEBSEARCH_CALLED = "websearch called: {query}"
    WEBSEARCH_RESULTS = "websearch results: {count}"

    # Wikipedia
    WIKI_SEARCH_CALLED = "wiki_search called: {query}"
    WIKI_RESULTS = "wiki_results: {count} characters"

    # ArXiv
    ARXIV_SEARCH_CALLED = "arvix_search called: {query}"
    ARXIV_RESULTS = "arvix_results: {count} characters"

    # YouTube
    YOUTUBE_TRANSCRIPT_CALLED = "get_youtube_transcript called: {url}"
    YOUTUBE_TRANSCRIPT_RESULT = "youtube_transcript: {count} characters"
    YOUTUBE_TRANSCRIPT_ERROR = "Failed to get transcript for video {url}: {error}"
    ANALYZE_YOUTUBE_CALLED = "analyze_youtube_video called: {url} with question: {question}"
    ANALYZE_YOUTUBE_ERROR = "Error analyzing YouTube video {url}: {error}"

    # Webpage
    WEBPAGE_CONTENT_CALLED = "get_webpage_content called: with url {url}"
    WEBPAGE_CONTENT_RESULT = "webpage_content: {count} characters"

    # Files
    READ_EXCEL_CALLED = "read_excel_file called: with file {file_name}"
    READ_PYTHON_CALLED = "read_python_script called: with file {file_name}"
    PARSE_AUDIO_CALLED = "parse_audio_file called: with file {file_name}"

    # Image Analysis
    ANALYZE_IMAGE_CALLED = "analyze_image called: {file_name} with question: {question}"
    ANALYZE_IMAGE_ERROR = "Error analyzing image {file_name}: {error}"


class QuestionRunnerLogging:
    """Logging strings for question runner operations."""

    # Loading
    LOADED_QUESTIONS = "Loaded {count} questions from {file_path}"
    ERROR_LOADING_GROUND_TRUTH = "Error loading ground truth: {error}"
    ERROR_LOADING_QUESTIONS = "Error loading questions: {error}"

    # Validation
    INVALID_QUESTIONS_DATA = "Invalid questions data: {error}"
    INVALID_FILTER = "Invalid filter: {error}"

    # Processing
    PROCESSING_HEADER = "=== Processing GAIA Questions ==="
    RUNNING_SELECTED = "Running {count} selected questions"
    RUNNING_ALL = "Running all {count} questions"
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


class DesktopToolLogging:
    """Logging strings for desktop tool operations."""

    # PDF Tools
    PDF_EXTRACT_PAGES = "pdf_extract_pages: {input_pdf} -> {output_pdf}, pages: {page_range}"
    PDF_DELETE_PAGES = "pdf_delete_pages: {input_pdf} -> {output_pdf}, delete pages: {page_range}"
    PDF_MERGE = "pdf_merge: {pdf_files} -> {output_pdf}"
    PDF_SPLIT = "pdf_split: {input_pdf} -> {output_dir}, {pages_per_split} pages each"
    PDF_TO_IMAGES = "pdf_to_images: {input_pdf} -> {output_dir}"
    EXTRACT_TEXT_PDF = "extract_text_from_pdf: {input_pdf}"

    # Image Tools
    IMAGE_CONVERT = "image_convert: {input_image} -> {output_image}"
    IMAGE_RESIZE = "image_resize: {input_image} -> {output_image}"
    IMAGE_COMPRESS = "image_compress: {input_image} -> {output_image}, target: {target_size_kb}KB"
    BATCH_CONVERT = "batch_convert_images: {input_dir} -> {output_dir}"

    # File Management Tools
    BATCH_RENAME = "batch_rename_files: {directory}, pattern: {pattern} -> {replacement}"
    ORGANIZE_FILES = "organize_files_by_type: {source_dir}, by: {organize_by}"
    FIND_DUPLICATES = "find_duplicate_files: {directory}, by_content: {by_content}"

    # Document Tools
    WORD_TO_PDF = "word_to_pdf: {input_docx} -> {output_pdf}"
    OCR_IMAGE = "ocr_image: {input_image}"

    # Media Tools
    VIDEO_TO_AUDIO = "video_to_audio: {input_video} -> {output_audio}"
    COMPRESS_VIDEO = "compress_video: {input_video} -> {output_video}, target: {target_size_mb}MB"
    GET_MEDIA_INFO = "get_media_info: {file_path}"


class APILogging:
    """Logging strings for API operations."""

    # Chat
    CHAT_COMPLETED_WITH_TIME = "Chat completed in {minutes}m {seconds}s"
    CHAT_FAILED = "Chat task failed: {error}"

    # Benchmark
    BENCHMARK_COMPLETED = "GAIA Benchmark completed"
    BENCHMARK_FAILED = "GAIA Benchmark failed: {error}"
    BENCHMARK_RESULT_SUMMARY = "{correct}/{total} correct ({accuracy:.1f}%)"
    BENCHMARK_RESULT_FALLBACK = "Benchmark completed - see logs for details"

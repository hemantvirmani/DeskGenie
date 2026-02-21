"""Centralized UI strings for Desktop AI Agent.

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
    SHUTDOWN_STOPPING_AGENT_LOOP = "Shutdown requested. Stopping remaining question processing."

    # LangGraph Agent
    LANGGRAPH_STARTING = "LangGraph Agent Starting: {question}"
    LANGGRAPH_FILE = "File: {file_name}"
    LANGGRAPH_REQUESTING_TOOLS = "Requesting {count} Tool(s): {tools}"
    LANGGRAPH_MAX_STEPS = "Maximum Steps Reached (40)"
    CALLING_TOOLS = "Calling tools"
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
    WEBSEARCH_CALLED = "Web Search"
    WEBSEARCH_RESULTS = "Web Search Results: {count}"

    # Wikipedia
    WIKI_SEARCH_CALLED = "Wikipedia"
    WIKI_RESULTS = "Wikipedia Results: {count} characters"

    # ArXiv
    ARXIV_SEARCH_CALLED = "ArXiv Search"
    ARXIV_RESULTS = "ArXiv Results: {count} characters"

    # YouTube
    YOUTUBE_TRANSCRIPT_CALLED = "YouTube Transcript"
    YOUTUBE_TRANSCRIPT_RESULT = "YouTube Transcript Results: {count} characters"
    YOUTUBE_TRANSCRIPT_ERROR = "Failed to Get Transcript: {url}"
    ANALYZE_YOUTUBE_CALLED = "YouTube Video"
    ANALYZE_YOUTUBE_ERROR = "Error Analyzing YouTube Video: {url}"

    # Webpage
    WEBPAGE_CONTENT_CALLED = "Web Page"
    WEBPAGE_CONTENT_RESULT = "Webpage Content: {count} characters"

    # Files
    READ_EXCEL_CALLED = "Excel File"
    READ_PYTHON_CALLED = "Python Script"
    PARSE_AUDIO_CALLED = "Audio File"

    # Image Analysis
    ANALYZE_IMAGE_CALLED = "Image Analysis"
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
    SHUTDOWN_STOPPING_VERIFICATION = "Shutdown requested. Stopping verification early."

    # Summary
    SUMMARY = "SUMMARY: {correct}/{total} correct ({accuracy:.1f}%)"
    RUNTIME = "Runtime: {minutes}m {seconds}s"


class DesktopToolStrings:
    """Strings for desktop tool operations.

    Each constant holds the display name passed as the first argument to
    logger.tool_call(name, detail). The detail (file path, directory, etc.)
    is passed separately at the call site.
    """

    # PDF Tools
    PDF_EXTRACT_PAGES = "Extracting PDF Pages"
    PDF_DELETE_PAGES = "Deleting PDF Pages"
    PDF_MERGE = "Merging PDFs"
    PDF_SPLIT = "Splitting PDF"
    PDF_TO_IMAGES = "Converting PDF to Images"
    EXTRACT_TEXT_PDF = "Extracting Text from PDF"

    # Image Tools
    IMAGE_CONVERT = "Converting Image"
    IMAGE_RESIZE = "Resizing Image"
    IMAGE_COMPRESS = "Compressing Image"
    BATCH_CONVERT = "Batch Converting Images"
    IMAGES_TO_PDF = "Converting Images to PDF"

    # File Management Tools
    BATCH_RENAME = "Renaming Files"
    ORGANIZE_FILES = "Organizing Files"
    FIND_DUPLICATES = "Finding Duplicates"

    # Document Tools
    WORD_TO_PDF = "Converting Word to PDF"
    OCR_IMAGE = "Extracting Text via OCR"

    # Media Tools
    VIDEO_TO_AUDIO = "Extracting Audio"
    COMPRESS_VIDEO = "Compressing Video"
    GET_MEDIA_INFO = "Media Info"

    # Directory / System Tools
    USER_DIRECTORY = "User Directory"
    SYSTEM_DIRECTORY = "System Directory"
    LIST_USER_DIRECTORIES = "List User Directories"
    LIST_SYSTEM_DIRECTORIES = "List System Directories"
    RESOLVING_PATH = "Resolving Path"
    FOLDER_ALIASES = "Folder Aliases"
    PREFERENCE = "Preference"
    LIST_DIRECTORY = "List Directory"
    LIST_FILES_RECURSIVE = "List Files Recursively"


class APIStrings:
    """Strings for API operations."""

    # API Identity
    API_TITLE = "DeskGenie API"
    SERVICE_NAME = "DeskGenie"

    # Chat
    CHAT_COMPLETED_WITH_TIME = "Chat completed in {minutes}m {seconds}s"
    CHAT_FAILED = "Chat task failed: {error}"

    # Benchmark
    BENCHMARK_COMPLETED = "GAIA Benchmark completed"
    BENCHMARK_FAILED = "GAIA Benchmark failed: {error}"
    BENCHMARK_RESULT_SUMMARY = "{correct}/{total} correct ({accuracy:.1f}%)"
    BENCHMARK_RESULT_FALLBACK = "Benchmark completed - see logs for details"

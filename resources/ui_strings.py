"""Centralized UI strings for DeskGenie.

All user-facing strings displayed in the UI log panel and console are defined here.
This makes it easy to update messaging and enables future localization.
"""


class AgentStrings:
    """Strings for agent operations."""

    # Initialization
    ERROR_INSTANTIATING_AGENT = "Error instantiating agent: {error}"
    GOOGLE_API_KEY_NOT_FOUND = "GOOGLE_API_KEY not found - analyze_youtube_video will fail"

    # Execution
    RUNNING_AGENT_ON_QUESTIONS = "Running agent on {total} questions..."
    SKIPPING_MISSING_DATA = "Skipping item with missing task_id or question: {item}"
    TASK_RESULT = "Task {task_id}: {answer}"
    QUESTION_TEXT = "Question: {question}"
    EXCEPTION_RUNNING_AGENT = "Exception running agent on task {task_id}: {error}"

    # LangGraph Agent
    LANGGRAPH_STARTING = "LangGraph Agent starting - Question: {question}"
    LANGGRAPH_FILE = "File: {file_name}"
    LANGGRAPH_NO_MORE_TOOLS = "Agent produced answer (no more tool calls)"
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


class ToolStrings:
    """Strings for tool operations."""

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
    TESTING_SELECTED = "Testing {count} selected questions (indices: {indices})"
    TESTING_ALL = "Testing all {count} questions"
    COMPLETED_HEADER = "=== Completed GAIA Questions ==="
    ERROR_INITIALIZING_AGENT = "Error initializing agent."

    # Verification
    VERIFICATION_HEADER = "=== Verification Results ==="
    VERIFYING_RESULTS = "Verifying {results} results against {truth} ground truth entries"
    QUESTION_CORRECT = "Q{num}: ✓ Correct"
    QUESTION_INCORRECT = "Q{num}: ✗ Incorrect (expected: {expected}, got: {actual})"
    QUESTION_NO_TRUTH = "Q{num}: No ground truth found"

    # Summary
    SUMMARY = "SUMMARY: {correct}/{total} correct ({accuracy:.1f}%)"
    RUNTIME = "Runtime: {minutes}m {seconds}s"


class DesktopToolStrings:
    """Strings for desktop tool operations."""

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


class APIStrings:
    """Strings for API operations."""

    # Chat
    CHAT_COMPLETED_WITH_TIME = "Chat completed in {minutes}m {seconds}s"
    CHAT_FAILED = "Chat task failed: {error}"

    # Benchmark
    STARTING_BENCHMARK = "Starting Benchmark with {description}"
    BENCHMARK_COMPLETED = "Benchmark completed"
    BENCHMARK_FAILED = "Benchmark failed: {error}"

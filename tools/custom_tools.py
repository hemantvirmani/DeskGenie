import concurrent.futures
import pytz
import datetime
from ddgs import DDGS
from bs4 import BeautifulSoup
import requests
import re
import io
import os
from google import genai
from google.genai import types
from app import config

from langchain_community.document_loaders import WikipediaLoader
from langchain_community.document_loaders import ArxivLoader
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import extract
from langchain_core.tools import tool
from utils.langfuse_tracking import track_tool_call
from utils.log_streamer import log_tool_call
from resources.ui_strings import ToolStrings as S
from resources.log_strings import ToolLogging as L
from resources.state_strings import ToolReturns as TR
from resources.error_strings import ToolErrors as TE

import pandas as pd
import speech_recognition as sr
from pydub import AudioSegment
from pypdf import PdfReader
from io import BytesIO
from markdownify import markdownify as md

# ============================================================================
# Helper Functions (must be defined before tools that use them)
# ============================================================================

def _sanitize_file_path(file_name: str) -> tuple:
    """
    Sanitize file name to prevent path traversal attacks.

    Args:
        file_name: The file name to sanitize

    Returns:
        tuple: (is_valid: bool, sanitized_name_or_error: str)
    """
    # Check for path traversal attempts
    if '..' in file_name or file_name.startswith('/') or file_name.startswith('\\'):
        return False, "Invalid file name: path traversal not allowed"

    # Check for absolute paths (Windows and Unix)
    if os.path.isabs(file_name):
        return False, "Invalid file name: absolute paths not allowed"

    # Normalize the path and ensure it doesn't escape the files directory
    normalized = os.path.normpath(file_name)
    if normalized.startswith('..') or os.path.isabs(normalized):
        return False, "Invalid file name: path traversal detected"

    return True, normalized

def _get_file_content(file_name: str, mode: str = 'binary'):
    """
    Helper function to get file content from local filesystem or remote URL.

    Args:
        file_name: The file name (without 'files/' prefix)
        mode: 'binary' for bytes, 'text' for string

    Returns:
        tuple: (success: bool, data: bytes/str or error_message: str)
    """
    # Sanitize file name first
    is_valid, result = _sanitize_file_path(file_name)
    if not is_valid:
        return False, result

    file_name = result  # Use sanitized name
    file_path = f"files/{file_name}"

    # Read local file
    if os.path.exists(file_path):
        try:
            if mode == 'binary':
                with open(file_path, 'rb') as f:
                    return True, f.read()
            else:  # text mode
                with open(file_path, 'r') as f:
                    return True, f.read()
        except Exception as e:
            return False, f"Error reading local file: {e}"
    else:
        return False, f"File not found: {file_path}"

def _get_mime_type(file_name: str) -> str:
    """Helper function to determine MIME type from file extension."""
    ext = file_name.lower().split('.')[-1]
    mime_types = {
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'gif': 'image/gif',
        'webp': 'image/webp',
        'bmp': 'image/bmp'
    }
    return mime_types.get(ext, 'image/png')

# ============================================================================
# Tools
# ============================================================================

@tool
@track_tool_call("calculate")
@log_tool_call(L.CALCULATE_CALLED)
def calculate(operation: str, a: float, b: float) -> str:
    """Perform a basic math operation on two numbers.

    Args:
        operation: The operation to perform — 'add', 'subtract', 'multiply', 'divide', 'power', 'modulus'
        a: first number
        b: second number
    """
    if operation == "add":
        return str(a + b)
    elif operation == "subtract":
        return str(a - b)
    elif operation == "multiply":
        return str(a * b)
    elif operation == "divide":
        if b == 0:
            return TE.DIVIDE_BY_ZERO
        return str(a / b)
    elif operation == "power":
        return str(a ** b)
    elif operation == "modulus":
        return str(int(a) % int(b))
    return f"Unknown operation: {operation}. Valid: add, subtract, multiply, divide, power, modulus"

@tool
@track_tool_call("string_reverse")
@log_tool_call(L.STRING_REVERSE_CALLED)
def string_reverse(input_string: str) -> str:
    """
    Reverses the input string. Useful whenever a string seems to be non-sensical or
    contains a lot of gibberish. This function can be used to reverse the string
    and check if it makes more sense when reversed.

    Args:
        input_string (str): The string to reverse.

    Returns:
        str: The reversed string.
    """
    return input_string[::-1]


@tool
@track_tool_call("get_current_time_in_timezone")
@log_tool_call(L.CURRENT_TIME_CALLED)
def get_current_time_in_timezone(timezone: str) -> str:
    """A tool that fetches the current local time in a specified timezone.
    Args:
        timezone: A string representing a valid timezone (e.g., 'America/New_York').
    """
    try:
        # Create timezone object
        tz = pytz.timezone(timezone)
        # Get current time in that timezone
        local_time = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        return TR.TIME_RESULT.format(timezone=timezone, local_time=local_time)
    except Exception as e:
        return TE.TIME_FETCH.format(timezone=timezone, error=str(e))

@tool
@track_tool_call("websearch")
@log_tool_call(S.WEBSEARCH_CALLED)
def websearch(query: str) -> str:
    """This tool will search the web using DuckDuckGo.

    Args:
        query: The search query.
    """

    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=config.WEBSEARCH_MAX_RESULTS)
            if results:
                return "\n\n".join([f"Title: {r['title']}\nURL: {r['href']}\nSnippet: {r['body']}" for r in results])
            return TE.SEARCH_NO_RESULTS
    except Exception as e:
        return TE.SEARCH_FAILED.format(error=str(e))

@tool
@track_tool_call("wiki_search")
@log_tool_call(S.WIKI_SEARCH_CALLED)
def wiki_search(query: str) -> str:
    """Search Wikipedia for a query and return maximum 3 results.

    Args:
        query: The search query."""
    try:
        search_docs = WikipediaLoader(query=query, load_max_docs=config.WIKI_MAX_DOCS).load()
        formatted_search_docs = "\n\n---\n\n".join(
            [
                f'<Document source="{doc.metadata["source"]}" page="{doc.metadata.get("page", "")}"/>\n{doc.page_content}\n</Document>'
                for doc in search_docs
            ])
        return {TR.WIKI_RESULTS: formatted_search_docs}
    except Exception as e:
        return TE.WIKI_SEARCH.format(error=e)

@tool
@track_tool_call("arvix_search")
@log_tool_call(S.ARXIV_SEARCH_CALLED)
def arvix_search(query: str) -> str:
    """Search Arxiv for a query and return maximum 3 result.

    Args:
        query: The search query."""
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                lambda: ArxivLoader(query=query, load_max_docs=config.ARXIV_MAX_DOCS).load()
            )
            search_docs = future.result(timeout=config.ARXIV_TIMEOUT_SECONDS)
        formatted_search_docs = "\n\n---\n\n".join(
            [
                f'<Document source="{doc.metadata["source"]}" page="{doc.metadata.get("page", "")}"/>\n{doc.page_content[:1000]}\n</Document>'
                for doc in search_docs
            ])
        return {TR.ARVIX_RESULTS: formatted_search_docs}
    except concurrent.futures.TimeoutError:
        return TE.ARXIV_SEARCH.format(error=f"ArXiv timed out after {config.ARXIV_TIMEOUT_SECONDS}s — try websearch instead")
    except Exception as e:
        return TE.ARXIV_SEARCH.format(error=e)

@tool
@track_tool_call("youtube_tool")
@log_tool_call(S.YOUTUBE_CALLED)
def youtube_tool(youtube_url: str, question: str = "") -> str:
    """Get information from a YouTube video.

    Leave question empty to get the spoken transcript.
    Provide a question to analyze the video visually using AI (use for visual content not in the transcript).

    Args:
        youtube_url (str): The full HTTPS URL of the YouTube video.
        question (str): Optional question about the video content. Leave empty to get the transcript.
    """
    if not question:
        try:
            video_id = extract.video_id(youtube_url)
            ytt_api = YouTubeTranscriptApi()
            transcript = ytt_api.fetch(video_id)
            return '\n'.join([s.text for s in transcript.snippets])
        except Exception as e:
            return S.YOUTUBE_TRANSCRIPT_ERROR.format(url=youtube_url, error=e)
    else:
        try:
            api_key = config.GOOGLE_API_KEY
            if not api_key:
                return TE.API_KEY_NOT_SET
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model=config.GEMINI_MODEL_2_5,
                contents=[types.Content(
                    parts=[
                        types.Part(file_data=types.FileData(file_uri=youtube_url)),
                        types.Part(text=question)
                    ]
                )],
                config=types.GenerateContentConfig(
                    temperature=config.GEMINI_TEMPERATURE,
                    max_output_tokens=config.GEMINI_MAX_TOKENS,
                )
            )
            return response.text
        except Exception as e:
            return S.ANALYZE_YOUTUBE_ERROR.format(url=youtube_url, error=str(e)[:config.QUESTION_PREVIEW_LENGTH])

@tool
@track_tool_call("get_webpage_content")
@log_tool_call(S.WEBPAGE_CONTENT_CALLED)
def get_webpage_content(page_url: str) -> str:
    """Load a web page and return it as markdown if possible

    Args:
        page_url (str): the URL of web page to get

    Returns:
        str: The content of the page(s).
   """

    try:
        r = requests.get(page_url, timeout=30)  # Add 30s timeout
        r.raise_for_status()
        text = ""
        # special case if page is a PDF file
        if r.headers.get('Content-Type', '') == 'application/pdf':
            pdf_file = BytesIO(r.content)
            reader = PdfReader(pdf_file)
            for page in reader.pages:
                text += page.extract_text()
        else:
            soup = BeautifulSoup((r.text), 'html.parser')
            if soup.body:
                # convert to markdown
                text = md(str(soup.body))
            else:
                # return the raw content
                text = r.text
        return text
    except Exception as e:
        return TE.WEBPAGE_FETCH.format(error=e)

@tool
@track_tool_call("read_file")
@log_tool_call(S.READ_FILE_CALLED)
def read_file(file_name: str) -> str:
    """
    Read a file from the files directory and return its content.
    Supports Excel spreadsheets (.xlsx) returned as a Markdown table,
    and Python scripts (.py) returned as raw source code.

    Args:
        file_name (str): The name of the file (e.g., 'data.xlsx', 'script.py'). Do not include the 'files/' prefix.

    Returns:
        str: The file content as text.
    """
    ext = os.path.splitext(file_name)[1].lower()

    if ext == '.xlsx':
        try:
            success, data = _get_file_content(file_name, mode='binary')
            if not success:
                return TE.EXCEL_READ.format(data=data)
            df = pd.read_excel(BytesIO(data))
            return df.to_markdown(index=False)
        except Exception as e:
            return TE.EXCEL_READ_REASON.format(error=e)

    elif ext == '.py':
        try:
            success, data = _get_file_content(file_name, mode='text')
            if not success:
                return TE.PYTHON_READ.format(data=data)
            return data
        except Exception as e:
            return TE.PYTHON_READ_REASON.format(error=e)

    return f"Unsupported file type: {ext}. Supported: .xlsx (Excel), .py (Python script)"

@tool
@track_tool_call("parse_audio_file")
@log_tool_call(S.PARSE_AUDIO_CALLED)
def parse_audio_file(file_name: str) -> str:
    """
    Transcribes audio from an MP3 file into text.
    Use this tool to extract speech/text from audio files.

    Args:
        file_name (str): The name of the MP3 file (e.g., 'audio.mp3'). Do not include the 'files/' prefix.

    Returns:
        str: The transcribed text.
    """

    try:
        # Get file content using helper function
        success, data = _get_file_content(file_name, mode='binary')
        if not success:
            return TE.AUDIO_READ.format(data=data)

        # Load audio from bytes
        audio = AudioSegment.from_file(io.BytesIO(data), format="mp3")
        # SpeechRecognition works best with WAV data so we to WAV format in memory
        wav_data = io.BytesIO()
        audio.export(wav_data, format="wav")
        wav_data.seek(0)  # Rewind the buffer to the beginning

        # Now we directly process the WAV data
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_data) as source:
            audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)
        return text

    except sr.RequestError as e:
        return TE.AUDIO_API.format(error=e)
    except Exception as e:
        if "ffmpeg" in str(e).lower() or "avlib" in str(e).lower():
            return TE.AUDIO_FFMPEG.format(error=e)
        return TE.AUDIO_PARSE.format(error=e)

@tool
@track_tool_call("analyze_image")
@log_tool_call(S.ANALYZE_IMAGE_CALLED, detail_param=1)
def analyze_image(question: str, file_name: str) -> str:
    """
    Analyzes an image file and answers a specific question about it using AI vision.
    Use this tool when you need to understand image content (e.g., chess positions, diagrams, photos).

    Args:
        question (str): The question you want answered about the image.
        file_name (str): The name of the image file (e.g., 'image.png'). Do not include the 'files/' prefix.

    Returns:
        str: The answer to the question based on the image analysis.
    """

    try:
        api_key = config.GOOGLE_API_KEY
        if not api_key:
            return TE.API_KEY_NOT_SET

        # Get file content using helper function
        success, image_data = _get_file_content(file_name, mode='binary')
        if not success:
            return TE.IMAGE_READ.format(image_data=image_data)

        client = genai.Client(api_key=api_key)

        # Use Gemini vision model with image data
        response = client.models.generate_content(
            model=config.GEMINI_MODEL_2_5,
            contents=[types.Content(
                parts=[
                    types.Part(inline_data=types.Blob(
                        mime_type=_get_mime_type(file_name),
                        data=image_data
                    )),
                    types.Part(text=question)
                ]
            )],
            config=types.GenerateContentConfig(
                temperature=config.GEMINI_TEMPERATURE,
                max_output_tokens=config.GEMINI_MAX_TOKENS,
            )
        )
        return response.text

    except Exception as e:
        error_msg = S.ANALYZE_IMAGE_ERROR.format(file_name=file_name, error=str(e)[:config.QUESTION_PREVIEW_LENGTH])
        return error_msg

# ============================================================================
# Tools List
# ============================================================================


def get_custom_tools_list() -> list:
    """Get list of all custom tools for the agent.

    Returns:
        list: List of tool functions
    """
    tools = [
        calculate,
        string_reverse,
        get_current_time_in_timezone,
        websearch,
        wiki_search,
        arvix_search,
        youtube_tool,
        get_webpage_content,
        read_file,
        parse_audio_file,
        analyze_image
    ]
    return tools

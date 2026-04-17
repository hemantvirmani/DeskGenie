"""
Desktop AI Agent - Tools
Desktop Tools Module

Copyright (c) 2026 Hemant Virmani. All rights reserved.

Licensed under the MIT License. See LICENSE file in the project root.

⚠️  IMPORTANT SAFETY WARNING ⚠️
This module performs file system operations that can MODIFY or DELETE files.
- ALWAYS BACKUP IMPORTANT FILES BEFORE USING THESE TOOLS
- Review tool parameters carefully before execution
- Test on non-critical files first
- The authors are NOT responsible for any data loss or damages

This is a hobbyist open-source project for educational purposes.
"""

from typing import Optional
from langchain_core.tools import tool
from utils.langfuse_tracking import track_tool_call
from utils.log_streamer import get_global_logger, log_tool_call
from utils.data_dir import (
    get_home_dir, get_documents_dir, get_downloads_dir, get_desktop_dir,
    get_pictures_dir, get_videos_dir, get_music_dir, get_local_appdata_dir,
    get_roaming_appdata_dir, get_temp_dir, get_all_user_dirs, get_all_system_dirs,
    resolve_path_alias
)
from resources.ui_strings import DesktopToolStrings as DTS
import tools.core.files as _core


# ============================================================================
# PDF Tools
# ============================================================================

@tool
@track_tool_call("pdf_extract_pages")
@log_tool_call(DTS.PDF_EXTRACT_PAGES)
def pdf_extract_pages(input_pdf: str, output_pdf: str, page_range: str) -> str:
    """Extract specific pages from a PDF file and save to a new PDF.

    Args:
        input_pdf: Path to the source PDF file
        output_pdf: Path for the output PDF file
        page_range: Page range to extract (e.g., "1-3", "1,3,5", "last2" for last 2 pages, "first3" for first 3 pages)

    Returns:
        str: Success message or error description
    """
    return _core.pdf_extract_pages(input_pdf, output_pdf, page_range)


@tool
@track_tool_call("pdf_delete_pages")
@log_tool_call(DTS.PDF_DELETE_PAGES)
def pdf_delete_pages(input_pdf: str, output_pdf: str, page_range: str) -> str:
    """Delete specific pages from a PDF file and save the result.

    Args:
        input_pdf: Path to the source PDF file
        output_pdf: Path for the output PDF file
        page_range: Page range to delete (e.g., "1-3", "1,3,5", "last2" for last 2 pages)

    Returns:
        str: Success message or error description
    """
    return _core.pdf_delete_pages(input_pdf, output_pdf, page_range)


@tool
@track_tool_call("pdf_merge")
@log_tool_call(DTS.PDF_MERGE, detail_param=1)
def pdf_merge(pdf_files: str, output_pdf: str) -> str:
    """Merge multiple PDF files into a single PDF.

    Args:
        pdf_files: Comma-separated list of PDF file paths to merge (in order)
        output_pdf: Path for the merged output PDF file

    Returns:
        str: Success message or error description
    """
    return _core.pdf_merge(pdf_files, output_pdf)


@tool
@track_tool_call("pdf_split")
@log_tool_call(DTS.PDF_SPLIT)
def pdf_split(input_pdf: str, output_dir: str, pages_per_split: int = 1) -> str:
    """Split a PDF into multiple smaller PDFs.

    Args:
        input_pdf: Path to the source PDF file
        output_dir: Directory to save split PDF files
        pages_per_split: Number of pages per split file (default: 1 for individual pages)

    Returns:
        str: Success message with list of created files
    """
    return _core.pdf_split(input_pdf, output_dir, pages_per_split)


@tool
@track_tool_call("pdf_to_images")
@log_tool_call(DTS.PDF_TO_IMAGES)
def pdf_to_images(input_pdf: str, output_dir: str, image_format: str = "png", dpi: Optional[int] = None) -> str:
    """Convert PDF pages to images.

    Args:
        input_pdf: Path to the PDF file
        output_dir: Directory to save image files
        image_format: Output format - 'png' or 'jpg' (default: 'png')
        dpi: Resolution in DPI (default: from user config, or 200)

    Returns:
        str: Success message with number of images created
    """
    if dpi is None:
        from utils.user_config import get_preference
        dpi = get_preference("pdf_dpi", 200)
    return _core.pdf_to_images(input_pdf, output_dir, image_format, dpi)


# ============================================================================
# Image Tools
# ============================================================================

@tool
@track_tool_call("process_image")
@log_tool_call(DTS.PROCESS_IMAGE)
def process_image(operation: str, input_image: str, output_image: str,
                  width: Optional[int] = None, height: Optional[int] = None,
                  quality: Optional[int] = None, target_size_kb: int = 500,
                  maintain_aspect: bool = True) -> str:
    """Convert, resize, or compress an image.

    Operations:
    - 'convert': Change image format (determined by output_image extension). Supports HEIC, PNG, JPG, WebP, BMP, GIF, TIFF.
    - 'resize': Change image dimensions. Provide width and/or height in pixels.
    - 'compress': Reduce image file size to target_size_kb (output should be .jpg for best results).

    Args:
        operation: 'convert', 'resize', or 'compress'
        input_image: Path to the source image
        output_image: Path for the output image
        width: Target width in pixels for resize (optional)
        height: Target height in pixels for resize (optional)
        quality: Quality for lossy formats 1-100 (default: from user config, or 85)
        target_size_kb: Target file size in KB for compress (default: 500)
        maintain_aspect: Keep aspect ratio for resize (default: True)

    Returns:
        str: Success message or error description
    """
    if quality is None:
        from utils.user_config import get_preference
        quality = get_preference("image_quality", 85)
    return _core.process_image(operation, input_image, output_image, width, height, quality, target_size_kb, maintain_aspect)


@tool
@track_tool_call("images_to_pdf")
@log_tool_call(DTS.IMAGES_TO_PDF, detail_param=1)
def images_to_pdf(image_files: str, output_pdf: str) -> str:
    """Convert one or more images to a single PDF file.

    Args:
        image_files: Comma-separated list of image paths, or a single image path
        output_pdf: Path for the output PDF file

    Returns:
        str: Success message or error description
    """
    return _core.images_to_pdf(image_files, output_pdf)


@tool
@track_tool_call("batch_convert_images")
@log_tool_call(DTS.BATCH_CONVERT)
def batch_convert_images(input_dir: str, output_dir: str, output_format: str = "jpg", quality: Optional[int] = None) -> str:
    """Convert all images in a directory to a specified format.

    Args:
        input_dir: Directory containing source images
        output_dir: Directory for converted images
        output_format: Target format - 'jpg', 'png', 'webp' (default: 'jpg')
        quality: Quality for lossy formats (1-100, default: from user config, or 85)

    Returns:
        str: Summary of conversion results
    """
    if quality is None:
        from utils.user_config import get_preference
        quality = get_preference("image_quality", 85)
    return _core.batch_convert_images(input_dir, output_dir, output_format, quality)


# ============================================================================
# File Management Tools
# ============================================================================

@tool
@track_tool_call("batch_rename_files")
@log_tool_call(DTS.BATCH_RENAME)
def batch_rename_files(directory: str, pattern: str, replacement: str, preview_only: bool = True) -> str:
    """Batch rename files in a directory using pattern matching.

    Args:
        directory: Directory containing files to rename
        pattern: Pattern to search for in filenames (supports * wildcard)
        replacement: Replacement string (use {n} for sequential numbers, {date} for date)
        preview_only: If True, only shows what would be renamed without making changes (default: True)

    Returns:
        str: List of renames (preview or completed)
    """
    return _core.batch_rename_files(directory, pattern, replacement, preview_only)


@tool
@track_tool_call("organize_files_by_type")
@log_tool_call(DTS.ORGANIZE_FILES)
def organize_files_by_type(source_dir: str, organize_by: str = "extension") -> str:
    """Organize files in a directory into subfolders by type or date.

    Args:
        source_dir: Directory to organize
        organize_by: Organization method - 'extension', 'date', or 'type' (default: 'extension')

    Returns:
        str: Summary of organization results
    """
    return _core.organize_files_by_type(source_dir, organize_by)


@tool
@track_tool_call("find_duplicate_files")
@log_tool_call(DTS.FIND_DUPLICATES)
def find_duplicate_files(directory: str, by_content: bool = False) -> str:
    """Find duplicate files in a directory.

    Args:
        directory: Directory to search for duplicates
        by_content: If True, compare file contents (slower but accurate). If False, compare by size only (default: False)

    Returns:
        str: List of potential duplicates grouped together
    """
    return _core.find_duplicate_files(directory, by_content)


# ============================================================================
# Document Tools
# ============================================================================

@tool
@track_tool_call("word_to_pdf")
@log_tool_call(DTS.WORD_TO_PDF)
def word_to_pdf(input_docx: str, output_pdf: str) -> str:
    """Convert a Word document (.docx) to PDF.

    Args:
        input_docx: Path to the Word document
        output_pdf: Path for the output PDF

    Returns:
        str: Success message or error description
    """
    return _core.word_to_pdf(input_docx, output_pdf)


@tool
@track_tool_call("extract_text_from_pdf")
@log_tool_call(DTS.EXTRACT_TEXT_PDF)
def extract_text_from_pdf(input_pdf: str, output_txt: Optional[str] = None) -> str:
    """Extract all text from a PDF file.

    Args:
        input_pdf: Path to the PDF file
        output_txt: Optional path to save extracted text (if not provided, returns text directly)

    Returns:
        str: Extracted text or success message if saved to file
    """
    return _core.extract_text_from_pdf(input_pdf, output_txt)


@tool
@track_tool_call("ocr_image")
@log_tool_call(DTS.OCR_IMAGE)
def ocr_image(input_image: str, output_txt: Optional[str] = None, language: str = "eng") -> str:
    """Extract text from an image using OCR (Optical Character Recognition).
    Requires Tesseract to be installed on the system.

    Args:
        input_image: Path to the image file
        output_txt: Optional path to save extracted text
        language: OCR language code (default: 'eng' for English)

    Returns:
        str: Extracted text or error if Tesseract not available
    """
    return _core.ocr_image(input_image, output_txt, language)


# ============================================================================
# Media Tools
# ============================================================================

@tool
@track_tool_call("video_to_audio")
@log_tool_call(DTS.VIDEO_TO_AUDIO)
def video_to_audio(input_video: str, output_audio: str, audio_format: str = "mp3") -> str:
    """Extract audio from a video file.

    Args:
        input_video: Path to the video file
        output_audio: Path for the output audio file
        audio_format: Output format - 'mp3', 'wav', 'aac' (default: 'mp3')

    Returns:
        str: Success message or error description
    """
    return _core.video_to_audio(input_video, output_audio, audio_format)


@tool
@track_tool_call("compress_video")
@log_tool_call(DTS.COMPRESS_VIDEO)
def compress_video(input_video: str, output_video: str, target_size_mb: int = 50) -> str:
    """Compress a video to a target file size.

    Args:
        input_video: Path to the source video
        output_video: Path for the compressed video
        target_size_mb: Target file size in megabytes (default: 50MB)

    Returns:
        str: Success message with compression results
    """
    return _core.compress_video(input_video, output_video, target_size_mb)


@tool
@track_tool_call("get_media_info")
@log_tool_call(DTS.GET_MEDIA_INFO)
def get_media_info(file_path: str) -> str:
    """Get detailed information about a media file (video, audio, or image).

    Args:
        file_path: Path to the media file

    Returns:
        str: Formatted media information
    """
    return _core.get_media_info(file_path)


# ============================================================================
# System Directory Tools  (DeskGenie-specific — alias resolution, config reads)
# ============================================================================

@tool
@track_tool_call("get_directory")
@log_tool_call(DTS.GET_DIRECTORY)
def get_directory(name: str = "") -> str:
    """Get the path to a user or system directory, or list all available directories and aliases.

    User directories: home, documents (docs), downloads, desktop, pictures (photos), videos (movies), music
    System directories: appdata, localappdata, roaming, temp (tmp)
    Leave name empty or pass 'all' to list every directory and configured alias.

    Args:
        name: Directory name or alias (e.g., 'downloads', 'appdata'). Empty or 'all' to list everything.

    Returns:
        str: Full path to the directory, or a formatted list of all directories.
    """
    import os
    try:
        dir_map = {
            "home": get_home_dir,
            "documents": get_documents_dir,
            "docs": get_documents_dir,
            "downloads": get_downloads_dir,
            "desktop": get_desktop_dir,
            "pictures": get_pictures_dir,
            "photos": get_pictures_dir,
            "videos": get_videos_dir,
            "movies": get_videos_dir,
            "music": get_music_dir,
            "appdata": get_local_appdata_dir,
            "localappdata": get_local_appdata_dir,
            "local appdata": get_local_appdata_dir,
            "roaming": get_roaming_appdata_dir,
            "roaming appdata": get_roaming_appdata_dir,
            "temp": get_temp_dir,
            "tmp": get_temp_dir,
        }

        key = name.lower().strip()

        if not key or key == "all":
            result = "User Directories:\n"
            for dir_name, path in get_all_user_dirs().items():
                exists = "exists" if path.exists() else "does not exist"
                result += f"  {dir_name.capitalize()}: {path} ({exists})\n"
            result += "\nSystem Directories:\n"
            for dir_name, path in get_all_system_dirs().items():
                if path is None:
                    result += f"  {dir_name}: Not available on this platform\n"
                else:
                    exists = "exists" if path.exists() else "does not exist"
                    result += f"  {dir_name}: {path} ({exists})\n"
            try:
                from utils.user_config import list_folder_aliases as _list_aliases
                aliases = _list_aliases()
                if aliases:
                    result += "\nConfigured Aliases:\n"
                    for alias, path in sorted(aliases.items()):
                        exists = "exists" if os.path.exists(path) else "path not found"
                        result += f"  {alias}: {path} ({exists})\n"
            except Exception:
                pass
            return result

        if key in dir_map:
            return str(dir_map[key]())

        resolved = resolve_path_alias(name)
        if resolved:
            return str(resolved)

        return f"Unknown directory: {name}. Valid: home, documents, downloads, desktop, pictures, videos, music, appdata, localappdata, roaming, temp"

    except Exception as e:
        return f"Error getting directory: {e}"


@tool
@track_tool_call("resolve_path")
@log_tool_call(DTS.RESOLVING_PATH)
def resolve_path(path_or_alias: str) -> str:
    """Resolve a path alias or expand a path with special prefixes.

    Supports:
    - User-defined aliases from config.json (e.g., "prax", "finance")
    - Built-in aliases:
      - ~, home -> Home directory
      - documents, docs -> Documents
      - downloads -> Downloads
      - desktop -> Desktop
      - pictures, photos -> Pictures
      - videos, movies -> Videos
      - music -> Music
      - appdata, localappdata -> Local AppData
      - roaming -> Roaming AppData
      - temp, tmp -> Temp directory

    Args:
        path_or_alias: A path alias or path starting with an alias (e.g., "downloads/myfile.txt")

    Returns:
        str: Resolved full path
    """
    try:
        resolved = resolve_path_alias(path_or_alias)
        if resolved:
            return str(resolved)

        parts = path_or_alias.replace("\\", "/").split("/")
        first_part = parts[0]
        base = resolve_path_alias(first_part)
        if base:
            full_path = base
            for part in parts[1:]:
                if part:
                    full_path = full_path / part
            return str(full_path)

        return path_or_alias

    except Exception as e:
        return f"Error resolving path: {e}"


@tool
@track_tool_call("get_user_preference")
@log_tool_call(DTS.PREFERENCE)
def get_user_preference(key: str) -> str:
    """Get a user preference value.

    Available preferences:
    - default_output_dir: Default directory for output files
    - image_quality: Default image quality (1-100)
    - pdf_dpi: Default DPI for PDF operations

    Args:
        key: The preference key

    Returns:
        str: The preference value or message if not set
    """
    try:
        from utils.user_config import get_preference, get_all_preferences

        if key == "all":
            prefs = get_all_preferences()
            result = "User Preferences:\n"
            for k, v in sorted(prefs.items()):
                result += f"  {k}: {v}\n"
            return result

        value = get_preference(key)
        if value is not None:
            return f"{key}: {value}"
        return f"Preference '{key}' not set"

    except Exception as e:
        return f"Error getting preference: {e}"


@tool
@track_tool_call("list_directory")
@log_tool_call(DTS.LIST_DIRECTORY)
def list_directory(directory: str, recursive: bool = False, pattern: str = "*",
                   show_hidden: bool = False, max_items: int = 50) -> str:
    """List the contents of a directory.

    Args:
        directory: Path to directory or alias (e.g., 'downloads', 'desktop', 'prax')
        recursive: If True, list all files in subdirectories too (default: False)
        pattern: Glob pattern to filter files when recursive=True (default: '*' for all)
        show_hidden: Include hidden files (default: False)
        max_items: Maximum items to show (default: 50)

    Returns:
        str: Formatted directory listing
    """
    resolved = resolve_path_alias(directory)
    resolved_dir = str(resolved) if resolved else directory
    return _core.list_directory(resolved_dir, recursive, pattern, show_hidden, max_items)


# ============================================================================
# Desktop Tools List
# ============================================================================

def get_desktop_tools_list() -> list:
    """Get list of all desktop utility tools.

    Returns:
        list: List of tool functions
    """
    # NOTE: PDF, image, file management, document and media tools (17 tools) are
    # served via the deskgenie-files MCP server (mcp_servers/file_ops_server.py)
    # and loaded at runtime by tools/mcp_tools.py. They are no longer registered
    # here to avoid duplicate tool definitions when the MCP server is active.
    return [
        # System Directory Tools
        get_directory,
        resolve_path,
        list_directory,

        # User Config Tools (read-only)
        get_user_preference,
    ]

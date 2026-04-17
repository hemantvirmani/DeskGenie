"""DeskGenie file-ops MCP server.

Exposes all file, PDF, image, document and media tools from tools/core/files.py
as MCP tools consumable by any MCP-compatible client (DeskGenie, Claude Desktop,
Continue.dev, etc.).

Usage (stdio transport — default for MCP):
    python mcp_servers/file_ops_server.py

Config entry (config.json mcpServers section):
    "deskgenie-files": {
        "command": "python",
        "args": ["mcp_servers/file_ops_server.py"]
    }
"""

import os
import sys
from typing import Optional

# Ensure the project root is importable so tools.core.files resolves correctly
# when the server is launched from any working directory.
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from fastmcp import FastMCP
import tools.core.files as _core

mcp = FastMCP("deskgenie-files")


# ============================================================================
# PDF Tools
# ============================================================================

@mcp.tool()
def pdf_extract_pages(input_pdf: str, output_pdf: str, page_range: str) -> str:
    """Extract specific pages from a PDF file and save to a new PDF.

    Args:
        input_pdf: Path to the source PDF file
        output_pdf: Path for the output PDF file
        page_range: Page range to extract (e.g., "1-3", "1,3,5", "last2", "first3")
    """
    return _core.pdf_extract_pages(input_pdf, output_pdf, page_range)


@mcp.tool()
def pdf_delete_pages(input_pdf: str, output_pdf: str, page_range: str) -> str:
    """Delete specific pages from a PDF file and save the result.

    Args:
        input_pdf: Path to the source PDF file
        output_pdf: Path for the output PDF file
        page_range: Page range to delete (e.g., "1-3", "1,3,5", "last2")
    """
    return _core.pdf_delete_pages(input_pdf, output_pdf, page_range)


@mcp.tool()
def pdf_merge(pdf_files: str, output_pdf: str) -> str:
    """Merge multiple PDF files into a single PDF.

    Args:
        pdf_files: Comma-separated list of PDF file paths to merge (in order)
        output_pdf: Path for the merged output PDF file
    """
    return _core.pdf_merge(pdf_files, output_pdf)


@mcp.tool()
def pdf_split(input_pdf: str, output_dir: str, pages_per_split: int = 1) -> str:
    """Split a PDF into multiple smaller PDFs.

    Args:
        input_pdf: Path to the source PDF file
        output_dir: Directory to save split PDF files
        pages_per_split: Number of pages per split file (default: 1)
    """
    return _core.pdf_split(input_pdf, output_dir, pages_per_split)


@mcp.tool()
def pdf_to_images(input_pdf: str, output_dir: str, image_format: str = "png", dpi: int = 200) -> str:
    """Convert PDF pages to images.

    Args:
        input_pdf: Path to the PDF file
        output_dir: Directory to save image files
        image_format: Output format - 'png' or 'jpg' (default: 'png')
        dpi: Resolution in DPI (default: 200)
    """
    return _core.pdf_to_images(input_pdf, output_dir, image_format, dpi)


# ============================================================================
# Image Tools
# ============================================================================

@mcp.tool()
def process_image(
    operation: str,
    input_image: str,
    output_image: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    quality: int = 85,
    target_size_kb: int = 500,
    maintain_aspect: bool = True,
) -> str:
    """Convert, resize, or compress an image.

    Operations:
    - 'convert': Change image format. Supports HEIC, PNG, JPG, WebP, BMP, GIF, TIFF.
    - 'resize': Change image dimensions. Provide width and/or height in pixels.
    - 'compress': Reduce image file size to target_size_kb.

    Args:
        operation: 'convert', 'resize', or 'compress'
        input_image: Path to the source image
        output_image: Path for the output image
        width: Target width in pixels for resize (optional)
        height: Target height in pixels for resize (optional)
        quality: Quality for lossy formats 1-100 (default: 85)
        target_size_kb: Target file size in KB for compress (default: 500)
        maintain_aspect: Keep aspect ratio for resize (default: True)
    """
    return _core.process_image(
        operation, input_image, output_image,
        width=width, height=height, quality=quality,
        target_size_kb=target_size_kb, maintain_aspect=maintain_aspect,
    )


@mcp.tool()
def images_to_pdf(image_files: str, output_pdf: str) -> str:
    """Convert one or more images to a single PDF file.

    Args:
        image_files: Comma-separated list of image paths, or a single image path
        output_pdf: Path for the output PDF file
    """
    return _core.images_to_pdf(image_files, output_pdf)


@mcp.tool()
def batch_convert_images(
    input_dir: str,
    output_dir: str,
    output_format: str = "jpg",
    quality: int = 85,
) -> str:
    """Convert all images in a directory to a specified format.

    Args:
        input_dir: Directory containing source images
        output_dir: Directory for converted images
        output_format: Target format - 'jpg', 'png', 'webp' (default: 'jpg')
        quality: Quality for lossy formats (1-100, default: 85)
    """
    return _core.batch_convert_images(input_dir, output_dir, output_format, quality)


# ============================================================================
# File Management Tools
# ============================================================================

@mcp.tool()
def batch_rename_files(
    directory: str,
    pattern: str,
    replacement: str,
    preview_only: bool = True,
) -> str:
    """Batch rename files in a directory using pattern matching.

    Args:
        directory: Directory containing files to rename
        pattern: Pattern to search for in filenames (supports * wildcard)
        replacement: Replacement string (use {n} for sequential numbers, {date} for date)
        preview_only: If True, only shows what would be renamed without making changes (default: True)
    """
    return _core.batch_rename_files(directory, pattern, replacement, preview_only)


@mcp.tool()
def organize_files_by_type(source_dir: str, organize_by: str = "extension") -> str:
    """Organize files in a directory into subfolders by type or date.

    Args:
        source_dir: Directory to organize
        organize_by: Organization method - 'extension', 'date', or 'type' (default: 'extension')
    """
    return _core.organize_files_by_type(source_dir, organize_by)


@mcp.tool()
def find_duplicate_files(directory: str, by_content: bool = False) -> str:
    """Find duplicate files in a directory.

    Args:
        directory: Directory to search for duplicates
        by_content: If True, compare file contents (slower but accurate). If False, compare by size only (default: False)
    """
    return _core.find_duplicate_files(directory, by_content)


# ============================================================================
# Document Tools
# ============================================================================

@mcp.tool()
def word_to_pdf(input_docx: str, output_pdf: str) -> str:
    """Convert a Word document (.docx) to PDF.

    Args:
        input_docx: Path to the Word document
        output_pdf: Path for the output PDF
    """
    return _core.word_to_pdf(input_docx, output_pdf)


@mcp.tool()
def extract_text_from_pdf(input_pdf: str, output_txt: Optional[str] = None) -> str:
    """Extract all text from a PDF file.

    Args:
        input_pdf: Path to the PDF file
        output_txt: Optional path to save extracted text (if not provided, returns text directly)
    """
    return _core.extract_text_from_pdf(input_pdf, output_txt)


@mcp.tool()
def ocr_image(input_image: str, output_txt: Optional[str] = None, language: str = "eng") -> str:
    """Extract text from an image using OCR (requires Tesseract installed).

    Args:
        input_image: Path to the image file
        output_txt: Optional path to save extracted text
        language: OCR language code (default: 'eng' for English)
    """
    return _core.ocr_image(input_image, output_txt, language)


# ============================================================================
# Media Tools
# ============================================================================

@mcp.tool()
def video_to_audio(input_video: str, output_audio: str, audio_format: str = "mp3") -> str:
    """Extract audio from a video file.

    Args:
        input_video: Path to the video file
        output_audio: Path for the output audio file
        audio_format: Output format - 'mp3', 'wav', 'aac' (default: 'mp3')
    """
    return _core.video_to_audio(input_video, output_audio, audio_format)


@mcp.tool()
def compress_video(input_video: str, output_video: str, target_size_mb: int = 50) -> str:
    """Compress a video to a target file size.

    Args:
        input_video: Path to the source video
        output_video: Path for the compressed video
        target_size_mb: Target file size in megabytes (default: 50MB)
    """
    return _core.compress_video(input_video, output_video, target_size_mb)


@mcp.tool()
def get_media_info(file_path: str) -> str:
    """Get detailed information about a media file (video, audio, or image).

    Args:
        file_path: Path to the media file
    """
    return _core.get_media_info(file_path)


# ============================================================================
# Directory Tools
# ============================================================================

@mcp.tool()
def list_directory(
    directory: str,
    recursive: bool = False,
    pattern: str = "*",
    show_hidden: bool = False,
    max_items: int = 50,
) -> str:
    """List the contents of a directory.

    Args:
        directory: Absolute path to directory
        recursive: If True, list all files in subdirectories too (default: False)
        pattern: Glob pattern to filter files when recursive=True (default: '*')
        show_hidden: Include hidden files (default: False)
        max_items: Maximum items to show (default: 50)
    """
    return _core.list_directory(directory, recursive, pattern, show_hidden, max_items)


if __name__ == "__main__":
    mcp.run()

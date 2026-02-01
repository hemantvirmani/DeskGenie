"""
DeskGenie - Desktop AI Agent
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

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional
from langchain_core.tools import tool
from utils.langfuse_tracking import track_tool_call
from utils.log_streamer import get_global_logger
from utils.data_dir import (
    get_home_dir, get_documents_dir, get_downloads_dir, get_desktop_dir,
    get_pictures_dir, get_videos_dir, get_music_dir, get_local_appdata_dir,
    get_roaming_appdata_dir, get_temp_dir, get_all_user_dirs, get_all_system_dirs,
    resolve_path_alias
)
from resources.state_strings import DesktopToolReturns as DTR
from resources.error_strings import DesktopToolErrors as DTE
from resources.ui_strings import DesktopToolStrings as DTS

# PDF handling
import fitz  # PyMuPDF
from pypdf import PdfReader, PdfWriter

# Image handling
from PIL import Image
import pillow_heif  # For HEIC support

# Document handling
from docx import Document as DocxDocument
from docx2pdf import convert as docx_to_pdf_convert

# OCR
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

# Video/Audio handling
try:
    # moviepy 2.0+ uses moviepy directly
    from moviepy import VideoFileClip, AudioFileClip
except ImportError:
    # moviepy 1.x uses moviepy.editor
    from moviepy.editor import VideoFileClip, AudioFileClip

# ============================================================================
# PDF Tools
# ============================================================================

@tool
@track_tool_call("pdf_extract_pages")
def pdf_extract_pages(input_pdf: str, output_pdf: str, page_range: str) -> str:
    """
    Extract specific pages from a PDF file and save to a new PDF.

    Args:
        input_pdf: Path to the source PDF file
        output_pdf: Path for the output PDF file
        page_range: Page range to extract (e.g., "1-3", "1,3,5", "last2" for last 2 pages, "first3" for first 3 pages)

    Returns:
        str: Success message or error description
    """
    try:
        get_global_logger().tool(DTS.PDF_EXTRACT_PAGES.format(input_pdf=input_pdf, output_pdf=output_pdf, page_range=page_range))

        reader = PdfReader(input_pdf)
        writer = PdfWriter()
        total_pages = len(reader.pages)

        # Parse page range
        pages_to_extract = _parse_page_range(page_range, total_pages)

        if not pages_to_extract:
            return DTE.PDF_INVALID_PAGE_RANGE.format(page_range=page_range, total_pages=total_pages)

        for page_num in pages_to_extract:
            writer.add_page(reader.pages[page_num])

        with open(output_pdf, "wb") as f:
            writer.write(f)

        return DTR.PDF_EXTRACT_SUCCESS.format(page_range=page_range, input_pdf=input_pdf, output_pdf=output_pdf, pages_count=len(pages_to_extract))

    except Exception as e:
        return DTE.PDF_EXTRACT.format(error=e)


@tool
@track_tool_call("pdf_delete_pages")
def pdf_delete_pages(input_pdf: str, output_pdf: str, page_range: str) -> str:
    """
    Delete specific pages from a PDF file and save the result.

    Args:
        input_pdf: Path to the source PDF file
        output_pdf: Path for the output PDF file
        page_range: Page range to delete (e.g., "1-3", "1,3,5", "last2" for last 2 pages)

    Returns:
        str: Success message or error description
    """
    try:
        get_global_logger().tool(DTS.PDF_DELETE_PAGES.format(input_pdf=input_pdf, output_pdf=output_pdf, page_range=page_range))

        reader = PdfReader(input_pdf)
        writer = PdfWriter()
        total_pages = len(reader.pages)

        # Parse pages to delete
        pages_to_delete = set(_parse_page_range(page_range, total_pages))

        if not pages_to_delete:
            return DTE.PDF_INVALID_PAGE_RANGE.format(page_range=page_range, total_pages=total_pages)

        pages_kept = 0
        for i in range(total_pages):
            if i not in pages_to_delete:
                writer.add_page(reader.pages[i])
                pages_kept += 1

        if pages_kept == 0:
            return DTE.PDF_DELETE_ALL

        with open(output_pdf, "wb") as f:
            writer.write(f)

        return DTR.PDF_DELETE_SUCCESS.format(page_range=page_range, input_pdf=input_pdf, output_pdf=output_pdf, pages_kept=pages_kept)

    except Exception as e:
        return DTE.PDF_DELETE.format(error=e)


@tool
@track_tool_call("pdf_merge")
def pdf_merge(pdf_files: str, output_pdf: str) -> str:
    """
    Merge multiple PDF files into a single PDF.

    Args:
        pdf_files: Comma-separated list of PDF file paths to merge (in order)
        output_pdf: Path for the merged output PDF file

    Returns:
        str: Success message or error description
    """
    try:
        get_global_logger().tool(DTS.PDF_MERGE.format(pdf_files=pdf_files, output_pdf=output_pdf))
        file_list = [f.strip() for f in pdf_files.split(",")]
        writer = PdfWriter()
        total_pages = 0

        for pdf_path in file_list:
            if not os.path.exists(pdf_path):
                return DTE.PDF_FILE_NOT_FOUND.format(pdf_path=pdf_path)

            reader = PdfReader(pdf_path)
            for page in reader.pages:
                writer.add_page(page)
                total_pages += 1

        with open(output_pdf, "wb") as f:
            writer.write(f)

        return DTR.PDF_MERGE_SUCCESS.format(count=len(file_list), output_pdf=output_pdf, total_pages=total_pages)

    except Exception as e:
        return DTE.PDF_MERGE.format(error=e)


@tool
@track_tool_call("pdf_split")
def pdf_split(input_pdf: str, output_dir: str, pages_per_split: int = 1) -> str:
    """
    Split a PDF into multiple smaller PDFs.

    Args:
        input_pdf: Path to the source PDF file
        output_dir: Directory to save split PDF files
        pages_per_split: Number of pages per split file (default: 1 for individual pages)

    Returns:
        str: Success message with list of created files
    """
    try:
        get_global_logger().tool(DTS.PDF_SPLIT.format(input_pdf=input_pdf, output_dir=output_dir, pages_per_split=pages_per_split))

        os.makedirs(output_dir, exist_ok=True)
        reader = PdfReader(input_pdf)
        total_pages = len(reader.pages)

        base_name = Path(input_pdf).stem
        created_files = []

        for i in range(0, total_pages, pages_per_split):
            writer = PdfWriter()
            end_page = min(i + pages_per_split, total_pages)

            for j in range(i, end_page):
                writer.add_page(reader.pages[j])

            output_path = os.path.join(output_dir, f"{base_name}_part{i//pages_per_split + 1}.pdf")
            with open(output_path, "wb") as f:
                writer.write(f)
            created_files.append(output_path)

        return DTR.PDF_SPLIT_SUCCESS.format(input_pdf=input_pdf, count=len(created_files), output_dir=output_dir)

    except Exception as e:
        return DTE.PDF_SPLIT.format(error=e)


@tool
@track_tool_call("pdf_to_images")
def pdf_to_images(input_pdf: str, output_dir: str, image_format: str = "png", dpi: int = 150) -> str:
    """
    Convert PDF pages to images.

    Args:
        input_pdf: Path to the PDF file
        output_dir: Directory to save image files
        image_format: Output format - 'png' or 'jpg' (default: 'png')
        dpi: Resolution in DPI (default: 150)

    Returns:
        str: Success message with number of images created
    """
    try:
        get_global_logger().tool(DTS.PDF_TO_IMAGES.format(input_pdf=input_pdf, output_dir=output_dir))

        os.makedirs(output_dir, exist_ok=True)
        doc = fitz.open(input_pdf)
        base_name = Path(input_pdf).stem

        created_files = []
        zoom = dpi / 72  # 72 is the default DPI for PDF
        matrix = fitz.Matrix(zoom, zoom)

        for i, page in enumerate(doc):
            pix = page.get_pixmap(matrix=matrix)
            output_path = os.path.join(output_dir, f"{base_name}_page{i+1}.{image_format}")
            pix.save(output_path)
            created_files.append(output_path)

        doc.close()
        return DTR.PDF_TO_IMAGES_SUCCESS.format(count=len(created_files), format=image_format.upper(), output_dir=output_dir)

    except Exception as e:
        return DTE.PDF_TO_IMAGES.format(error=e)


# ============================================================================
# Image Tools
# ============================================================================

@tool
@track_tool_call("image_convert")
def image_convert(input_image: str, output_image: str, quality: int = 85) -> str:
    """
    Convert image between formats (supports HEIC, PNG, JPG, WebP, BMP, GIF, TIFF).

    Args:
        input_image: Path to the source image file
        output_image: Path for the output image (format determined by extension)
        quality: Quality for lossy formats like JPG (1-100, default: 85)

    Returns:
        str: Success message or error description
    """
    try:
        get_global_logger().tool(DTS.IMAGE_CONVERT.format(input_image=input_image, output_image=output_image))

        input_ext = Path(input_image).suffix.lower()
        output_ext = Path(output_image).suffix.lower()

        # Handle HEIC input
        if input_ext in ['.heic', '.heif']:
            pillow_heif.register_heif_opener()

        img = Image.open(input_image)

        # Convert RGBA to RGB for formats that don't support alpha
        if output_ext in ['.jpg', '.jpeg'] and img.mode in ['RGBA', 'P']:
            img = img.convert('RGB')

        # Save with appropriate options
        save_kwargs = {}
        if output_ext in ['.jpg', '.jpeg']:
            save_kwargs['quality'] = quality
            save_kwargs['optimize'] = True
        elif output_ext == '.png':
            save_kwargs['optimize'] = True
        elif output_ext == '.webp':
            save_kwargs['quality'] = quality

        img.save(output_image, **save_kwargs)

        # Get file sizes for comparison
        input_size = os.path.getsize(input_image) / 1024  # KB
        output_size = os.path.getsize(output_image) / 1024  # KB

        return DTR.IMAGE_CONVERT_SUCCESS.format(input_image=input_image, input_size=input_size, output_image=output_image, output_size=output_size)

    except Exception as e:
        return DTE.IMAGE_CONVERT.format(error=e)


@tool
@track_tool_call("image_resize")
def image_resize(input_image: str, output_image: str, width: Optional[int] = None,
                 height: Optional[int] = None, maintain_aspect: bool = True) -> str:
    """
    Resize an image to specified dimensions.

    Args:
        input_image: Path to the source image
        output_image: Path for the resized image
        width: Target width in pixels (optional)
        height: Target height in pixels (optional)
        maintain_aspect: Keep aspect ratio if only one dimension specified (default: True)

    Returns:
        str: Success message with old and new dimensions
    """
    try:
        get_global_logger().tool(DTS.IMAGE_RESIZE.format(input_image=input_image, output_image=output_image))

        input_ext = Path(input_image).suffix.lower()
        if input_ext in ['.heic', '.heif']:
            pillow_heif.register_heif_opener()

        img = Image.open(input_image)
        original_size = img.size

        if width is None and height is None:
            return DTE.IMAGE_RESIZE_NO_DIMENSIONS

        if maintain_aspect:
            if width and height:
                # Fit within box while maintaining aspect ratio
                img.thumbnail((width, height), Image.Resampling.LANCZOS)
            elif width:
                ratio = width / img.width
                height = int(img.height * ratio)
                img = img.resize((width, height), Image.Resampling.LANCZOS)
            else:
                ratio = height / img.height
                width = int(img.width * ratio)
                img = img.resize((width, height), Image.Resampling.LANCZOS)
        else:
            new_width = width or img.width
            new_height = height or img.height
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        img.save(output_image)

        return DTR.IMAGE_RESIZE_SUCCESS.format(input_image=input_image, original_size=original_size, new_size=img.size)

    except Exception as e:
        return DTE.IMAGE_RESIZE.format(error=e)


@tool
@track_tool_call("image_compress")
def image_compress(input_image: str, output_image: str, target_size_kb: int = 500) -> str:
    """
    Compress an image to target file size while maintaining quality.

    Args:
        input_image: Path to the source image
        output_image: Path for the compressed image (should be .jpg for best compression)
        target_size_kb: Target file size in kilobytes (default: 500KB)

    Returns:
        str: Success message with compression results
    """
    try:
        get_global_logger().tool(DTS.IMAGE_COMPRESS.format(input_image=input_image, output_image=output_image, target_size_kb=target_size_kb))

        input_ext = Path(input_image).suffix.lower()
        if input_ext in ['.heic', '.heif']:
            pillow_heif.register_heif_opener()

        img = Image.open(input_image)
        original_size = os.path.getsize(input_image) / 1024

        # Convert to RGB if needed
        if img.mode in ['RGBA', 'P']:
            img = img.convert('RGB')

        # Binary search for optimal quality
        min_quality = 10
        max_quality = 95
        best_quality = max_quality

        while min_quality <= max_quality:
            mid_quality = (min_quality + max_quality) // 2

            # Save to temporary buffer
            from io import BytesIO
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=mid_quality, optimize=True)
            size_kb = buffer.tell() / 1024

            if size_kb <= target_size_kb:
                best_quality = mid_quality
                min_quality = mid_quality + 1
            else:
                max_quality = mid_quality - 1

        # Save with best quality found
        img.save(output_image, format='JPEG', quality=best_quality, optimize=True)
        final_size = os.path.getsize(output_image) / 1024

        return DTR.IMAGE_COMPRESS_SUCCESS.format(input_image=input_image, original_size=original_size, output_image=output_image, final_size=final_size, quality=best_quality)

    except Exception as e:
        return DTE.IMAGE_COMPRESS.format(error=e)


@tool
@track_tool_call("images_to_pdf")
def images_to_pdf(image_files: str, output_pdf: str) -> str:
    """
    Convert one or more images to a single PDF file.

    Args:
        image_files: Comma-separated list of image paths, or a single image path
        output_pdf: Path for the output PDF file

    Returns:
        str: Success message or error description
    """
    try:
        get_global_logger().tool(f"Converting images to PDF: {output_pdf}")

        file_list = [f.strip() for f in image_files.split(",")]
        pillow_heif.register_heif_opener()

        images = []
        for img_path in file_list:
            if not os.path.exists(img_path):
                return f"Image file not found: {img_path}"

            img = Image.open(img_path)
            # Convert to RGB if needed (PDF doesn't support RGBA)
            if img.mode in ['RGBA', 'P']:
                img = img.convert('RGB')
            images.append(img)

        if not images:
            return "No valid images to convert"

        # Save first image and append the rest
        first_img = images[0]
        if len(images) > 1:
            first_img.save(output_pdf, "PDF", save_all=True, append_images=images[1:])
        else:
            first_img.save(output_pdf, "PDF")

        return f"Successfully created PDF with {len(images)} image(s): {output_pdf}"

    except Exception as e:
        return f"Error converting images to PDF: {e}"


@tool
@track_tool_call("batch_convert_images")
def batch_convert_images(input_dir: str, output_dir: str, output_format: str = "jpg", quality: int = 85) -> str:
    """
    Convert all images in a directory to a specified format.

    Args:
        input_dir: Directory containing source images
        output_dir: Directory for converted images
        output_format: Target format - 'jpg', 'png', 'webp' (default: 'jpg')
        quality: Quality for lossy formats (1-100, default: 85)

    Returns:
        str: Summary of conversion results
    """
    try:
        get_global_logger().tool(DTS.BATCH_CONVERT.format(input_dir=input_dir, output_dir=output_dir))

        os.makedirs(output_dir, exist_ok=True)
        pillow_heif.register_heif_opener()

        supported_formats = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff', '.heic', '.heif'}
        converted = 0
        failed = 0

        for filename in os.listdir(input_dir):
            input_path = os.path.join(input_dir, filename)
            if not os.path.isfile(input_path):
                continue

            ext = Path(filename).suffix.lower()
            if ext not in supported_formats:
                continue

            try:
                output_filename = Path(filename).stem + f".{output_format}"
                output_path = os.path.join(output_dir, output_filename)

                img = Image.open(input_path)
                if output_format in ['jpg', 'jpeg'] and img.mode in ['RGBA', 'P']:
                    img = img.convert('RGB')

                save_kwargs = {'quality': quality} if output_format in ['jpg', 'jpeg', 'webp'] else {}
                img.save(output_path, **save_kwargs)
                converted += 1
            except Exception:
                failed += 1

        return DTR.BATCH_CONVERT_SUCCESS.format(converted=converted, failed=failed)

    except Exception as e:
        return DTE.BATCH_CONVERT.format(error=e)


# ============================================================================
# File Management Tools
# ============================================================================

@tool
@track_tool_call("batch_rename_files")
def batch_rename_files(directory: str, pattern: str, replacement: str, preview_only: bool = True) -> str:
    """
    Batch rename files in a directory using pattern matching.

    Args:
        directory: Directory containing files to rename
        pattern: Pattern to search for in filenames (supports * wildcard)
        replacement: Replacement string (use {n} for sequential numbers, {date} for date)
        preview_only: If True, only shows what would be renamed without making changes (default: True)

    Returns:
        str: List of renames (preview or completed)
    """
    try:
        get_global_logger().tool(DTS.BATCH_RENAME.format(directory=directory, pattern=pattern, replacement=replacement))

        import fnmatch
        import re

        files = os.listdir(directory)
        renames = []
        counter = 1
        today = datetime.now().strftime("%Y%m%d")

        for filename in sorted(files):
            if fnmatch.fnmatch(filename, f"*{pattern}*") or pattern in filename:
                # Build new filename
                new_name = replacement
                new_name = new_name.replace("{n}", str(counter).zfill(3))
                new_name = new_name.replace("{date}", today)

                # Preserve extension if not in replacement
                ext = Path(filename).suffix
                if '.' not in new_name:
                    new_name += ext

                old_path = os.path.join(directory, filename)
                new_path = os.path.join(directory, new_name)

                if not preview_only:
                    os.rename(old_path, new_path)

                renames.append(f"{filename} -> {new_name}")
                counter += 1

        if not renames:
            return DTE.BATCH_RENAME_NO_MATCH.format(pattern=pattern)

        action = "Would rename" if preview_only else "Renamed"
        result = f"{action} {len(renames)} files:\n" + "\n".join(renames[:20])
        if len(renames) > 20:
            result += f"\n... and {len(renames) - 20} more"

        return result

    except Exception as e:
        return DTE.BATCH_RENAME.format(error=e)


@tool
@track_tool_call("organize_files_by_type")
def organize_files_by_type(source_dir: str, organize_by: str = "extension") -> str:
    """
    Organize files in a directory into subfolders by type or date.

    Args:
        source_dir: Directory to organize
        organize_by: Organization method - 'extension', 'date', or 'type' (default: 'extension')

    Returns:
        str: Summary of organization results
    """
    try:
        get_global_logger().tool(DTS.ORGANIZE_FILES.format(source_dir=source_dir, organize_by=organize_by))

        type_mapping = {
            'Images': {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.heic', '.heif', '.tiff', '.svg'},
            'Documents': {'.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx'},
            'Videos': {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'},
            'Audio': {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'},
            'Archives': {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'},
            'Code': {'.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h', '.json', '.xml', '.yaml', '.yml'},
        }

        moved_counts = {}

        for filename in os.listdir(source_dir):
            file_path = os.path.join(source_dir, filename)
            if not os.path.isfile(file_path):
                continue

            ext = Path(filename).suffix.lower()

            if organize_by == "extension":
                folder_name = ext[1:].upper() if ext else "NoExtension"
            elif organize_by == "date":
                mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                folder_name = mtime.strftime("%Y-%m")
            else:  # type
                folder_name = "Other"
                for type_name, extensions in type_mapping.items():
                    if ext in extensions:
                        folder_name = type_name
                        break

            dest_dir = os.path.join(source_dir, folder_name)
            os.makedirs(dest_dir, exist_ok=True)

            dest_path = os.path.join(dest_dir, filename)
            shutil.move(file_path, dest_path)

            moved_counts[folder_name] = moved_counts.get(folder_name, 0) + 1

        summary = "Organization complete:\n"
        for folder, count in sorted(moved_counts.items()):
            summary += f"  {folder}: {count} files\n"

        return summary

    except Exception as e:
        return DTE.FILE_ORGANIZE.format(error=e)


@tool
@track_tool_call("find_duplicate_files")
def find_duplicate_files(directory: str, by_content: bool = False) -> str:
    """
    Find duplicate files in a directory.

    Args:
        directory: Directory to search for duplicates
        by_content: If True, compare file contents (slower but accurate). If False, compare by size only (default: False)

    Returns:
        str: List of potential duplicates grouped together
    """
    try:
        get_global_logger().tool(DTS.FIND_DUPLICATES.format(directory=directory, by_content=by_content))

        import hashlib
        from collections import defaultdict

        # Group files by size first
        size_groups = defaultdict(list)
        for root, _, files in os.walk(directory):
            for filename in files:
                file_path = os.path.join(root, filename)
                try:
                    size = os.path.getsize(file_path)
                    size_groups[size].append(file_path)
                except OSError:
                    continue

        duplicates = []

        for size, files in size_groups.items():
            if len(files) < 2:
                continue

            if by_content:
                # Compare by hash
                hash_groups = defaultdict(list)
                for file_path in files:
                    try:
                        with open(file_path, 'rb') as f:
                            file_hash = hashlib.md5(f.read()).hexdigest()
                        hash_groups[file_hash].append(file_path)
                    except OSError:
                        continue

                for hash_val, hash_files in hash_groups.items():
                    if len(hash_files) > 1:
                        duplicates.append(hash_files)
            else:
                # Just group by size
                duplicates.append(files)

        if not duplicates:
            return DTR.FILE_NO_DUPLICATES

        result = f"Found {len(duplicates)} groups of potential duplicates:\n\n"
        for i, group in enumerate(duplicates[:10], 1):
            size_kb = os.path.getsize(group[0]) / 1024
            result += f"Group {i} ({size_kb:.1f}KB):\n"
            for path in group:
                result += f"  - {path}\n"
            result += "\n"

        if len(duplicates) > 10:
            result += f"... and {len(duplicates) - 10} more groups"

        return result

    except Exception as e:
        return DTE.FILE_DUPLICATES.format(error=e)


# ============================================================================
# Document Tools
# ============================================================================

@tool
@track_tool_call("word_to_pdf")
def word_to_pdf(input_docx: str, output_pdf: str) -> str:
    """
    Convert a Word document (.docx) to PDF.

    Args:
        input_docx: Path to the Word document
        output_pdf: Path for the output PDF

    Returns:
        str: Success message or error description
    """
    try:
        get_global_logger().tool(DTS.WORD_TO_PDF.format(input_docx=input_docx, output_pdf=output_pdf))

        docx_to_pdf_convert(input_docx, output_pdf)

        return DTR.DOCX_TO_PDF_SUCCESS.format(input_docx=input_docx, output_pdf=output_pdf)

    except Exception as e:
        return DTE.DOCX_TO_PDF.format(error=e)


@tool
@track_tool_call("extract_text_from_pdf")
def extract_text_from_pdf(input_pdf: str, output_txt: Optional[str] = None) -> str:
    """
    Extract all text from a PDF file.

    Args:
        input_pdf: Path to the PDF file
        output_txt: Optional path to save extracted text (if not provided, returns text directly)

    Returns:
        str: Extracted text or success message if saved to file
    """
    try:
        get_global_logger().tool(DTS.EXTRACT_TEXT_PDF.format(input_pdf=input_pdf))

        doc = fitz.open(input_pdf)
        text = ""

        for page in doc:
            text += page.get_text() + "\n\n"

        doc.close()

        if output_txt:
            with open(output_txt, 'w', encoding='utf-8') as f:
                f.write(text)
            return DTR.PDF_TEXT_EXTRACT_SUCCESS.format(output_txt=output_txt, char_count=len(text))

        # Return first 5000 chars if no output file specified
        if len(text) > 5000:
            return text[:5000] + f"\n\n... (truncated, {len(text)} total characters)"
        return text

    except Exception as e:
        return DTE.PDF_TEXT_EXTRACT.format(error=e)


@tool
@track_tool_call("ocr_image")
def ocr_image(input_image: str, output_txt: Optional[str] = None, language: str = "eng") -> str:
    """
    Extract text from an image using OCR (Optical Character Recognition).
    Requires Tesseract to be installed on the system.

    Args:
        input_image: Path to the image file
        output_txt: Optional path to save extracted text
        language: OCR language code (default: 'eng' for English)

    Returns:
        str: Extracted text or error if Tesseract not available
    """
    try:
        if not TESSERACT_AVAILABLE:
            return DTE.OCR_NOT_INSTALLED

        get_global_logger().tool(DTS.OCR_IMAGE.format(input_image=input_image))

        input_ext = Path(input_image).suffix.lower()
        if input_ext in ['.heic', '.heif']:
            pillow_heif.register_heif_opener()

        img = Image.open(input_image)
        text = pytesseract.image_to_string(img, lang=language)

        if output_txt:
            with open(output_txt, 'w', encoding='utf-8') as f:
                f.write(text)
            return DTR.OCR_SUCCESS.format(output_txt=output_txt, char_count=len(text))

        return text if text.strip() else "No text detected in image"

    except Exception as e:
        return DTE.OCR_FAILED.format(error=e)


# ============================================================================
# Media Tools
# ============================================================================

@tool
@track_tool_call("video_to_audio")
def video_to_audio(input_video: str, output_audio: str, audio_format: str = "mp3") -> str:
    """
    Extract audio from a video file.

    Args:
        input_video: Path to the video file
        output_audio: Path for the output audio file
        audio_format: Output format - 'mp3', 'wav', 'aac' (default: 'mp3')

    Returns:
        str: Success message or error description
    """
    try:
        get_global_logger().tool(DTS.VIDEO_TO_AUDIO.format(input_video=input_video, output_audio=output_audio))

        video = VideoFileClip(input_video)
        audio = video.audio

        if audio is None:
            video.close()
            return DTE.VIDEO_NO_AUDIO.format(input_video=input_video)

        audio.write_audiofile(output_audio, verbose=False, logger=None)

        duration = video.duration
        video.close()

        return DTR.AUDIO_EXTRACT_SUCCESS.format(input_video=input_video, output_audio=output_audio, duration=duration)

    except Exception as e:
        return DTE.AUDIO_EXTRACT.format(error=e)


@tool
@track_tool_call("compress_video")
def compress_video(input_video: str, output_video: str, target_size_mb: int = 50) -> str:
    """
    Compress a video to a target file size.

    Args:
        input_video: Path to the source video
        output_video: Path for the compressed video
        target_size_mb: Target file size in megabytes (default: 50MB)

    Returns:
        str: Success message with compression results
    """
    try:
        get_global_logger().tool(DTS.COMPRESS_VIDEO.format(input_video=input_video, output_video=output_video, target_size_mb=target_size_mb))

        video = VideoFileClip(input_video)
        original_size = os.path.getsize(input_video) / (1024 * 1024)  # MB

        # Calculate target bitrate
        duration = video.duration
        target_bits = target_size_mb * 8 * 1024 * 1024  # Convert to bits
        audio_bitrate = 128 * 1000  # 128kbps for audio
        video_bitrate = int((target_bits / duration) - audio_bitrate)

        if video_bitrate < 100000:  # Minimum 100kbps
            video_bitrate = 100000

        # Write compressed video
        video.write_videofile(
            output_video,
            bitrate=f"{video_bitrate}",
            audio_bitrate=f"{audio_bitrate//1000}k",
            verbose=False,
            logger=None
        )

        video.close()

        final_size = os.path.getsize(output_video) / (1024 * 1024)

        return DTR.VIDEO_COMPRESS_SUCCESS.format(input_video=input_video, original_size=original_size, output_video=output_video, final_size=final_size)

    except Exception as e:
        return DTE.VIDEO_COMPRESS.format(error=e)


@tool
@track_tool_call("get_media_info")
def get_media_info(file_path: str) -> str:
    """
    Get detailed information about a media file (video, audio, or image).

    Args:
        file_path: Path to the media file

    Returns:
        str: Formatted media information
    """
    try:
        get_global_logger().tool(DTS.GET_MEDIA_INFO.format(file_path=file_path))

        ext = Path(file_path).suffix.lower()
        info = [f"File: {file_path}"]
        info.append(f"Size: {os.path.getsize(file_path) / 1024:.1f} KB")

        # Video files
        if ext in ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm']:
            video = VideoFileClip(file_path)
            info.append(f"Type: Video")
            info.append(f"Duration: {video.duration:.1f} seconds")
            info.append(f"Resolution: {video.size[0]}x{video.size[1]}")
            info.append(f"FPS: {video.fps}")
            info.append(f"Has Audio: {'Yes' if video.audio else 'No'}")
            video.close()

        # Audio files
        elif ext in ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a']:
            audio = AudioFileClip(file_path)
            info.append(f"Type: Audio")
            info.append(f"Duration: {audio.duration:.1f} seconds")
            audio.close()

        # Image files
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.heic', '.heif', '.tiff']:
            if ext in ['.heic', '.heif']:
                pillow_heif.register_heif_opener()
            img = Image.open(file_path)
            info.append(f"Type: Image")
            info.append(f"Dimensions: {img.size[0]}x{img.size[1]}")
            info.append(f"Mode: {img.mode}")
            info.append(f"Format: {img.format}")
            img.close()

        else:
            info.append(f"Type: Unknown ({ext})")

        return "\n".join(info)

    except Exception as e:
        return DTE.MEDIA_INFO.format(error=e)


# ============================================================================
# System Directory Tools
# ============================================================================

@tool
@track_tool_call("get_user_directory")
def get_user_directory(directory_name: str) -> str:
    """
    Get the path to a standard user directory.

    Args:
        directory_name: Name of the directory - 'home', 'documents', 'downloads',
                       'desktop', 'pictures', 'videos', 'music'

    Returns:
        str: Full path to the directory or error if not recognized
    """
    try:
        get_global_logger().tool(f"Getting user directory: {directory_name}")

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
        }

        name = directory_name.lower().strip()
        if name in dir_map:
            path = dir_map[name]()
            return str(path)

        return f"Unknown directory name: {directory_name}. Valid options: home, documents, downloads, desktop, pictures, videos, music"

    except Exception as e:
        return f"Error getting directory: {e}"


@tool
@track_tool_call("get_system_directory")
def get_system_directory(directory_name: str) -> str:
    """
    Get the path to a system/application directory.

    Args:
        directory_name: Name of the directory - 'appdata', 'localappdata', 'roaming', 'temp'

    Returns:
        str: Full path to the directory or error if not recognized
    """
    try:
        get_global_logger().tool(f"Getting system directory: {directory_name}")

        dir_map = {
            "appdata": get_local_appdata_dir,
            "localappdata": get_local_appdata_dir,
            "local appdata": get_local_appdata_dir,
            "roaming": get_roaming_appdata_dir,
            "roaming appdata": get_roaming_appdata_dir,
            "temp": get_temp_dir,
            "tmp": get_temp_dir,
        }

        name = directory_name.lower().strip()
        if name in dir_map:
            path = dir_map[name]()
            return str(path)

        return f"Unknown directory name: {directory_name}. Valid options: appdata, localappdata, roaming, temp"

    except Exception as e:
        return f"Error getting directory: {e}"


@tool
@track_tool_call("list_user_directories")
def list_user_directories() -> str:
    """
    List all standard user directories with their full paths.

    Returns:
        str: Formatted list of user directories and their paths
    """
    try:
        get_global_logger().tool("Listing all user directories")

        dirs = get_all_user_dirs()
        result = "User Directories:\n"
        for name, path in dirs.items():
            exists = "exists" if path.exists() else "does not exist"
            result += f"  {name.capitalize()}: {path} ({exists})\n"

        return result

    except Exception as e:
        return f"Error listing directories: {e}"


@tool
@track_tool_call("list_system_directories")
def list_system_directories() -> str:
    """
    List all system/application directories with their full paths.

    Returns:
        str: Formatted list of system directories and their paths
    """
    try:
        get_global_logger().tool("Listing all system directories")

        dirs = get_all_system_dirs()
        result = "System Directories:\n"
        for name, path in dirs.items():
            if path is None:
                result += f"  {name}: Not available on this platform\n"
            else:
                exists = "exists" if path.exists() else "does not exist"
                result += f"  {name}: {path} ({exists})\n"

        return result

    except Exception as e:
        return f"Error listing directories: {e}"


@tool
@track_tool_call("resolve_path")
def resolve_path(path_or_alias: str) -> str:
    """
    Resolve a path alias or expand a path with special prefixes.

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
        get_global_logger().tool(f"Resolving path: {path_or_alias}")

        # Check if it's a simple alias first
        resolved = resolve_path_alias(path_or_alias)
        if resolved:
            return str(resolved)

        # Try to split and resolve the first component
        parts = path_or_alias.replace("\\", "/").split("/")
        first_part = parts[0]

        base = resolve_path_alias(first_part)
        if base:
            # Join with remaining parts
            full_path = base
            for part in parts[1:]:
                if part:
                    full_path = full_path / part
            return str(full_path)

        # If not an alias, return as-is (might be a regular path)
        return path_or_alias

    except Exception as e:
        return f"Error resolving path: {e}"


@tool
@track_tool_call("list_folder_aliases")
def list_folder_aliases() -> str:
    """
    List all configured folder aliases.

    Returns:
        str: Formatted list of aliases and their paths
    """
    try:
        from utils.user_config import list_folder_aliases as _list_aliases

        get_global_logger().tool("Listing folder aliases")

        aliases = _list_aliases()

        if not aliases:
            return "No folder aliases configured. Use set_folder_alias to add one."

        result = "Configured Folder Aliases:\n"
        for alias, path in sorted(aliases.items()):
            exists = "exists" if os.path.exists(path) else "path not found"
            result += f"  {alias}: {path} ({exists})\n"

        return result

    except Exception as e:
        return f"Error listing folder aliases: {e}"


@tool
@track_tool_call("get_user_preference")
def get_user_preference(key: str) -> str:
    """
    Get a user preference value.

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

        get_global_logger().tool(f"Getting preference: {key}")

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
@track_tool_call("list_directory_contents")
def list_directory_contents(directory: str, show_hidden: bool = False, max_items: int = 50) -> str:
    """
    List contents of a directory with details.

    Args:
        directory: Path to directory OR alias (e.g., 'downloads', 'desktop')
        show_hidden: Include hidden files (default: False)
        max_items: Maximum number of items to show (default: 50)

    Returns:
        str: Formatted directory listing
    """
    try:
        # Resolve alias if needed
        resolved = resolve_path_alias(directory)
        dir_path = Path(resolved) if resolved else Path(directory)

        if not dir_path.exists():
            return f"Directory does not exist: {dir_path}"

        if not dir_path.is_dir():
            return f"Not a directory: {dir_path}"

        get_global_logger().tool(f"Listing directory: {dir_path}")

        items = []
        for item in dir_path.iterdir():
            if not show_hidden and item.name.startswith('.'):
                continue

            if item.is_dir():
                item_type = "[DIR]"
                size = ""
            else:
                item_type = "[FILE]"
                size_bytes = item.stat().st_size
                if size_bytes < 1024:
                    size = f"{size_bytes}B"
                elif size_bytes < 1024 * 1024:
                    size = f"{size_bytes/1024:.1f}KB"
                else:
                    size = f"{size_bytes/(1024*1024):.1f}MB"

            items.append((item_type, item.name, size))

        # Sort: directories first, then files
        items.sort(key=lambda x: (0 if x[0] == "[DIR]" else 1, x[1].lower()))

        if not items:
            return f"Directory is empty: {dir_path}"

        result = f"Contents of {dir_path}:\n\n"
        for item_type, name, size in items[:max_items]:
            if size:
                result += f"  {item_type} {name} ({size})\n"
            else:
                result += f"  {item_type} {name}\n"

        if len(items) > max_items:
            result += f"\n... and {len(items) - max_items} more items"

        return result

    except Exception as e:
        return f"Error listing directory: {e}"


@tool
@track_tool_call("list_files_recursive")
def list_files_recursive(
    directory: str,
    pattern: str = "*",
    show_hidden: bool = False,
    max_files: int = 200
) -> str:
    """
    Recursively list all files in a directory and its subdirectories.

    Args:
        directory: Path to directory OR alias (e.g., 'downloads', 'prax')
        pattern: Glob pattern to filter files (default: '*' for all files).
                 Examples: '*.pdf', '*.jpg', 'report*', '*.py'
        show_hidden: Include hidden files and directories (default: False)
        max_files: Maximum number of files to return (default: 200)

    Returns:
        str: Formatted list of files with relative paths and sizes
    """
    try:
        # Resolve alias if needed
        resolved = resolve_path_alias(directory)
        dir_path = Path(resolved) if resolved else Path(directory)

        if not dir_path.exists():
            return f"Directory does not exist: {dir_path}"

        if not dir_path.is_dir():
            return f"Not a directory: {dir_path}"

        get_global_logger().tool(f"Recursively listing files in: {dir_path} (pattern: {pattern})")

        files = []
        for file_path in dir_path.rglob(pattern):
            # Skip directories
            if file_path.is_dir():
                continue

            # Skip hidden files/directories if not requested
            if not show_hidden:
                # Check if any part of the path is hidden
                if any(part.startswith('.') for part in file_path.relative_to(dir_path).parts):
                    continue

            try:
                size_bytes = file_path.stat().st_size
                if size_bytes < 1024:
                    size = f"{size_bytes}B"
                elif size_bytes < 1024 * 1024:
                    size = f"{size_bytes/1024:.1f}KB"
                else:
                    size = f"{size_bytes/(1024*1024):.1f}MB"

                rel_path = file_path.relative_to(dir_path)
                files.append((str(rel_path), size, size_bytes))
            except OSError:
                continue

        if not files:
            return f"No files found in {dir_path} matching pattern '{pattern}'"

        # Sort by path
        files.sort(key=lambda x: x[0].lower())

        # Build result
        total_size = sum(f[2] for f in files)
        if total_size < 1024 * 1024:
            total_str = f"{total_size/1024:.1f}KB"
        elif total_size < 1024 * 1024 * 1024:
            total_str = f"{total_size/(1024*1024):.1f}MB"
        else:
            total_str = f"{total_size/(1024*1024*1024):.2f}GB"

        result = f"Files in {dir_path} (pattern: {pattern}):\n"
        result += f"Total: {len(files)} files, {total_str}\n\n"

        for rel_path, size, _ in files[:max_files]:
            result += f"  {rel_path} ({size})\n"

        if len(files) > max_files:
            result += f"\n... and {len(files) - max_files} more files"

        return result

    except Exception as e:
        return f"Error listing files: {e}"


# ============================================================================
# Helper Functions
# ============================================================================

def _parse_page_range(page_range: str, total_pages: int) -> list:
    """Parse page range string into list of 0-indexed page numbers."""
    pages = []
    page_range = page_range.strip().lower()

    # Handle special keywords
    if page_range.startswith("last"):
        try:
            n = int(page_range[4:])
            return list(range(max(0, total_pages - n), total_pages))
        except ValueError:
            return []

    if page_range.startswith("first"):
        try:
            n = int(page_range[5:])
            return list(range(min(n, total_pages)))
        except ValueError:
            return []

    # Handle comma-separated values and ranges
    for part in page_range.split(","):
        part = part.strip()
        if "-" in part:
            try:
                start, end = part.split("-")
                start = int(start) - 1  # Convert to 0-indexed
                end = int(end)  # Keep end as-is for range
                pages.extend(range(max(0, start), min(end, total_pages)))
            except ValueError:
                continue
        else:
            try:
                page = int(part) - 1  # Convert to 0-indexed
                if 0 <= page < total_pages:
                    pages.append(page)
            except ValueError:
                continue

    return sorted(set(pages))


# ============================================================================
# Desktop Tools List
# ============================================================================

def get_desktop_tools_list() -> list:
    """Get list of all desktop utility tools.

    Returns:
        list: List of tool functions
    """
    tools = [
        # PDF Tools
        pdf_extract_pages,
        pdf_delete_pages,
        pdf_merge,
        pdf_split,
        pdf_to_images,

        # Image Tools
        image_convert,
        image_resize,
        image_compress,
        images_to_pdf,
        batch_convert_images,

        # File Management Tools
        batch_rename_files,
        organize_files_by_type,
        find_duplicate_files,

        # Document Tools
        word_to_pdf,
        extract_text_from_pdf,
        ocr_image,

        # Media Tools
        video_to_audio,
        compress_video,
        get_media_info,

        # System Directory Tools
        get_user_directory,
        get_system_directory,
        list_user_directories,
        list_system_directories,
        resolve_path,
        list_directory_contents,
        list_files_recursive,

        # User Config Tools (read-only)
        list_folder_aliases,
        get_user_preference,
    ]
    return tools

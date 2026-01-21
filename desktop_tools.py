"""Desktop utility tools for DeskGenie - file manipulation, conversion, and automation."""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional
from langchain_core.tools import tool
from langfuse_tracking import track_tool_call

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
        print(f"pdf_extract_pages called: {input_pdf} -> {output_pdf}, pages: {page_range}")

        reader = PdfReader(input_pdf)
        writer = PdfWriter()
        total_pages = len(reader.pages)

        # Parse page range
        pages_to_extract = _parse_page_range(page_range, total_pages)

        if not pages_to_extract:
            return f"Error: Invalid page range '{page_range}'. Total pages: {total_pages}"

        for page_num in pages_to_extract:
            writer.add_page(reader.pages[page_num])

        with open(output_pdf, "wb") as f:
            writer.write(f)

        return f"Successfully extracted pages {page_range} from '{input_pdf}' to '{output_pdf}' ({len(pages_to_extract)} pages)"

    except Exception as e:
        return f"Error extracting PDF pages: {e}"


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
        print(f"pdf_delete_pages called: {input_pdf} -> {output_pdf}, delete pages: {page_range}")

        reader = PdfReader(input_pdf)
        writer = PdfWriter()
        total_pages = len(reader.pages)

        # Parse pages to delete
        pages_to_delete = set(_parse_page_range(page_range, total_pages))

        if not pages_to_delete:
            return f"Error: Invalid page range '{page_range}'. Total pages: {total_pages}"

        pages_kept = 0
        for i in range(total_pages):
            if i not in pages_to_delete:
                writer.add_page(reader.pages[i])
                pages_kept += 1

        if pages_kept == 0:
            return "Error: Cannot delete all pages from PDF"

        with open(output_pdf, "wb") as f:
            writer.write(f)

        return f"Successfully deleted pages {page_range} from '{input_pdf}'. Saved to '{output_pdf}' ({pages_kept} pages remaining)"

    except Exception as e:
        return f"Error deleting PDF pages: {e}"


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
        print(f"pdf_merge called: {pdf_files} -> {output_pdf}")

        file_list = [f.strip() for f in pdf_files.split(",")]
        writer = PdfWriter()
        total_pages = 0

        for pdf_path in file_list:
            if not os.path.exists(pdf_path):
                return f"Error: File not found: {pdf_path}"

            reader = PdfReader(pdf_path)
            for page in reader.pages:
                writer.add_page(page)
                total_pages += 1

        with open(output_pdf, "wb") as f:
            writer.write(f)

        return f"Successfully merged {len(file_list)} PDFs into '{output_pdf}' ({total_pages} total pages)"

    except Exception as e:
        return f"Error merging PDFs: {e}"


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
        print(f"pdf_split called: {input_pdf} -> {output_dir}, {pages_per_split} pages each")

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

        return f"Successfully split '{input_pdf}' into {len(created_files)} files in '{output_dir}'"

    except Exception as e:
        return f"Error splitting PDF: {e}"


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
        print(f"pdf_to_images called: {input_pdf} -> {output_dir}")

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
        return f"Successfully converted {len(created_files)} pages to {image_format.upper()} images in '{output_dir}'"

    except Exception as e:
        return f"Error converting PDF to images: {e}"


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
        print(f"image_convert called: {input_image} -> {output_image}")

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

        return f"Successfully converted '{input_image}' ({input_size:.1f}KB) to '{output_image}' ({output_size:.1f}KB)"

    except Exception as e:
        return f"Error converting image: {e}"


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
        print(f"image_resize called: {input_image} -> {output_image}")

        input_ext = Path(input_image).suffix.lower()
        if input_ext in ['.heic', '.heif']:
            pillow_heif.register_heif_opener()

        img = Image.open(input_image)
        original_size = img.size

        if width is None and height is None:
            return "Error: Must specify at least width or height"

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

        return f"Successfully resized '{input_image}' from {original_size} to {img.size}"

    except Exception as e:
        return f"Error resizing image: {e}"


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
        print(f"image_compress called: {input_image} -> {output_image}, target: {target_size_kb}KB")

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

        return f"Compressed '{input_image}' ({original_size:.1f}KB) to '{output_image}' ({final_size:.1f}KB) at quality {best_quality}"

    except Exception as e:
        return f"Error compressing image: {e}"


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
        print(f"batch_convert_images called: {input_dir} -> {output_dir}")

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

        return f"Batch conversion complete: {converted} images converted, {failed} failed"

    except Exception as e:
        return f"Error in batch conversion: {e}"


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
        print(f"batch_rename_files called: {directory}, pattern: {pattern} -> {replacement}")

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
            return f"No files matched pattern '{pattern}'"

        action = "Would rename" if preview_only else "Renamed"
        result = f"{action} {len(renames)} files:\n" + "\n".join(renames[:20])
        if len(renames) > 20:
            result += f"\n... and {len(renames) - 20} more"

        return result

    except Exception as e:
        return f"Error in batch rename: {e}"


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
        print(f"organize_files_by_type called: {source_dir}, by: {organize_by}")

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
        return f"Error organizing files: {e}"


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
        print(f"find_duplicate_files called: {directory}, by_content: {by_content}")

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
            return "No duplicate files found"

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
        return f"Error finding duplicates: {e}"


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
        print(f"word_to_pdf called: {input_docx} -> {output_pdf}")

        docx_to_pdf_convert(input_docx, output_pdf)

        return f"Successfully converted '{input_docx}' to '{output_pdf}'"

    except Exception as e:
        return f"Error converting Word to PDF: {e}"


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
        print(f"extract_text_from_pdf called: {input_pdf}")

        doc = fitz.open(input_pdf)
        text = ""

        for page in doc:
            text += page.get_text() + "\n\n"

        doc.close()

        if output_txt:
            with open(output_txt, 'w', encoding='utf-8') as f:
                f.write(text)
            return f"Successfully extracted text to '{output_txt}' ({len(text)} characters)"

        # Return first 5000 chars if no output file specified
        if len(text) > 5000:
            return text[:5000] + f"\n\n... (truncated, {len(text)} total characters)"
        return text

    except Exception as e:
        return f"Error extracting text from PDF: {e}"


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
            return "Error: Tesseract OCR is not installed. Install with: pip install pytesseract and install Tesseract-OCR"

        print(f"ocr_image called: {input_image}")

        input_ext = Path(input_image).suffix.lower()
        if input_ext in ['.heic', '.heif']:
            pillow_heif.register_heif_opener()

        img = Image.open(input_image)
        text = pytesseract.image_to_string(img, lang=language)

        if output_txt:
            with open(output_txt, 'w', encoding='utf-8') as f:
                f.write(text)
            return f"Successfully extracted text to '{output_txt}' ({len(text)} characters)"

        return text if text.strip() else "No text detected in image"

    except Exception as e:
        return f"Error performing OCR: {e}"


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
        print(f"video_to_audio called: {input_video} -> {output_audio}")

        video = VideoFileClip(input_video)
        audio = video.audio

        if audio is None:
            video.close()
            return f"Error: Video '{input_video}' has no audio track"

        audio.write_audiofile(output_audio, verbose=False, logger=None)

        duration = video.duration
        video.close()

        return f"Successfully extracted audio from '{input_video}' to '{output_audio}' (duration: {duration:.1f}s)"

    except Exception as e:
        return f"Error extracting audio: {e}"


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
        print(f"compress_video called: {input_video} -> {output_video}, target: {target_size_mb}MB")

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

        return f"Compressed '{input_video}' ({original_size:.1f}MB) to '{output_video}' ({final_size:.1f}MB)"

    except Exception as e:
        return f"Error compressing video: {e}"


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
        print(f"get_media_info called: {file_path}")

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
        return f"Error getting media info: {e}"


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
    ]
    return tools

# Contributing to DeskGenie 🧞‍♂️

Thank you for your interest in contributing to DeskGenie! This is a hobbyist open-source project, and we appreciate any help you can provide.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

Be respectful and constructive in all interactions. We're all here to learn and have fun!

- Be respectful of different viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates.

When creating a bug report, include:
- **Clear and descriptive title**
- **Steps to reproduce** the issue
- **Expected behavior**
- **Actual behavior**
- **Environment details** (OS, Python version, etc.)
- **Relevant logs or screenshots**

### Suggesting Enhancements

Enhancement suggestions are welcome! Provide:
- **Clear description** of the enhancement
- **Motivation** for the enhancement
- **Examples** of how it would work
- **Possible implementation** (if you have ideas)

### Pull Requests

We welcome pull requests! Here's how to contribute:

1. **Fork the repository**
2. **Create a branch** for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bugfix-name
   ```
3. **Make your changes** following our coding standards
4. **Test your changes** thoroughly
5. **Commit your changes** with clear messages:
   ```bash
   git commit -m "feat: add PDF page rotation"
   # or
   git commit -m "fix: resolve HEIC conversion error"
   ```
6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Create a Pull Request** to the main repository

## Development Setup

### Prerequisites

- Python 3.10+
- Node.js 18+ (for frontend development)
- [FFmpeg](https://ffmpeg.org/) (for audio/video processing)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) (optional)

### Setting Up the Development Environment

1. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/DeskGenie.git
   cd DeskGenie
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install frontend dependencies**:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

5. **Set up environment variables**:
   ```bash
   export GOOGLE_API_KEY="your_google_api_key"
   # Optional: Langfuse observability
   export LANGFUSE_PUBLIC_KEY="pk-lf-..."
   export LANGFUSE_SECRET_KEY="sk-lf-..."
   ```

6. **Run the development servers**:
   
   **Terminal 1 - Backend**:
   ```bash
   python app/main.py
   ```
   
   **Terminal 2 - Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

## Coding Standards

### Python Code

- Follow [PEP 8](https://peps.python.org/pep-0008/) style guidelines
- Use type hints where appropriate
- Write docstrings for functions and classes
- Keep functions focused and modular
- Use meaningful variable and function names

Example:
```python
def process_pdf(input_path: str, output_path: str) -> bool:
    """
    Process a PDF file and save the result.
    
    Args:
        input_path: Path to the input PDF file
        output_path: Path to save the processed PDF
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Processing logic here
        return True
    except Exception as e:
        logger.error(f"PDF processing failed: {e}")
        return False
```

### JavaScript/React Code

- Follow modern JavaScript/React best practices
- Use functional components and hooks
- Keep components small and focused
- Use meaningful variable and function names
- Add comments for complex logic

Example:
```jsx
function FileProcessor({ file, onComplete }) {
  const [processing, setProcessing] = useState(false);
  
  const handleProcess = async () => {
    setProcessing(true);
    try {
      await processFile(file);
      onComplete();
    } catch (error) {
      console.error('Processing failed:', error);
    } finally {
      setProcessing(false);
    }
  };
  
  return (
    <button onClick={handleProcess} disabled={processing}>
      {processing ? 'Processing...' : 'Process File'}
    </button>
  );
}
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

Examples:
```
feat: add support for AVIF image format
fix: resolve memory leak in batch processing
docs: update installation instructions
refactor: improve agent tool selection logic
```

## Testing

### Python Tests

Write tests for new functionality using pytest:

```python
import pytest
from tools.desktop_tools import pdf_extract_pages

def test_pdf_extract_pages():
    result = pdf_extract_pages.invoke({
        "input_pdf": "test.pdf",
        "output_pdf": "output.pdf",
        "page_range": "1-3"
    })
    assert result is True
```

### Testing Tools

- Test tools with sample files
- Verify error handling
- Check edge cases

### Frontend Tests

- Test UI components with user interactions
- Verify API integration
- Check responsive design

## Submitting Changes

### Before Submitting

1. **Run tests** to ensure nothing is broken
2. **Check code style** using linters
3. **Update documentation** if needed
4. **Test manually** with various scenarios
5. **Clean up** any temporary files or debugging code

### Pull Request Checklist

- [ ] Code follows project coding standards
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] Commit messages follow conventional commits
- [ ] No merge conflicts with main branch
- [ ] Description explains the changes clearly

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe how you tested your changes

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review
- [ ] I have commented my code where needed
- [ ] I have updated documentation
- [ ] My changes generate no new warnings
```

## Areas for Contribution

Looking for ideas? Here are some areas where we need help:

### Tools & Features
- Add more file format conversions (e.g., EPUB, MOBI)
- Improve batch processing performance
- Add video transcoding options
- Implement file compression tools
- Add cloud storage integration (Google Drive, Dropbox)
- Create file encryption/decryption tools

### AI & Agent
- Improve natural language understanding
- Add support for more LLM providers (OpenAI, Anthropic, etc.)
- Implement multi-step task planning
- Add memory/context management
- Improve tool selection logic

### UI/UX
- Create native desktop UI (Electron, Tauri)
- Add dark/light theme toggle
- Implement drag-and-drop file upload
- Add keyboard shortcuts
- Improve mobile responsiveness

### Testing & Quality
- Add comprehensive test suite
- Implement automated testing
- Add performance benchmarks
- Improve error messages and user feedback

### Documentation
- Write more usage examples
- Create video tutorials
- Add API documentation
- Improve troubleshooting guide
- Translate documentation to other languages

## Reporting Issues

When reporting issues, please:

1. **Search existing issues** first
2. **Use the issue template** if available
3. **Provide as much detail as possible**
4. **Include reproduction steps**
5. **Add screenshots/logs** when applicable

## Questions?

If you have questions about contributing:
- Check existing issues and pull requests
- Read the documentation
- Open an issue with the "question" label

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to DeskGenie! 🎉
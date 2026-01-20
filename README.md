---
title: GAIA Benchmark Agent
emoji: 🕵🏻‍♂️
colorFrom: indigo
colorTo: indigo
sdk: gradio
sdk_version: 6.2.0
app_file: app.py
pinned: false
hf_oauth: true
hf_oauth_expiration_minutes: 480
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference


# GAIA Benchmark Agent

A LangGraph-based AI agent designed to solve questions from the GAIA (General AI Assistants) benchmark. This agent uses Google's Gemini model with custom tools for web search, file processing, and multimodal analysis to answer complex questions requiring reasoning and information gathering.

## Features

- **LangGraph Architecture**: Implements a state-graph agent workflow with tool calling capabilities
- **Multimodal Capabilities**:
  - Image analysis (PNG, JPG, JPEG, GIF, WebP, BMP)
  - YouTube video analysis and transcript extraction
  - Audio transcription (MP3)
  - PDF and Excel file processing
- **Web Research Tools**:
  - DuckDuckGo web search
  - Wikipedia integration
  - ArXiv academic paper search
  - Web page content extraction
- **Mathematical Operations**: Basic arithmetic and modulus operations
- **Gradio Interface**: User-friendly web UI for testing and evaluation
- **Automated Evaluation**: Fetches questions from API, processes them, and submits answers
- **Observability**: Built-in integration with Langfuse for tracking traces and metrics

## Project Structure

```
GAIA_Benchmark_Agent/
├── app.py              # Main application entry point
├── agents.py           # LangGraph agent implementation
├── custom_tools.py     # Tool definitions for web search, files, etc.
├── system_prompt.py    # Agent system prompt and instructions
├── gradioapp.py        # Gradio UI components
├── requirements.txt    # Python dependencies
└── files/
    └── metadata.jsonl  # Ground truth data for local testing
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/GAIA_Benchmark_Agent.git
cd GAIA_Benchmark_Agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export GOOGLE_API_KEY="your_google_api_key"
export HUGGINGFACEHUB_API_TOKEN="your_hf_token"  # Optional.  not yet used

# Langfuse Observability (Optional)
export LANGFUSE_PUBLIC_KEY="pk-lf-..."
export LANGFUSE_SECRET_KEY="sk-lf-..."
export LANGFUSE_HOST="https://cloud.langfuse.com" # Optional
```

## Requirements

- Python 3.8+
- Google API Key (for Gemini model)
- ffmpeg (optional, for audio processing)

### Key Dependencies

- `langchain-core`, `langgraph` - Agent framework
- `langchain-google-genai` - Google Gemini integration
- `gradio` - Web UI
- `requests`, `beautifulsoup4` - Web scraping
- `pypdf`, `pandas` - File processing
- `youtube-transcript-api` - YouTube integration
- `ddgs` - DuckDuckGo search

## Usage

### Running the Gradio Interface

Launch the web interface for interactive testing:

```bash
python app.py
```

This will start a Gradio app where you can:
- Log in with your Hugging Face account
- Run evaluation on all questions
- Test individual questions
- View results and scores

### Running Local Tests

Test the agent on specific questions without the web interface:

```bash
python app.py --test
```

Edit the question indices in [app.py:196](app.py#L196) to customize which questions to test.

### Using the Agent Programmatically

```python
from agents import MyGAIAAgents

# Initialize agent (automatically uses ACTIVE_AGENT from config)
agent = MyGAIAAgents()

# Ask a question
answer = agent("What is the capital of France?")
print(answer)

# Ask a question with a file reference
answer = agent(
    "What data is in this spreadsheet?",
    file_name="data.xlsx"
)
print(answer)
```

## How It Works

### Agent Architecture

The agent is built using LangGraph with the following workflow:

1. **Initialize**: Loads the question and system prompt
2. **Assistant Node**: Calls the LLM (Gemini) to decide on tool usage
3. **Tool Node**: Executes requested tools (search, file reading, etc.)
4. **Iteration**: Loops between assistant and tools until answer is found
5. **Termination**: Returns final answer or hits step limit (25 steps max)

### Available Tools

**Search & Research:**
- `websearch` - DuckDuckGo web search
- `wiki_search` - Wikipedia articles
- `arvix_search` - Academic papers
- `get_webpage_content` - Extract webpage text
- `get_youtube_transcript` - YouTube video transcripts
- `analyze_youtube_video` - AI analysis of YouTube videos

**File Processing:**
- `read_excel_file` - Read Excel spreadsheets
- `read_python_script` - Read Python source code
- `parse_audio_file` - Transcribe MP3 files
- `analyze_image` - AI vision analysis of images

**Utilities:**
- Math operations: `add`, `subtract`, `multiply`, `divide`, `power`, `modulus`
- `string_reverse` - Reverse encoded/gibberish text
- `get_current_time_in_timezone` - Get time in any timezone

### System Prompt

The agent follows strict output formatting rules defined in [system_prompt.py](system_prompt.py):
- Returns only the final answer (no conversational filler)
- No markdown formatting or JSON structures
- Uses tools instead of guessing
- Handles encoded/reversed text
- Verifies answers before output

## Configuration

### Change Agent Type

Edit the `ACTIVE_AGENT` variable in [config.py:32](config.py#L32):

```python
# Valid values: "LangGraph", "ReActLangGraph", "LLamaIndex", "SMOL"
ACTIVE_AGENT = "LangGraph"  # Currently only LangGraph is implemented
```

The `MyGAIAAgents` wrapper class will automatically instantiate the correct agent based on this configuration.

### Adjust Step Limits

Modify the maximum iteration count in [agents.py:169](agents.py#L169):

```python
if step_count >= 25:  # Change this value
    # ...
```

### Customize Tools

Add or modify tools in [custom_tools.py](custom_tools.py) using the `@tool` decorator:

```python
from langchain_core.tools import tool

@tool
def my_custom_tool(param: str) -> str:
    """Tool description for the LLM."""
    # Implementation
    return result
```

## API Integration

The agent integrates with the GAIA benchmark API:

- **Questions Endpoint**: `https://agents-course-unit4-scoring.hf.space/questions`
- **Submit Endpoint**: `https://agents-course-unit4-scoring.hf.space/submit`

Questions may include file references which are automatically fetched from:
- Local `files/` directory (if available)
- Remote API endpoint (fallback)

## Testing

### Local Ground Truth Verification

The app includes local verification against ground truth data in `files/metadata.jsonl`. This allows you to test your agent's performance before submitting to the evaluation server.

### Test Mode

Run specific questions in test mode by modifying [app.py:196](app.py#L196):

```python
my_questions = [
    {
        "question": my_questions_data[i]["question"],
        "file_name": my_questions_data[i].get("file_name")
    }
    for i in (0, 5, 17) if i < len(my_questions_data)  # Customize indices
]
```

## Performance Considerations

- **Timeout**: Agent has 180-second timeout per question
- **Step Limit**: Maximum 25 reasoning steps to prevent infinite loops
- **Tool Timeouts**: Individual tools have their own timeout settings
- **Cost**: Uses Google Gemini API (gemini-2.5-flash model)

## Deployment

### Hugging Face Spaces

This project is designed to run on Hugging Face Spaces:

1. Create a new Space on Hugging Face
2. Set SDK to Gradio (version 6.2.0+)
3. Add environment variables: `GOOGLE_API_KEY`, `SPACE_ID`, `SPACE_HOST`
4. Enable OAuth authentication

The app will automatically detect the Hugging Face environment and configure URLs accordingly.

### Local Deployment

Simply run `python app.py` locally. The app will detect it's not in a Hugging Face Space and adjust behavior accordingly.

## Troubleshooting

### Common Issues

**"GOOGLE_API_KEY not found"**
- Set the environment variable: `export GOOGLE_API_KEY="your_key"`

**Audio parsing fails**
- Install ffmpeg: `apt-get install ffmpeg` (Linux) or `brew install ffmpeg` (macOS)

**Tool timeouts**
- Adjust timeout values in respective tool functions in [custom_tools.py](custom_tools.py)

**Agent exceeds step limit**
- Increase limit in [agents.py:169](agents.py#L169) or optimize tool usage in system prompt

## Contributing

Contributions are welcome! Areas for improvement:
- Add more tools (database access, code execution, etc.)
- Move the Benchmark from 50% to 100%
- Improve error handling and retry logic
- Try with smaller LLMs
- Make it work with Ollama

## License

This project is open-source and available under the MIT License.

## Acknowledgments

- Built for the GAIA (General AI Assistants) benchmark
- Uses Google's Gemini model via LangChain
- LangGraph framework by LangChain
- Gradio for web interface

## Contact

For questions, issues, or suggestions, please open an issue on GitHub.

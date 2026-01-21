"""Ollama chat interface for DeskGenie - local LLM chat functionality."""

import json
import requests
from typing import Optional, Generator, List, Dict, Any
from dataclasses import dataclass, field
from langchain_core.tools import tool
from langfuse_tracking import track_tool_call
import config


@dataclass
class ChatMessage:
    """Represents a chat message."""
    role: str  # 'user', 'assistant', or 'system'
    content: str


@dataclass
class ChatSession:
    """Manages a chat conversation session."""
    model: str = config.OLLAMA_DEFAULT_MODEL
    messages: List[ChatMessage] = field(default_factory=list)
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    context_window: int = 4096

    def add_message(self, role: str, content: str):
        """Add a message to the conversation history."""
        self.messages.append(ChatMessage(role=role, content=content))

    def get_messages_for_api(self) -> List[Dict[str, str]]:
        """Convert messages to Ollama API format."""
        api_messages = []
        if self.system_prompt:
            api_messages.append({"role": "system", "content": self.system_prompt})
        for msg in self.messages:
            api_messages.append({"role": msg.role, "content": msg.content})
        return api_messages

    def clear(self):
        """Clear conversation history."""
        self.messages = []


class OllamaClient:
    """Client for interacting with Ollama API."""

    def __init__(self, base_url: str = config.OLLAMA_BASE_URL):
        self.base_url = base_url.rstrip("/")

    def is_running(self) -> bool:
        """Check if Ollama server is running."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def list_models(self) -> List[Dict[str, Any]]:
        """List available models."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("models", [])
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to connect to Ollama: {e}")

    def pull_model(self, model_name: str) -> Generator[str, None, None]:
        """Pull a model from Ollama registry (streaming progress)."""
        try:
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                stream=True,
                timeout=600  # 10 minutes for large models
            )
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    status = data.get("status", "")
                    if "completed" in data and "total" in data:
                        progress = (data["completed"] / data["total"]) * 100
                        yield f"{status}: {progress:.1f}%"
                    else:
                        yield status

        except requests.RequestException as e:
            raise ConnectionError(f"Failed to pull model: {e}")

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = config.OLLAMA_DEFAULT_MODEL,
        temperature: float = 0.7,
        stream: bool = False,
        context_length: int = 4096
    ) -> str | Generator[str, None, None]:
        """
        Send a chat request to Ollama.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name to use
            temperature: Sampling temperature (0-1)
            stream: Whether to stream the response
            context_length: Maximum context window

        Returns:
            Response text or generator for streaming
        """
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_ctx": context_length
            }
        }

        try:
            if stream:
                return self._stream_chat(payload)
            else:
                response = requests.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                    timeout=120
                )
                response.raise_for_status()
                data = response.json()
                return data.get("message", {}).get("content", "")

        except requests.RequestException as e:
            raise ConnectionError(f"Chat request failed: {e}")

    def _stream_chat(self, payload: Dict) -> Generator[str, None, None]:
        """Stream chat response."""
        response = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            stream=True,
            timeout=120
        )
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                content = data.get("message", {}).get("content", "")
                if content:
                    yield content
                if data.get("done", False):
                    break

    def generate(
        self,
        prompt: str,
        model: str = config.OLLAMA_DEFAULT_MODEL,
        system: Optional[str] = None,
        temperature: float = 0.7,
        stream: bool = False
    ) -> str | Generator[str, None, None]:
        """
        Generate a completion (non-chat mode).

        Args:
            prompt: The input prompt
            model: Model name to use
            system: Optional system prompt
            temperature: Sampling temperature
            stream: Whether to stream the response

        Returns:
            Generated text or generator for streaming
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature
            }
        }
        if system:
            payload["system"] = system

        try:
            if stream:
                return self._stream_generate(payload)
            else:
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=120
                )
                response.raise_for_status()
                data = response.json()
                return data.get("response", "")

        except requests.RequestException as e:
            raise ConnectionError(f"Generate request failed: {e}")

    def _stream_generate(self, payload: Dict) -> Generator[str, None, None]:
        """Stream generate response."""
        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            stream=True,
            timeout=120
        )
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                content = data.get("response", "")
                if content:
                    yield content
                if data.get("done", False):
                    break

    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get detailed information about a model."""
        try:
            response = requests.post(
                f"{self.base_url}/api/show",
                json={"name": model_name},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to get model info: {e}")


# Global client instance
_ollama_client: Optional[OllamaClient] = None


def get_ollama_client() -> OllamaClient:
    """Get or create the global Ollama client."""
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient()
    return _ollama_client


# ============================================================================
# Ollama Tools for Agent
# ============================================================================

@tool
@track_tool_call("ollama_chat")
def ollama_chat(message: str, model: str = config.OLLAMA_DEFAULT_MODEL, system_prompt: str = "") -> str:
    """
    Send a message to Ollama and get a response. Uses local LLM for chat.

    Args:
        message: The user message to send
        model: Model name to use (e.g., 'llama3.2', 'mistral', 'codellama')
        system_prompt: Optional system prompt to set context

    Returns:
        str: The model's response or error message
    """
    try:
        print(f"ollama_chat called: model={model}, message length={len(message)}")

        client = get_ollama_client()

        if not client.is_running():
            return "Error: Ollama is not running. Start it with 'ollama serve' or ensure the Ollama app is running."

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})

        response = client.chat(messages, model=model)
        return response

    except ConnectionError as e:
        return f"Connection error: {e}"
    except Exception as e:
        return f"Error in Ollama chat: {e}"


@tool
@track_tool_call("ollama_list_models")
def ollama_list_models() -> str:
    """
    List all available Ollama models installed locally.

    Returns:
        str: Formatted list of available models
    """
    try:
        print("ollama_list_models called")

        client = get_ollama_client()

        if not client.is_running():
            return "Error: Ollama is not running. Start it with 'ollama serve' or ensure the Ollama app is running."

        models = client.list_models()

        if not models:
            return "No models installed. Use 'ollama pull <model>' to download models."

        result = "Available Ollama Models:\n\n"
        for model in models:
            name = model.get("name", "unknown")
            size = model.get("size", 0) / (1024 * 1024 * 1024)  # Convert to GB
            modified = model.get("modified_at", "")[:10]  # Just date part
            result += f"  • {name} ({size:.1f}GB) - modified {modified}\n"

        return result

    except ConnectionError as e:
        return f"Connection error: {e}"
    except Exception as e:
        return f"Error listing models: {e}"


@tool
@track_tool_call("ollama_model_info")
def ollama_model_info(model_name: str) -> str:
    """
    Get detailed information about a specific Ollama model.

    Args:
        model_name: Name of the model (e.g., 'llama3.2', 'mistral')

    Returns:
        str: Detailed model information
    """
    try:
        print(f"ollama_model_info called: {model_name}")

        client = get_ollama_client()

        if not client.is_running():
            return "Error: Ollama is not running."

        info = client.get_model_info(model_name)

        result = f"Model: {model_name}\n\n"

        if "modelfile" in info:
            # Extract key info from modelfile
            modelfile = info["modelfile"]
            lines = modelfile.split("\n")
            for line in lines[:20]:  # First 20 lines
                if line.strip() and not line.startswith("#"):
                    result += f"{line}\n"

        if "parameters" in info:
            result += f"\nParameters: {info['parameters']}"

        if "template" in info:
            result += f"\nTemplate available: Yes"

        return result

    except ConnectionError as e:
        return f"Connection error: {e}"
    except Exception as e:
        return f"Error getting model info: {e}"


@tool
@track_tool_call("ollama_summarize")
def ollama_summarize(text: str, model: str = config.OLLAMA_DEFAULT_MODEL, style: str = "concise") -> str:
    """
    Summarize text using Ollama local LLM.

    Args:
        text: The text to summarize
        model: Model to use for summarization
        style: Summary style - 'concise' (bullet points), 'detailed', or 'brief' (one paragraph)

    Returns:
        str: Summarized text
    """
    try:
        print(f"ollama_summarize called: model={model}, style={style}, text length={len(text)}")

        client = get_ollama_client()

        if not client.is_running():
            return "Error: Ollama is not running."

        style_prompts = {
            "concise": "Summarize the following text as bullet points, capturing the key information:",
            "detailed": "Provide a comprehensive summary of the following text, maintaining important details:",
            "brief": "Summarize the following text in one short paragraph:"
        }

        system_prompt = style_prompts.get(style, style_prompts["concise"])
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]

        response = client.chat(messages, model=model, temperature=0.3)
        return response

    except ConnectionError as e:
        return f"Connection error: {e}"
    except Exception as e:
        return f"Error summarizing: {e}"


@tool
@track_tool_call("ollama_translate")
def ollama_translate(text: str, target_language: str, model: str = config.OLLAMA_DEFAULT_MODEL) -> str:
    """
    Translate text to a target language using Ollama.

    Args:
        text: The text to translate
        target_language: Target language (e.g., 'Spanish', 'French', 'German', 'Japanese')
        model: Model to use for translation

    Returns:
        str: Translated text
    """
    try:
        print(f"ollama_translate called: target={target_language}, text length={len(text)}")

        client = get_ollama_client()

        if not client.is_running():
            return "Error: Ollama is not running."

        messages = [
            {"role": "system", "content": f"You are a professional translator. Translate the following text to {target_language}. Only output the translation, nothing else."},
            {"role": "user", "content": text}
        ]

        response = client.chat(messages, model=model, temperature=0.3)
        return response

    except ConnectionError as e:
        return f"Connection error: {e}"
    except Exception as e:
        return f"Error translating: {e}"


@tool
@track_tool_call("ollama_code_explain")
def ollama_code_explain(code: str, language: str = "auto", model: str = config.OLLAMA_DEFAULT_MODEL) -> str:
    """
    Explain code using Ollama. Works best with code-focused models like codellama.

    Args:
        code: The code to explain
        language: Programming language (or 'auto' to detect)
        model: Model to use (recommend 'codellama' for code)

    Returns:
        str: Explanation of the code
    """
    try:
        print(f"ollama_code_explain called: language={language}, code length={len(code)}")

        client = get_ollama_client()

        if not client.is_running():
            return "Error: Ollama is not running."

        lang_hint = f"This is {language} code. " if language != "auto" else ""

        messages = [
            {"role": "system", "content": f"You are a helpful programming assistant. {lang_hint}Explain the following code clearly, describing what it does, how it works, and any important patterns or techniques used."},
            {"role": "user", "content": f"```\n{code}\n```"}
        ]

        response = client.chat(messages, model=model, temperature=0.3)
        return response

    except ConnectionError as e:
        return f"Connection error: {e}"
    except Exception as e:
        return f"Error explaining code: {e}"


@tool
@track_tool_call("ollama_rewrite")
def ollama_rewrite(text: str, style: str = "professional", model: str = config.OLLAMA_DEFAULT_MODEL) -> str:
    """
    Rewrite text in a different style using Ollama.

    Args:
        text: The text to rewrite
        style: Target style - 'professional', 'casual', 'formal', 'simplified', 'technical'
        model: Model to use

    Returns:
        str: Rewritten text
    """
    try:
        print(f"ollama_rewrite called: style={style}, text length={len(text)}")

        client = get_ollama_client()

        if not client.is_running():
            return "Error: Ollama is not running."

        style_instructions = {
            "professional": "Rewrite in a professional, business-appropriate tone",
            "casual": "Rewrite in a casual, friendly tone",
            "formal": "Rewrite in a formal, academic tone",
            "simplified": "Rewrite using simple words and short sentences, making it easy to understand",
            "technical": "Rewrite with precise technical terminology"
        }

        instruction = style_instructions.get(style, style_instructions["professional"])

        messages = [
            {"role": "system", "content": f"{instruction}. Maintain the original meaning. Only output the rewritten text."},
            {"role": "user", "content": text}
        ]

        response = client.chat(messages, model=model, temperature=0.5)
        return response

    except ConnectionError as e:
        return f"Connection error: {e}"
    except Exception as e:
        return f"Error rewriting: {e}"


# ============================================================================
# Ollama Tools List
# ============================================================================

def get_ollama_tools_list() -> list:
    """Get list of all Ollama-related tools.

    Returns:
        list: List of tool functions
    """
    tools = [
        ollama_chat,
        ollama_list_models,
        ollama_model_info,
        ollama_summarize,
        ollama_translate,
        ollama_code_explain,
        ollama_rewrite,
    ]
    return tools

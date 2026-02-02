"""Utility functions for GAIA Benchmark Agent including retry logic and answer cleanup."""

import time
import requests
from typing import Callable, Any
from functools import wraps
from app import config
from resources.log_strings import UtilityMessages as UM


def retry_with_backoff(
    max_retries: int = config.MAX_RETRIES,
    initial_delay: float = config.INITIAL_RETRY_DELAY,
    backoff_factor: float = config.RETRY_BACKOFF_FACTOR,
    exceptions: tuple = (requests.RequestException,)
):
    """
    Decorator to retry a function with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds before first retry
        backoff_factor: Multiplier for delay after each retry
        exceptions: Tuple of exception types to catch and retry
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        print(UM.RETRY_FAILED.format(attempt=attempt + 1, max_retries=max_retries, error=e))
                        print(UM.RETRY_WAITING.format(delay=delay))
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        print(UM.RETRY_EXHAUSTED.format(max_retries=max_retries))

            # Re-raise the last exception if all retries failed
            raise last_exception

        return wrapper
    return decorator


def extract_text_from_content(content: Any) -> str:
    """
    Extract plain text from various content formats returned by LLM agents.

    This function handles multiple content formats:
    - AgentOutput objects (LlamaIndex): Extracts the response attribute
    - Message objects with 'content' attribute: Extracts the content attribute
      (works for LlamaIndex ChatMessage, LangChain AIMessage, etc.)
    - String: Returns as-is
    - Dict with 'text' field: Extracts the text value
    - List of content blocks: Extracts text from all blocks with type='text'
    - Other types: Converts to string

    Args:
        content: The content object from an LLM response (can be str, dict, list, etc.)

    Returns:
        str: Extracted plain text content
    """
    # Handle LlamaIndex AgentOutput objects (has 'response' attribute)
    if hasattr(content, 'response') and not isinstance(content, (str, dict, list)):
        # Extract the response attribute from AgentOutput
        response = content.response
        # The response might itself be a message object with 'content'
        if hasattr(response, 'content'):
            return str(response.content)
        elif hasattr(response, 'message') and hasattr(response.message, 'content'):
            return str(response.message.content)
        else:
            return str(response)

    # Handle message objects with 'content' attribute (e.g., ChatMessage from various frameworks)
    # This works for LlamaIndex ChatMessage, LangChain AIMessage, etc.
    if hasattr(content, 'content') and not isinstance(content, (str, dict, list)):
        # Extract the content attribute (works for any message object)
        return str(content.content)

    # Handle dict format (e.g., {'text': 'answer'})
    if isinstance(content, dict):
        if 'text' in content:
            return str(content['text'])
        else:
            print(UM.CONTENT_DICT_WARNING)
            return str(content)

    # Handle list format (e.g., [{'type': 'text', 'text': 'answer'}])
    elif isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict):
                # Look for items with type='text' and extract the 'text' field
                if item.get('type') == 'text':
                    text_parts.append(str(item.get('text', '')))
                # Fallback: if there's a 'text' field but no type, use it
                elif 'text' in item:
                    text_parts.append(str(item['text']))
            elif isinstance(item, str):
                text_parts.append(item)
            else:
                text_parts.append(str(item))

        result = ' '.join(text_parts)
        return result

    # Handle string format (already plain text)
    elif isinstance(content, str):
        return content

    # Fallback for other types
    else:
        return str(content)


def cleanup_answer(answer: Any) -> str:
    """
    Clean up the agent answer to ensure it's in plain text format.

    This function:
    - Converts answer to string
    - Removes comma separators from numbers (e.g., "1,000" -> "1000")
    - Strips whitespace and trailing punctuation
    - Logs warnings for verbose or malformatted answers

    Args:
        answer: The raw answer from the agent (can be str, dict, list, etc.)

    Returns:
        str: Cleaned up answer as plain text
    """
    # Convert to string and strip whitespace
    answer = str(answer).strip()

    # Remove comma separators from numbers (e.g., "1,000" -> "1000")
    if ',' in answer and answer.replace(',', '').replace('.', '').isdigit():
        answer = answer.replace(',', '')

    # Ensure no trailing/leading whitespace or punctuation
    answer = answer.strip().rstrip('.')

    return answer

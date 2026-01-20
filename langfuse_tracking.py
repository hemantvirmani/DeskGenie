"""Langfuse tracking integration for GAIA Benchmark Agent.

This module provides decorators and context managers for tracking:
- Agent execution sessions
- LLM invocations
- Tool calls
- Question processing
"""

import os
import functools
import time
from typing import Any, Optional, Dict
from contextlib import contextmanager

# Langfuse will be imported conditionally
langfuse = None

try:
    from langfuse import Langfuse, observe
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    print("[INFO] Langfuse not installed. Tracking is disabled. Install with: pip install langfuse")


class LangfuseTracker:
    """Singleton class to manage Langfuse client and tracking state."""

    _instance = None
    _client = None
    _enabled = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize Langfuse client if not already initialized."""
        if self._client is None and LANGFUSE_AVAILABLE:
            public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
            secret_key = os.getenv("LANGFUSE_SECRET_KEY")
            host = os.getenv("LANGFUSE_HOST", "https://us.cloud.langfuse.com")

            if public_key and secret_key:
                self._client = Langfuse(
                    public_key=public_key,
                    secret_key=secret_key,
                    host=host
                )
                self._enabled = True
                print(f"[LANGFUSE] Tracking enabled (host: {host})")
            else:
                print("[LANGFUSE] Tracking disabled. Set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY to enable.")

    @property
    def enabled(self) -> bool:
        """Check if Langfuse tracking is enabled."""
        return self._enabled and LANGFUSE_AVAILABLE

    @property
    def client(self):
        """Get Langfuse client instance."""
        return self._client if self.enabled else None


# Global tracker instance
tracker = LangfuseTracker()


def track_agent_execution(agent_type: str):
    """Decorator to track agent execution lifecycle.

    Args:
        agent_type: Type of agent (e.g., "LangGraph", "ReAct", "LlamaIndex")

    Usage:
        @track_agent_execution("LangGraph")
        def __call__(self, question: str, file_name: str = None) -> str:
            ...
    """
    def decorator(func):
        if not tracker.enabled:
            return func

        @observe(name=f"{agent_type}_Agent_Execution")
        @functools.wraps(func)
        def wrapper(self, question: str, file_name: str = None, *args, **kwargs):
            # Add metadata to current observation
            if tracker.client:
                tracker.client.update_current_span(
                    metadata={
                        "agent_type": agent_type,
                        "has_file": file_name is not None,
                        "file_name": file_name or "none",
                        "question_length": len(question)
                    },
                    input={"question": question[:500], "file_name": file_name}  # Limit question length
                )

            start_time = time.time()
            try:
                result = func(self, question, file_name, *args, **kwargs)

                # Update with output and success metrics
                if tracker.client:
                    tracker.client.update_current_span(
                        output={"answer": str(result)[:500]},  # Limit answer length
                        metadata={
                            "execution_time_seconds": time.time() - start_time,
                            "success": not result.startswith("Error:")
                        }
                    )
                return result
            except Exception as e:
                # Track errors
                if tracker.client:
                    tracker.client.update_current_span(
                        level="ERROR",
                        status_message=str(e),
                        metadata={
                            "execution_time_seconds": time.time() - start_time,
                            "error": str(e)
                        }
                    )
                raise

        return wrapper
    return decorator


def track_llm_call(model_name: str):
    """Decorator to track LLM invocations.

    Args:
        model_name: Name of the LLM model being called

    Usage:
        @track_llm_call("gemini-1.5-flash")
        def _assistant(self, state):
            response = self.llm_client_with_tools.invoke(state["messages"])
            ...
    """
    def decorator(func):
        if not tracker.enabled:
            return func

        @observe(as_type="generation", name=f"LLM_Call_{model_name}")
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = func(*args, **kwargs)

                # Update generation with model info
                if tracker.client:
                    tracker.client.update_current_generation(
                        model=model_name,
                        metadata={
                            "latency_seconds": time.time() - start_time,
                        }
                    )

                return result
            except Exception as e:
                if tracker.client:
                    tracker.client.update_current_generation(
                        level="ERROR",
                        status_message=str(e),
                        metadata={
                            "latency_seconds": time.time() - start_time,
                            "error": str(e)
                        }
                    )
                raise

        return wrapper
    return decorator


def track_tool_call(tool_name: str):
    """Decorator to track tool/function calls.

    Args:
        tool_name: Name of the tool being called

    Usage:
        @track_tool_call("websearch")
        def websearch(query: str, num_results: int = 5):
            ...
    """
    def decorator(func):
        if not tracker.enabled:
            return func

        @observe(name=f"Tool_{tool_name}")
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Capture input parameters
            if tracker.client:
                tracker.client.update_current_span(
                    input={
                        "tool": tool_name,
                        "args": args[:3] if args else [],  # Limit args
                        "kwargs": {k: str(v)[:100] for k, v in list(kwargs.items())[:5]}  # Limit kwargs
                    },
                    metadata={"tool_name": tool_name}
                )

            start_time = time.time()
            try:
                result = func(*args, **kwargs)

                # Track output
                result_str = str(result)
                if tracker.client:
                    tracker.client.update_current_span(
                        output={
                            "result_preview": result_str[:500],
                            "result_length": len(result_str)
                        },
                        metadata={
                            "execution_time_seconds": time.time() - start_time,
                            "success": True
                        }
                    )

                return result
            except Exception as e:
                if tracker.client:
                    tracker.client.update_current_span(
                        level="ERROR",
                        status_message=str(e),
                        metadata={
                            "execution_time_seconds": time.time() - start_time,
                            "error": str(e)
                        }
                    )
                raise

        return wrapper
    return decorator


@contextmanager
def track_session(session_name: str, metadata: Optional[Dict[str, Any]] = None):
    """Context manager to track a complete session (batch processing).

    Args:
        session_name: Name of the session (e.g., "Test_Run", "Full_Submission")
        metadata: Optional metadata dict

    Usage:
        with track_session("Test_Run", {"agent": "LangGraph", "questions": 20}):
            # Run agent on questions
            ...
    """
    if not tracker.enabled:
        yield
        return

    # Use start_as_current_span to create a root span/trace for the session
    with tracker.client.start_as_current_span(
        name=session_name,
        metadata=metadata or {}
    ) as span:
        try:
            yield span
        finally:
            # Flush to ensure data is sent
            if tracker.client:
                tracker.client.flush()


@contextmanager
def track_question_processing(task_id: str, question: str):
    """Context manager to track individual question processing.

    Args:
        task_id: Unique task identifier
        question: Question text

    Usage:
        with track_question_processing(task_id, question_text) as span:
            answer = agent(question_text)
            span.update(output={"answer": answer})
    """
    if not tracker.enabled:
        yield None
        return

    with tracker.client.start_as_current_span(
        name=f"Question_{task_id[:8]}",
        input={"task_id": task_id, "question": question[:300]},
        metadata={"task_id": task_id}
    ) as span:
        yield span


# Convenience function for manual span creation
def create_span(name: str, input_data: Optional[Dict] = None, metadata: Optional[Dict] = None):
    """Create a manual span for tracking custom operations.

    Args:
        name: Span name
        input_data: Input data dict
        metadata: Metadata dict

    Returns:
        Span context manager or None if tracking disabled
    """
    if not tracker.enabled:
        return None

    return tracker.client.start_span(
        name=name,
        input=input_data,
        metadata=metadata
    )

"""Log streaming for DeskGenie UI.

This module provides a LogStreamer class that can be used to stream logs
from agents and question runners to the frontend via SSE.
"""

import asyncio
import time
from typing import Optional, Callable, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import threading


class LogLevel(Enum):
    """Log levels for categorizing messages."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    TOOL = "tool"
    STEP = "step"
    RESULT = "result"


@dataclass
class LogEntry:
    """A single log entry."""
    timestamp: float
    level: LogLevel
    message: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp,
            "level": self.level.value,
            "message": self.message,
            "metadata": self.metadata
        }


class LogStreamer:
    """Thread-safe log streamer that buffers logs and supports SSE streaming.

    Usage:
        # Create a streamer for a task
        streamer = LogStreamer(task_id="abc123")

        # Log messages from agents/runners
        streamer.log("Starting agent...", LogLevel.INFO)
        streamer.log("Calling tool: websearch", LogLevel.TOOL)

        # Get all logs (for polling)
        logs = streamer.get_logs()

        # Subscribe to new logs (for SSE)
        async for log in streamer.subscribe():
            yield log
    """

    # Global registry of active streamers by task_id
    _streamers: Dict[str, "LogStreamer"] = {}
    _lock = threading.RLock()  # Reentrant lock to avoid deadlock in create_or_get -> __init__

    def __init__(self, task_id: str, max_logs: int = 1000, console_output: bool = True):
        """Initialize a new LogStreamer.

        Args:
            task_id: Unique identifier for this task/session
            max_logs: Maximum number of logs to keep in buffer
            console_output: Whether to also print logs to console
        """
        self.task_id = task_id
        self.max_logs = max_logs
        self.console_output = console_output
        self._logs: deque = deque(maxlen=max_logs)
        self._subscribers: List[asyncio.Queue] = []
        self._lock = threading.Lock()
        self._closed = False

        # Import colorama for colored console output
        try:
            from colorama import Fore, Style
            self._colors = {
                LogLevel.DEBUG: Fore.BLUE,
                LogLevel.INFO: Fore.BLUE,
                LogLevel.WARNING: Fore.YELLOW,
                LogLevel.ERROR: Fore.RED,
                LogLevel.SUCCESS: Fore.GREEN,
                LogLevel.TOOL: Fore.MAGENTA,
                LogLevel.STEP: Fore.CYAN,
                LogLevel.RESULT: Fore.LIGHTGREEN_EX,
            }
            self._reset = Style.RESET_ALL
        except ImportError:
            self._colors = {}
            self._reset = ""

        # Register this streamer
        with LogStreamer._lock:
            LogStreamer._streamers[task_id] = self

    @classmethod
    def get(cls, task_id: str) -> Optional["LogStreamer"]:
        """Get an existing LogStreamer by task_id."""
        with cls._lock:
            return cls._streamers.get(task_id)

    @classmethod
    def create_or_get(cls, task_id: str, **kwargs) -> "LogStreamer":
        """Get an existing LogStreamer or create a new one."""
        with cls._lock:
            if task_id in cls._streamers:
                return cls._streamers[task_id]
            streamer = cls(task_id, **kwargs)
            return streamer

    def log(self, message: str, level: LogLevel = LogLevel.INFO, **metadata):
        """Add a log entry.

        Args:
            message: The log message
            level: Log level (INFO, ERROR, etc.)
            **metadata: Additional metadata to attach to the log
        """
        if self._closed:
            return

        entry = LogEntry(
            timestamp=time.time(),
            level=level,
            message=message,
            metadata=metadata
        )

        with self._lock:
            self._logs.append(entry)

            # Notify all subscribers
            for queue in self._subscribers:
                try:
                    queue.put_nowait(entry)
                except asyncio.QueueFull:
                    pass  # Drop if queue is full

        # Console output
        if self.console_output:
            level_prefix = {
                LogLevel.DEBUG: "[DEBUG]",
                LogLevel.INFO: "[INFO]",
                LogLevel.WARNING: "[WARNING]",
                LogLevel.ERROR: "[ERROR]",
                LogLevel.SUCCESS: "[SUCCESS]",
                LogLevel.TOOL: "[TOOL]",
                LogLevel.STEP: "[STEP]",
                LogLevel.RESULT: "[RESULT]",
            }.get(level, "[LOG]")
            color = self._colors.get(level, "")
            print(f"{color}{level_prefix} {message}{self._reset}")

    def info(self, message: str, **metadata):
        """Log an info message."""
        self.log(message, LogLevel.INFO, **metadata)

    def error(self, message: str, **metadata):
        """Log an error message."""
        self.log(message, LogLevel.ERROR, **metadata)

    def warning(self, message: str, **metadata):
        """Log a warning message."""
        self.log(message, LogLevel.WARNING, **metadata)

    def success(self, message: str, **metadata):
        """Log a success message."""
        self.log(message, LogLevel.SUCCESS, **metadata)

    def tool(self, message: str, **metadata):
        """Log a tool call message."""
        self.log(message, LogLevel.TOOL, **metadata)

    def step(self, message: str, **metadata):
        """Log a step message."""
        self.log(message, LogLevel.STEP, **metadata)

    def result(self, message: str, **metadata):
        """Log a result message."""
        self.log(message, LogLevel.RESULT, **metadata)

    def get_logs(self, since: float = 0) -> List[dict]:
        """Get all logs, optionally filtered by timestamp.

        Args:
            since: Only return logs after this timestamp

        Returns:
            List of log entries as dictionaries
        """
        with self._lock:
            logs = [entry.to_dict() for entry in self._logs if entry.timestamp > since]
        return logs

    async def subscribe(self) -> asyncio.Queue:
        """Subscribe to new log entries.

        Returns:
            An asyncio Queue that will receive new LogEntry objects
        """
        queue = asyncio.Queue(maxsize=100)
        with self._lock:
            self._subscribers.append(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue):
        """Unsubscribe from log entries."""
        with self._lock:
            if queue in self._subscribers:
                self._subscribers.remove(queue)

    def close(self):
        """Close the streamer and clean up."""
        self._closed = True
        with self._lock:
            # Notify subscribers that stream is closing
            for queue in self._subscribers:
                try:
                    queue.put_nowait(None)  # None signals end of stream
                except asyncio.QueueFull:
                    pass
            self._subscribers.clear()

        # Unregister
        with LogStreamer._lock:
            if self.task_id in LogStreamer._streamers:
                del LogStreamer._streamers[self.task_id]


class ConsoleLogger:
    """A simple logger that only prints to console (for CLI mode).

    This provides the same interface as LogStreamer but without
    the streaming/buffering overhead. Uses colored output matching the UI panel.
    """

    def __init__(self, task_id: str = "cli"):
        self.task_id = task_id
        # Import colorama for colored console output
        try:
            from colorama import Fore, Style
            self._colors = {
                LogLevel.DEBUG: Fore.BLUE,
                LogLevel.INFO: Fore.BLUE,
                LogLevel.WARNING: Fore.YELLOW,
                LogLevel.ERROR: Fore.RED,
                LogLevel.SUCCESS: Fore.GREEN,
                LogLevel.TOOL: Fore.MAGENTA,
                LogLevel.STEP: Fore.CYAN,
                LogLevel.RESULT: Fore.LIGHTGREEN_EX,
            }
            self._reset = Style.RESET_ALL
        except ImportError:
            self._colors = {}
            self._reset = ""

    def log(self, message: str, level: LogLevel = LogLevel.INFO, **metadata):
        level_prefix = {
            LogLevel.DEBUG: "[DEBUG]",
            LogLevel.INFO: "[INFO]",
            LogLevel.WARNING: "[WARNING]",
            LogLevel.ERROR: "[ERROR]",
            LogLevel.SUCCESS: "[SUCCESS]",
            LogLevel.TOOL: "[TOOL]",
            LogLevel.STEP: "[STEP]",
            LogLevel.RESULT: "[RESULT]",
        }.get(level, "[LOG]")
        color = self._colors.get(level, "")
        print(f"{color}{level_prefix} {message}{self._reset}")

    def info(self, message: str, **metadata):
        self.log(message, LogLevel.INFO, **metadata)

    def error(self, message: str, **metadata):
        self.log(message, LogLevel.ERROR, **metadata)

    def warning(self, message: str, **metadata):
        self.log(message, LogLevel.WARNING, **metadata)

    def success(self, message: str, **metadata):
        self.log(message, LogLevel.SUCCESS, **metadata)

    def tool(self, message: str, **metadata):
        self.log(message, LogLevel.TOOL, **metadata)

    def step(self, message: str, **metadata):
        self.log(message, LogLevel.STEP, **metadata)

    def result(self, message: str, **metadata):
        self.log(message, LogLevel.RESULT, **metadata)

    def get_logs(self, since: float = 0) -> List[dict]:
        return []

    def close(self):
        pass


# Type alias for logger interface
Logger = LogStreamer | ConsoleLogger


def create_logger(task_id: str, streaming: bool = True, console_output: bool = None) -> Logger:
    """Factory function to create the appropriate logger.

    Args:
        task_id: Unique identifier for the task
        streaming: If True, create a LogStreamer; if False, create a ConsoleLogger
        console_output: Whether to also print to console. Defaults to False for streaming, True for CLI.

    Returns:
        A logger instance
    """
    if streaming:
        # Default: no console output for streaming (UI mode)
        if console_output is None:
            console_output = False
        return LogStreamer.create_or_get(task_id, console_output=console_output)
    else:
        return ConsoleLogger(task_id)

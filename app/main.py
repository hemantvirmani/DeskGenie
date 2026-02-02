"""
DeskGenie - Desktop AI Agent

Copyright (c) 2026 Hemant Virmani. All rights reserved.

Licensed under the MIT License. See LICENSE file in the project root.

This is a hobbyist open-source project for educational purposes.
The software performs file system operations that may modify or delete files.
ALWAYS BACKUP IMPORTANT FILES BEFORE USING THIS SOFTWARE.

The authors are not responsible for any data loss or damages that may occur.
"""

import sys
import time
from pathlib import Path

# Add project root to path for direct script execution
_project_root = Path(__file__).parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import argparse
import warnings
import logging
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Tuple
from colorama import init

# Initialize colorama for Windows compatibility
init(autoreset=True)

# Suppress asyncio event loop cleanup warnings (common on HF Spaces and Python 3.13+)
warnings.filterwarnings('ignore', message='.*Invalid file descriptor.*')
warnings.filterwarnings('ignore', category=ResourceWarning)
logging.getLogger('asyncio').setLevel(logging.ERROR)

# Suppress the BaseEventLoop.__del__ AttributeError on shutdown (Python 3.13 issue)
import atexit
import gc
@atexit.register
def _cleanup():
    gc.collect()

# Import configuration
from app import config

# Import benchmark runner
from runners.question_runner import run_gaia_questions

# Import logger utilities
from utils.log_streamer import set_global_logger, ConsoleLogger

# Import log strings
from resources.log_strings import (
    CLIMessages as CLI,
    LogSeparators as LS
)

# --- Run Modes ---
class RunMode(Enum):
    UI = "ui"   # Web UI mode (FastAPI + React)
    CLI = "cli" # Command-line test mode


@dataclass
class AppOptions:
    """Options parsed from command-line arguments."""
    run_mode: RunMode
    test_query: Optional[str] = None  # For --testq
    test_filter: Optional[Tuple[int, ...]] = None  # For --test/--testall
    error: Optional[str] = None  # Parsing error message


def run_single_query(query: str) -> str:
    """Run a single query through the agent (same path as UI chat).

    Args:
        query: The question or command to execute

    Returns:
        str: The agent's response
    """
    from agents.agents import MyGAIAAgents
    from utils.langfuse_tracking import track_session

    print(CLI.QUERY_HEADER)
    print(CLI.QUERY_PREFIX.format(query=query))
    print(CLI.QUERY_SEPARATOR)

    start_time = time.time()

    with track_session("CLI_Query", {
        "agent_type": config.ACTIVE_AGENT,
        "query_length": len(query),
        "mode": "cli_query"
    }):
        agent = MyGAIAAgents()
        result = agent(query, None)

    # Calculate runtime
    elapsed_time = time.time() - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)

    print(CLI.QUERY_SEPARATOR.rstrip() + "\n")
    print(CLI.COMPLETED_IN.format(minutes=minutes, seconds=seconds))
    print(CLI.RESPONSE_PREFIX.format(result=result))
    print(CLI.RESPONSE_SEPARATOR)

    return result


def _parse_cli_args() -> AppOptions:
    """Parse command-line arguments and return configuration.

    Returns:
        AppOptions: Parsed configuration with run mode and test parameters
    """
    parser = argparse.ArgumentParser(description="Run the agent application.")
    parser.add_argument(
        "--test", type=str, nargs='?', const='default',
        help="Run GAIA benchmark. Use '--test all' for all questions, '--test' for default filter, or '--test 2,4,6' for specific questions."
    )
    parser.add_argument(
        "--testq", type=str,
        help="Run a single query through the agent (same as UI chat). Example: --testq \"What is the capital of France?\""
    )
    args = parser.parse_args()

    # Handle --testq (single query mode)
    if args.testq:
        return AppOptions(
            run_mode=RunMode.CLI,
            test_query=args.testq
        )

    # Handle --test (GAIA benchmark mode)
    if args.test:
        test_filter = None
        if args.test == 'default':
            test_filter = config.DEFAULT_TEST_FILTER
        elif args.test.lower() == 'all':
            test_filter = None  # None means all questions
        else:
            try:
                # User provides 1-based indices, convert to 0-based
                test_filter = tuple(int(idx.strip()) - 1 for idx in args.test.split(','))
            except ValueError:
                return AppOptions(
                    run_mode=RunMode.CLI,
                    error=f"Invalid test indices '{args.test}'. Use 'all', or comma-separated question numbers (e.g., 1,2,3)"
                )

        return AppOptions(
            run_mode=RunMode.CLI,
            test_filter=test_filter
        )

    # Default: UI mode
    return AppOptions(run_mode=RunMode.UI)


def main() -> None:
    """Main entry point for the application."""
    options = _parse_cli_args()

    # Handle parsing errors
    if options.error:
        print(CLI.ERROR_PREFIX.format(error=options.error))
        return

    print(CLI.SECTION_SEPARATOR)

    # Set global logger for CLI mode (UI mode sets it in genie_api.py)
    if options.run_mode == RunMode.CLI:
        set_global_logger(ConsoleLogger(task_id="cli"))

    # Execute based on run mode
    if options.run_mode == RunMode.UI:
        import uvicorn
        from app.genie_api import app

        print(CLI.LAUNCHING_UI)
        print(CLI.BACKEND_API)
        print(CLI.FRONTEND_PRODUCTION)
        print(CLI.DEV_INSTRUCTIONS)

        uvicorn.run(app, host="0.0.0.0", port=8000)

    elif options.test_query:
        # Single query mode (--testq)
        run_single_query(options.test_query)

    else: # GAIA benchmark mode (--test or --testall)
        filter_desc = len(options.test_filter) if options.test_filter else 'ALL'
        print(CLI.RUNNING_BENCHMARK.format(count=filter_desc))

        # Results are streamed via logger, function returns None
        run_gaia_questions(filter=options.test_filter)


if __name__ == "__main__":
    main()

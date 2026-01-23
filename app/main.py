import argparse
import warnings
import logging
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Tuple
from colorama import init

# Initialize colorama for Windows compatibility
init(autoreset=True)

# Suppress asyncio event loop cleanup warnings (common on HF Spaces)
warnings.filterwarnings('ignore', message='.*Invalid file descriptor.*')
logging.getLogger('asyncio').setLevel(logging.ERROR)

# Import configuration
from app import config

# Import benchmark runner
from runners.question_runner import run_gaia_questions

# --- Run Modes ---
class RunMode(Enum):
    UI = "ui"   # Web UI mode (FastAPI + React)
    CLI = "cli" # Command-line test mode


@dataclass
class AppOptions:
    """Options parsed from command-line arguments."""
    run_mode: RunMode
    active_agent: Optional[str] = None
    test_query: Optional[str] = None  # For --testq
    test_filter: Optional[Tuple[int, ...]] = None  # For --test/--testall
    error: Optional[str] = None  # Parsing error message


def run_single_query(query: str, active_agent: str = None) -> str:
    """Run a single query through the agent (same path as UI chat).

    Args:
        query: The question or command to execute
        active_agent: Optional agent type to use

    Returns:
        str: The agent's response
    """
    from agents.agents import MyGAIAAgents
    from utils.langfuse_tracking import track_session

    print(f"\n{'=' * 60}")
    print(f"Query: {query}")
    print(f"{'=' * 60}\n")

    with track_session("CLI_Query", {
        "agent_type": active_agent or config.ACTIVE_AGENT,
        "query_length": len(query),
        "mode": "cli_query"
    }):
        agent = MyGAIAAgents(active_agent=active_agent)
        result = agent(query, None)

    print(f"\n{'=' * 60}")
    print("Response:")
    print(f"{'=' * 60}")
    print(result)
    print(f"{'=' * 60}\n")

    return result


def _parse_cli_args() -> AppOptions:
    """Parse command-line arguments and return configuration.

    Returns:
        AppOptions: Parsed configuration with run mode, agent, and test parameters
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
    parser.add_argument(
        "--agent", type=str, choices=['langgraph', 'reactlangg'],
        help="Agent to use. Options: langgraph, reactlangg. Default: uses config.ACTIVE_AGENT"
    )
    args = parser.parse_args()

    # Map agent name to config constant
    agent_mapping = {
        'langgraph': config.AGENT_LANGGRAPH,
        'reactlangg': config.AGENT_REACT_LANGGRAPH,
    }

    # Parse agent
    active_agent = config.AGENT_REACT_LANGGRAPH  # Default agent
    if args.agent:
        active_agent = agent_mapping.get(args.agent.lower())
        if not active_agent:
            return AppOptions(
                run_mode=RunMode.CLI,
                error=f"Unknown agent '{args.agent}'. Valid options: langgraph, reactlangg"
            )

    # Handle --testq (single query mode)
    if args.testq:
        return AppOptions(
            run_mode=RunMode.CLI,
            active_agent=active_agent,
            test_query=args.testq
        )

    # Handle --test (GAIA benchmark mode)
    if args.test:
        test_filter = None
        if args.test == 'default':
            test_filter = config.DEFAULT_TEST_FILTER
        elif args.test.lower() == 'all':
            test_filter = None  # None means all questions
        else: #we will parse specific indices
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
            active_agent=active_agent,
            test_filter=test_filter
        )

    # Default: UI mode
    return AppOptions(
        run_mode=RunMode.UI,
        active_agent=active_agent
    )


def main() -> None:
    """Main entry point for the application."""
    options = _parse_cli_args()

    # Handle parsing errors
    if options.error:
        print(f"Error: {options.error}")
        return

    # Print agent info if specified
    if options.active_agent:
        print(f"[CLI] Using agent: {options.active_agent}")

    print(f"{'-' * (60 + len(' App Starting '))}\n")

    # Execute based on run mode
    if options.run_mode == RunMode.UI:
        import uvicorn
        from app.genie_api import app

        print("Launching DeskGenie Web UI...")
        print("  Backend API: http://localhost:8000")
        print("  Frontend:    http://localhost:8000 (production) or http://localhost:5173 (dev)")
        print("\nFor development, run 'cd frontend && npm run dev' in a separate terminal.")

        uvicorn.run(app, host="0.0.0.0", port=8000)

    elif options.test_query:
        # Single query mode (--testq)
        run_single_query(options.test_query, active_agent=options.active_agent)

    else:
        # GAIA benchmark mode (--test or --testall)
        filter_desc = len(options.test_filter) if options.test_filter else 'ALL'
        print(f"Running GAIA benchmark on {filter_desc} questions...")

        # Results are streamed via logger, function returns None
        run_gaia_questions(filter=options.test_filter, active_agent=options.active_agent)


if __name__ == "__main__":
    main()

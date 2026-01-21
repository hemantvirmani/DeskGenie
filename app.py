import os
import argparse
import pandas as pd
import json
import time
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
import config

# Import scoring function for answer verification
from scorer import question_scorer

# Import utilities
from result_formatter import ResultFormatter
from agent_runner import AgentRunner
from validators import InputValidator, ValidationError
from langfuse_tracking import track_session

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


def load_questions(file_path: str = config.QUESTIONS_FILE) -> list:
    """Load questions from local JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        questions = json.load(f)
        print(f"[INFO] Loaded {len(questions)} questions from {file_path}")
        return questions


def _load_ground_truth(file_path: str = config.METADATA_FILE) -> dict:
    """Load ground truth data indexed by task_id.

    Args:
        file_path: Path to the metadata file

    Returns:
        dict: Mapping of task_id -> {"question": str, "answer": str}
    """
    truth_mapping = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                task_id = data.get("task_id")
                question = data.get("Question")
                answer = data.get("Final answer")
                if task_id and answer:
                    truth_mapping[task_id] = {
                        "question": question,
                        "answer": answer
                    }
    except Exception as e:
        print(f"Error loading ground truth: {e}")
    return truth_mapping

def _verify_answers(results: list, log_output: list, runtime: tuple = None) -> None:
    """Verify answers against ground truth using the official GAIA scorer.

    Args:
        results: List of tuples (task_id, question_text, answer)
        log_output: List to append verification results to
        runtime: Optional tuple of (minutes, seconds) for total runtime
    """
    ground_truth = _load_ground_truth()
    log_output.append("\n=== Verification Results ===")

    correct_count = 0
    total_count = 0

    for task_id, question_text, answer in results:
        if task_id in ground_truth:
            truth_data = ground_truth[task_id]
            correct_answer = truth_data["answer"]

            # Use the official GAIA question_scorer for comparison
            # This handles numbers, lists, and strings with proper normalization
            is_correct = question_scorer(str(answer), str(correct_answer))

            if is_correct:
                correct_count += 1
            total_count += 1

            log_output.append(f"Task ID: {task_id}")
            log_output.append(f"Question: {question_text[:config.ERROR_MESSAGE_LENGTH]}...")
            log_output.append(f"Expected: {correct_answer}")
            log_output.append(f"Got: {answer}")
            log_output.append(f"Match: {'✓ Correct' if is_correct else '✗ Incorrect'}\n")
        else:
            log_output.append(f"Task ID: {task_id}")
            log_output.append(f"Question: {question_text[:config.ERROR_MESSAGE_LENGTH]}...")
            log_output.append(f"No ground truth found.\n")

    # Add summary statistics
    if total_count > 0:
        accuracy = (correct_count / total_count) * 100
        log_output.append("=" * config.SEPARATOR_WIDTH)
        log_output.append(f"SUMMARY: {correct_count}/{total_count} correct ({accuracy:.1f}%)")
        if runtime:
            minutes, seconds = runtime
            log_output.append(f"Runtime: {minutes}m {seconds}s")
        log_output.append("=" * config.SEPARATOR_WIDTH)

def run_gaia_questions(filter=None, active_agent=None) -> pd.DataFrame:
    """Run GAIA benchmark questions.

    Args:
        filter: Optional tuple/list of question indices to test (e.g., (4, 7, 15)).
                If None, processes all questions.
        active_agent: Optional agent type to use (e.g., "LangGraph", "ReActLangGraph", "LLamaIndex").
                      If None, uses config.ACTIVE_AGENT.

    Returns:
        pd.DataFrame: Results and verification output
    """
    start_time = time.time()
    logs_for_display = []
    logs_for_display.append("=== Processing Example Questions One by One ===")

    # Fetch questions (OFFLINE for testing)
    try:
        questions_data = load_questions()
    except Exception as e:
        return pd.DataFrame([f"Error loading questions: {e}"])

    # Validate questions data
    try:
        questions_data = InputValidator.validate_questions_data(questions_data)
    except ValidationError as e:
        return pd.DataFrame([f"Invalid questions data: {e}"])

    # Validate and apply filter
    try:
        filter = InputValidator.validate_filter_indices(filter, len(questions_data))
    except ValidationError as e:
        return pd.DataFrame([f"Invalid filter: {e}"])

    # Apply filter or use all questions
    if filter is not None:
        questions_to_process = [questions_data[i] for i in filter]
        logs_for_display.append(f"Testing {len(questions_to_process)} selected questions (indices: {filter})")
    else:
        questions_to_process = questions_data
        logs_for_display.append(f"Testing all {len(questions_to_process)} questions")

    # Run agent on selected questions with specified agent type (with Langfuse session tracking)
    with track_session("Test_Run", {
        "agent": active_agent or config.ACTIVE_AGENT,
        "question_count": len(questions_to_process),
        "filter": str(filter) if filter else "all",
        "mode": "test"
    }):
        results = AgentRunner(active_agent=active_agent).run_on_questions(questions_to_process)

    if results is None:
        return pd.DataFrame(["Error initializing agent."])

    logs_for_display.append("\n=== Completed Example Questions ===")

    # Calculate runtime
    elapsed_time = time.time() - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)

    _verify_answers(results, logs_for_display, runtime=(minutes, seconds))
    return pd.DataFrame(logs_for_display)


def run_single_query(query: str, active_agent: str = None) -> str:
    """Run a single query through the agent (same path as UI chat).

    Args:
        query: The question or command to execute
        active_agent: Optional agent type to use

    Returns:
        str: The agent's response
    """
    from agents import MyGAIAAgents
    from langfuse_tracking import track_session

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
        help="Run GAIA benchmark on selected questions. Optionally provide comma-separated indices (e.g., --test 2,4,6)."
    )
    parser.add_argument(
        "--testall", action="store_true",
        help="Run GAIA benchmark on all questions."
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

    # Handle --test or --testall (GAIA benchmark mode)
    if args.test or args.testall:
        test_filter = None
        if args.test:
            if args.test == 'default':
                test_filter = config.DEFAULT_TEST_FILTER
            else:
                try:
                    test_filter = tuple(int(idx.strip()) for idx in args.test.split(','))
                except ValueError:
                    return AppOptions(
                        run_mode=RunMode.CLI,
                        error=f"Invalid test indices '{args.test}'. Must be comma-separated integers (e.g., 2,4,6)"
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
        from genie_api import app

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

        result = run_gaia_questions(filter=options.test_filter, active_agent=options.active_agent)

        if isinstance(result, pd.DataFrame):
            ResultFormatter.print_dataframe(result)
        else:
            print(result)


if __name__ == "__main__":
    main()

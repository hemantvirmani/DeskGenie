import os
import argparse
import requests
import pandas as pd
import json
import time
import warnings
import logging
from enum import Enum
from colorama import init

# Initialize colorama for Windows compatibility
init(autoreset=True)

# Suppress asyncio event loop cleanup warnings (common on HF Spaces)
warnings.filterwarnings('ignore', message='.*Invalid file descriptor.*')
logging.getLogger('asyncio').setLevel(logging.ERROR)

# Import configuration
import config

# Agent-related code is imported via agent_runner module
# Import Gradio UI creation function
from gradioapp import create_ui
# Import scoring function for answer verification
from scorer import question_scorer

# Import new utilities
from question_loader import QuestionLoader
from result_formatter import ResultFormatter
from agent_runner import AgentRunner
from validators import InputValidator, ValidationError
from utils import retry_with_backoff
from langfuse_tracking import track_session

# --- Run Modes ---
class RunMode(Enum):
    UI = "ui"   # Gradio UI mode
    CLI = "cli" # Command-line test mode


@retry_with_backoff(max_retries=3, initial_delay=2.0)
def _submit_to_server(submit_url: str, submission_data: dict) -> dict:
    """Internal function to submit to server (with retries)."""
    response = requests.post(submit_url, json=submission_data, timeout=config.SUBMIT_TIMEOUT)
    response.raise_for_status()
    return response.json()

def submit_and_score(username: str, results: list) -> str:
    """
    Submit answers to the GAIA scoring server and return status message.

    Args:
        username: Hugging Face username for submission
        results: List of tuples (task_id, question_text, answer)

    Returns:
        str: Status message (success or error details)
    """
    # Validate username
    try:
        username = InputValidator.validate_username(username)
    except ValidationError as e:
        error_msg = f"Invalid username: {e}"
        print(error_msg)
        return error_msg

    # Format results for API submission
    answers_payload = ResultFormatter.format_for_api(results)

    if not answers_payload:
        error_msg = "No answers to submit."
        print(error_msg)
        return error_msg

    space_id = config.SPACE_ID
    submit_url = f"{config.DEFAULT_API_URL}/submit"
    agent_code = f"https://huggingface.co/spaces/{space_id}/tree/main"

    # Prepare submission data
    submission_data = {
        "username": username,
        "agent_code": agent_code,
        "answers": answers_payload
    }

    print(f"\n{'=' * config.SEPARATOR_WIDTH}")
    print(f"Submitting {len(answers_payload)} answers for user '{username}'...")
    print(f"{'=' * config.SEPARATOR_WIDTH}\n")

    # Submit to server
    print(f"Submitting to: {submit_url}")
    try:
        result_data = _submit_to_server(submit_url, submission_data)

        final_status = (
            f"Submission Successful!\n"
            f"User: {result_data.get('username')}\n"
            f"Overall Score: {result_data.get('score', 'N/A')}% "
            f"({result_data.get('correct_count', '?')}/{result_data.get('total_attempted', '?')} correct)\n"
            f"Message: {result_data.get('message', 'No message received.')}"
        )
        print("Submission successful.")
        return final_status

    except requests.exceptions.HTTPError as e:
        error_detail = f"Server responded with status {e.response.status_code}."
        try:
            error_json = e.response.json()
            error_detail += f" Detail: {error_json.get('detail', e.response.text)}"
        except requests.exceptions.JSONDecodeError:
            error_detail += f" Response: {e.response.text[:500]}"
        status_message = f"Submission Failed: {error_detail}"
        print(status_message)
        return status_message

    except requests.exceptions.Timeout:
        status_message = "Submission Failed: The request timed out."
        print(status_message)
        return status_message

    except requests.exceptions.RequestException as e:
        status_message = f"Submission Failed: Network error - {e}"
        print(status_message)
        return status_message

    except Exception as e:
        status_message = f"An unexpected error occurred during submission: {e}"
        print(status_message)
        return status_message


def run_and_submit_all(username: str, active_agent: str = None) -> tuple:
    """
    Fetches all questions, runs the GAIA agent on them, submits all answers,
    and displays the results.

    Args:
        username: Hugging Face username for submission
        active_agent: The agent type to use (default: config.AGENT_LANGGRAPH)

    Returns:
        tuple: (status_message: str, results_df: pd.DataFrame)
    """
    # Fetch questions from API (always online for submission)
    try:
        questions_data = QuestionLoader().get_questions(test_mode=False)
    except Exception as e:
        return f"Error loading questions: {e}", None

    # Validate questions data
    try:
        questions_data = InputValidator.validate_questions_data(questions_data)
    except ValidationError as e:
        return f"Invalid questions data: {e}", None

    # Run agent on all questions with specified agent type (with Langfuse session tracking)
    with track_session("Submit_All", {
        "agent": active_agent or config.ACTIVE_AGENT,
        "username": username,
        "question_count": len(questions_data),
        "mode": "submission"
    }):
        results = AgentRunner(active_agent=active_agent).run_on_questions(questions_data)

    if results is None:
        return "Error initializing agent.", None

    # Submit answers and get score (formatting happens inside submit_and_score)
    status_message = submit_and_score(username, results)

    # Format results for UI display
    results_for_display = ResultFormatter.format_for_display(results)
    results_df = pd.DataFrame(results_for_display)
    return status_message, results_df

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

def run_test_code(filter=None, active_agent=None) -> pd.DataFrame:
    """Run test code on selected questions.

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
        questions_data = QuestionLoader().get_questions(test_mode=True)
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


def main() -> None:
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Run the agent application.")
    parser.add_argument("--test", type=str, nargs='?', const='default', help="Run local tests on selected questions and exit. Optionally provide comma-separated question indices (e.g., --test 2,4,6). If no indices provided, uses default test questions.")
    parser.add_argument("--testall", action="store_true", help="Run local tests on all questions and exit.")
    parser.add_argument("--agent", type=str, choices=['langgraph', 'reactlangg', 'llamaindex'], help="Agent to use in CLI mode (case-insensitive). Options: langgraph, react langgraph, llamaindex. Default: uses config.ACTIVE_AGENT")
    args = parser.parse_args()

    # Map agent name to config constant (case-insensitive)
    agent_mapping = {
        'langgraph': config.AGENT_LANGGRAPH,
        'reactlangg': config.AGENT_REACT_LANGGRAPH,
        'llamaindex': config.AGENT_LLAMAINDEX,
    }

    active_agent = None
    if args.agent:
        agent_key = args.agent.lower()
        active_agent = agent_mapping.get(agent_key)
        if not active_agent:
            print(f"Error: Unknown agent '{args.agent}'. Valid options: langgraph, react, llamaindex")
            return
        print(f"[CLI] Using agent: {active_agent}")

    print(f"\n{'-' * 30} App Starting {'-' * 30}")

    # Determine run mode
    run_mode = RunMode.CLI if (args.test or args.testall) else RunMode.UI

    # Print environment info only in UI mode
    if run_mode == RunMode.UI:
        space_host = config.SPACE_HOST
        space_id = config.SPACE_ID

        if space_host:
            print(f"[OK] SPACE_HOST found: {space_host}")
            print(f"   Runtime URL should be: https://{space_host}.hf.space")
        else:
            print("[INFO] SPACE_HOST environment variable not found (running locally?).")

        if space_id:
            print(f"[OK] SPACE_ID found: {space_id}")
            print(f"   Repo URL: https://huggingface.co/spaces/{space_id}")
            print(f"   Repo Tree URL: https://huggingface.co/spaces/{space_id}/tree/main")
        else:
            print("[INFO] SPACE_ID environment variable not found (running locally?). Repo URL cannot be determined.")

    print(f"{'-' * (60 + len(' App Starting '))}\n")

    # Execute based on run mode
    if run_mode == RunMode.UI:
        print("Launching Gradio Interface for Basic Agent Evaluation...")
        grTestApp = create_ui(run_and_submit_all, run_test_code)
        grTestApp.launch()

    else:  # RunMode.CLI
        # Determine test filter based on which CLI flag was used
        if args.test:
            # Check if custom indices were provided
            if args.test == 'default':
                # No indices provided, use default
                test_filter = config.DEFAULT_TEST_FILTER
            else:
                # Parse comma-separated indices
                try:
                    test_filter = tuple(int(idx.strip()) for idx in args.test.split(','))
                except ValueError:
                    print(f"Error: Invalid test indices '{args.test}'. Must be comma-separated integers (e.g., 2,4,6)")
                    return
        else:  # args.testall
            test_filter = None  # Test all questions

        print(f"Running test code on {len(test_filter) if test_filter else 'ALL'} questions (CLI mode)...")
        result = run_test_code(filter=test_filter, active_agent=active_agent)

        # Print results
        if isinstance(result, pd.DataFrame):
            ResultFormatter.print_dataframe(result)
        else:
            print(result)


if __name__ == "__main__":
    main()

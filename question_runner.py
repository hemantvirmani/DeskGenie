"""Question runner for GAIA benchmark tests.

This module handles loading and running benchmark questions,
verifying answers against ground truth, and formatting results.
"""

import json
import time

import config
from scorer import question_scorer
from agent_runner import AgentRunner
from validators import InputValidator, ValidationError
from langfuse_tracking import track_session
from log_streamer import ConsoleLogger, Logger


def load_questions(file_path: str = config.QUESTIONS_FILE, logger: Logger = None) -> list:
    """Load questions from local JSON file."""
    logger = logger or ConsoleLogger()
    with open(file_path, 'r', encoding='utf-8') as f:
        questions = json.load(f)
        logger.info(f"Loaded {len(questions)} questions from {file_path}")
        return questions


def _load_ground_truth(file_path: str = config.METADATA_FILE, logger: Logger = None) -> dict:
    """Load ground truth data indexed by task_id.

    Args:
        file_path: Path to the metadata file
        logger: Optional logger

    Returns:
        dict: Mapping of task_id -> {"question": str, "answer": str}
    """
    logger = logger or ConsoleLogger()
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
        logger.error(f"Error loading ground truth: {e}")
    return truth_mapping


def _verify_answers(results: list, logger: Logger = None, runtime: tuple = None) -> None:
    """Verify answers against ground truth using the official GAIA scorer.

    Args:
        results: List of tuples (task_id, question_text, answer)
        logger: Optional logger for streaming
        runtime: Optional tuple of (minutes, seconds) for total runtime
    """
    logger = logger or ConsoleLogger()
    ground_truth = _load_ground_truth(logger=logger)
    logger.info("=== Verification Results ===")

    correct_count = 0
    total_count = 0

    for task_id, question_text, answer in results:
        q_num = total_count + 1  # 1-based question number
        if task_id in ground_truth:
            truth_data = ground_truth[task_id]
            correct_answer = truth_data["answer"]

            # Use the official GAIA question_scorer for comparison
            # This handles numbers, lists, and strings with proper normalization
            is_correct = question_scorer(str(answer), str(correct_answer))

            if is_correct:
                correct_count += 1
            total_count += 1

            # Stream to logger (q_num is 1-based index)
            if is_correct:
                logger.success(f"Q{q_num}: ✓ Correct")
            else:
                logger.error(f"Q{q_num}: ✗ Incorrect (expected: {correct_answer}, got: {answer})")
        else:
            logger.warning(f"Q{q_num}: No ground truth found")

    # Add summary statistics
    if total_count > 0:
        accuracy = (correct_count / total_count) * 100
        summary = f"SUMMARY: {correct_count}/{total_count} correct ({accuracy:.1f}%)"
        logger.result(summary)
        if runtime:
            minutes, seconds = runtime
            runtime_str = f"Runtime: {minutes}m {seconds}s"
            logger.info(runtime_str)


def run_gaia_questions(filter=None, active_agent=None, logger: Logger = None):
    """Run GAIA benchmark questions.

    Args:
        filter: Optional tuple/list of question indices to test (e.g., (4, 7, 15)).
                If None, processes all questions.
        active_agent: Optional agent type to use (e.g., "LangGraph", "ReActLangGraph", "LLamaIndex").
                      If None, uses config.ACTIVE_AGENT.
        logger: Optional logger for streaming logs to UI. If None, uses ConsoleLogger.

    Returns:
        None (results are streamed via logger)
    """
    logger = logger or ConsoleLogger()

    start_time = time.time()
    logger.info("=== Processing Example Questions One by One ===")

    # Fetch questions (OFFLINE for testing)
    try:
        questions_data = load_questions(logger=logger)
    except Exception as e:
        logger.error(f"Error loading questions: {e}")
        return

    # Validate questions data
    try:
        questions_data = InputValidator.validate_questions_data(questions_data)
    except ValidationError as e:
        logger.error(f"Invalid questions data: {e}")
        return

    # Validate and apply filter
    try:
        filter = InputValidator.validate_filter_indices(filter, len(questions_data))
    except ValidationError as e:
        logger.error(f"Invalid filter: {e}")
        return

    # Apply filter or use all questions
    if filter is not None:
        questions_to_process = [questions_data[i] for i in filter]
        logger.info(f"Testing {len(questions_to_process)} selected questions (indices: {filter})")
    else:
        questions_to_process = questions_data
        logger.info(f"Testing all {len(questions_to_process)} questions")

    # Run agent on selected questions with specified agent type (with Langfuse session tracking)
    with track_session("Test_Run", {
        "agent": active_agent or config.ACTIVE_AGENT,
        "question_count": len(questions_to_process),
        "filter": str(filter) if filter else "all",
        "mode": "test"
    }):
        results = AgentRunner(active_agent=active_agent, logger=logger).run_on_questions(questions_to_process)

    if results is None:
        logger.error("Error initializing agent.")
        return

    logger.success("=== Completed Example Questions ===")

    # Calculate runtime
    elapsed_time = time.time() - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)

    _verify_answers(results, logger=logger, runtime=(minutes, seconds))

"""Question runner for GAIA benchmark tests.

This module handles loading and running benchmark questions,
verifying answers against ground truth, and formatting results.
"""

import json
import threading
import time

from app import config
from utils.generous_scorer import score_with_details
from runners.agent_runner import AgentRunner
from utils.validators import InputValidator, ValidationError
from utils.langfuse_tracking import track_session
from utils.log_streamer import ConsoleLogger, Logger
from resources.ui_strings import QuestionRunnerStrings as S


def load_questions(file_path: str = config.QUESTIONS_FILE, logger: Logger = None) -> list:
    """Load questions from local JSON file."""
    logger = logger or ConsoleLogger()
    with open(file_path, 'r', encoding='utf-8') as f:
        questions = json.load(f)
        logger.info(S.LOADED_QUESTIONS.format(count=len(questions), file_path=file_path))
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
        logger.error(S.ERROR_LOADING_GROUND_TRUTH.format(error=e))
    return truth_mapping


def _verify_answers(
    results: list,
    logger: Logger = None,
    runtime: tuple = None,
    stop_event: threading.Event | None = None
) -> dict:
    """Verify answers against ground truth using the official GAIA scorer.

    Args:
        results: List of tuples (task_id, question_text, answer)
        logger: Optional logger for streaming
        runtime: Optional tuple of (minutes, seconds) for total runtime

    Returns:
        dict: Summary stats with keys 'correct', 'total', 'accuracy'
    """
    logger = logger or ConsoleLogger()
    ground_truth = _load_ground_truth(logger=logger)
    logger.info(S.VERIFICATION_HEADER)
    logger.info(S.VERIFYING_RESULTS.format(results=len(results), truth=len(ground_truth)))

    correct_count = 0
    total_count = 0

    for idx, (task_id, _question_text, answer) in enumerate(results):
        if stop_event and stop_event.is_set():
            logger.warning(S.SHUTDOWN_STOPPING_VERIFICATION)
            break
        q_num = idx + 1  # 1-based question number
        if task_id in ground_truth:
            truth_data = ground_truth[task_id]
            correct_answer = truth_data["answer"]

            # Use generous scorer with fallback matching strategies
            result = score_with_details(str(answer), str(correct_answer))
            is_correct = result["correct"]
            match_type = result["match_type"]

            if is_correct:
                correct_count += 1
            total_count += 1

            # Stream to logger (q_num is 1-based index)
            if is_correct:
                logger.question(S.QUESTION_CORRECT.format(num=q_num, match_type=match_type, expected=correct_answer, actual=answer))
            else:
                logger.error(S.QUESTION_INCORRECT.format(num=q_num, expected=correct_answer, actual=answer))
        else:
            logger.warning(S.QUESTION_NO_TRUTH.format(num=q_num))

    # Add summary statistics
    accuracy = (correct_count / total_count) * 100 if total_count > 0 else 0
    if total_count > 0:
        logger.result(S.SUMMARY.format(correct=correct_count, total=total_count, accuracy=accuracy))
        if runtime:
            minutes, seconds = runtime
            logger.info(S.RUNTIME.format(minutes=minutes, seconds=seconds))

    return {"correct": correct_count, "total": total_count, "accuracy": accuracy}


def run_gaia_questions(filter=None, logger: Logger = None, stop_event: threading.Event | None = None) -> dict:
    """Run GAIA benchmark questions.

    Args:
        filter: Optional tuple/list of question indices to test (e.g., (4, 7, 15)).
                If None, processes all questions.
        logger: Optional logger for streaming logs to UI. If None, uses ConsoleLogger.

    Returns:
        dict: Summary stats with keys 'correct', 'total', 'accuracy', or None on error
    """
    logger = logger or ConsoleLogger()

    start_time = time.time()
    logger.info(S.PROCESSING_HEADER)

    # Fetch questions (OFFLINE for testing)
    try:
        questions_data = load_questions(logger=logger)
    except Exception as e:
        logger.error(S.ERROR_LOADING_QUESTIONS.format(error=e))
        return None

    # Validate questions data
    try:
        questions_data = InputValidator.validate_questions_data(questions_data)
    except ValidationError as e:
        logger.error(S.INVALID_QUESTIONS_DATA.format(error=e))
        return None

    # Validate and apply filter
    try:
        filter = InputValidator.validate_filter_indices(filter, len(questions_data))
    except ValidationError as e:
        logger.error(S.INVALID_FILTER.format(error=e))
        return None

    # Apply filter or use all questions
    if filter is not None:
        questions_to_process = [questions_data[i] for i in filter]
        logger.info(S.RUNNING_SELECTED.format(count=len(questions_to_process)))
    else:
        questions_to_process = questions_data
        logger.info(S.RUNNING_ALL.format(count=len(questions_to_process)))

    # Run agent on selected questions (with Langfuse session tracking)
    with track_session("Run", {
        "agent": config.ACTIVE_AGENT,
        "question_count": len(questions_to_process),
        "filter": str(filter) if filter else "all",
        "mode": "test"
    }):
        results = AgentRunner(logger=logger).run_on_questions(questions_to_process, stop_event=stop_event)

    if results is None:
        logger.error(S.ERROR_INITIALIZING_AGENT)
        return None

    logger.success(S.COMPLETED_HEADER)

    # Calculate runtime
    elapsed_time = time.time() - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)

    return _verify_answers(results, logger=logger, runtime=(minutes, seconds), stop_event=stop_event)

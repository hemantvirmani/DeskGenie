"""Agent execution functionality for running questions through the GAIA agent."""

import threading
from typing import Optional, Tuple, List, Dict
from agents.agents import MyGAIAAgents
from app.config import *
from utils.langfuse_tracking import track_question_processing
from utils.log_streamer import ConsoleLogger, Logger
from resources.ui_strings import AgentStrings as S


class AgentRunner:
    """Handles agent execution and question processing.
    """

    def __init__(self, logger: Logger = None):
        """Initialize the AgentRunner.

        Args:
            logger: Optional logger for streaming logs to UI. If None, uses ConsoleLogger.
        """
        self.agent = None
        self.logger = logger or ConsoleLogger()

    def _initialize_agent(self) -> bool:
        """Initialize the agent. Returns True if successful."""
        try:
            self.agent = MyGAIAAgents(logger=self.logger)
            return True
        except Exception as e:
            self.logger.error(S.ERROR_INSTANTIATING_AGENT.format(error=e))
            return False

    def run_on_questions(self, questions_data: List[Dict], stop_event: threading.Event | None = None) -> Optional[List[Tuple]]:
        """Run agent on a list of questions and return results."""
        if not self._initialize_agent():
            return None

        results = []
        total = len(questions_data)
        self.logger.info(S.RUNNING_AGENT_ON_QUESTIONS.format(total=total))

        for idx, item in enumerate(questions_data, 1):
            if stop_event and stop_event.is_set():
                self.logger.warning(S.SHUTDOWN_STOPPING_AGENT_LOOP)
                break

            task_id = item.get("task_id")
            question_text = item.get("question")
            file_name = item.get("file_name")

            if not task_id or question_text is None:
                self.logger.warning(S.SKIPPING_MISSING_DATA.format(item=item))
                continue

            try:
                self.logger.question(S.LINE_SEPARATOR)
                self.logger.question(S.QUESTION_TEXT.format(num=idx, question=question_text))
                # Track individual question processing with Langfuse
                with track_question_processing(task_id, question_text) as span:
                    answer = self.agent(question_text, file_name=file_name)
                    if span:
                        span.update(output={"answer": str(answer)[:300]})

                truncated_answer = f"{answer[:100]}..." if len(str(answer)) > 100 else answer
                self.logger.result(S.TASK_RESULT.format(task_id=task_id, answer=truncated_answer))
                results.append((task_id, question_text, answer))
            except Exception as e:
                self.logger.error(S.EXCEPTION_RUNNING_AGENT.format(task_id=task_id, error=e))
                error_msg = f"AGENT ERROR: {str(e)[:config.ERROR_MESSAGE_LENGTH]}"
                results.append((task_id, question_text, error_msg))

        return results

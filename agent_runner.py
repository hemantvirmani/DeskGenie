"""Agent execution functionality for running questions through the GAIA agent."""

from typing import Optional, Tuple, List, Dict
from agents import MyGAIAAgents
import config
from langfuse_tracking import track_question_processing
from log_streamer import ConsoleLogger, Logger


class AgentRunner:
    """Handles agent execution and question processing.
    """

    def __init__(self, active_agent: str = None, logger: Logger = None):
        """Initialize the AgentRunner.

        Args:
            active_agent: The agent type to use. If None, uses config.ACTIVE_AGENT.
            logger: Optional logger for streaming logs to UI. If None, uses ConsoleLogger.
        """
        self.agent = None
        self.active_agent = active_agent
        self.logger = logger or ConsoleLogger()

    def _initialize_agent(self) -> bool:
        """Initialize the agent. Returns True if successful."""
        try:
            self.agent = MyGAIAAgents(active_agent=self.active_agent, logger=self.logger)
            return True
        except Exception as e:
            self.logger.error(f"Error instantiating agent: {e}")
            return False

    def run_on_questions(self, questions_data: List[Dict]) -> Optional[List[Tuple]]:
        """Run agent on a list of questions and return results."""
        if not self._initialize_agent():
            return None

        results = []
        total = len(questions_data)
        self.logger.info(f"Running agent on {total} questions...")

        for idx, item in enumerate(questions_data, 1):
            task_id = item.get("task_id")
            question_text = item.get("question")
            file_name = item.get("file_name")

            if not task_id or question_text is None:
                self.logger.warning(f"Skipping item with missing task_id or question: {item}")
                continue

            try:
                # Track individual question processing with Langfuse
                with track_question_processing(task_id, question_text) as span:
                    answer = self.agent(question_text, file_name=file_name)
                    if span:
                        span.update(output={"answer": str(answer)[:300]})

                self.logger.result(f"Task {task_id}: {answer[:100]}{'...' if len(str(answer)) > 100 else ''}")
                self.logger.info(f"Question: {question_text}")
                results.append((task_id, question_text, answer))
            except Exception as e:
                self.logger.error(f"Exception running agent on task {task_id}: {e}")
                error_msg = f"AGENT ERROR: {str(e)[:config.ERROR_MESSAGE_LENGTH]}"
                results.append((task_id, question_text, error_msg))

        return results

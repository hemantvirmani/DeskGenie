"""Agent execution functionality for running questions through the GAIA agent."""

from typing import Optional, Tuple, List, Dict
from colorama import Fore, Style
from agents import MyGAIAAgents
import config
from langfuse_tracking import track_question_processing


class AgentRunner:
    """Handles agent execution and question processing.
    """

    def __init__(self, active_agent: str = None):
        """Initialize the AgentRunner.

        Args:
            active_agent: The agent type to use. If None, uses config.ACTIVE_AGENT.
        """
        self.agent = None
        self.active_agent = active_agent

    def _initialize_agent(self) -> bool:
        """Initialize the agent. Returns True if successful."""
        try:
            self.agent = MyGAIAAgents(active_agent=self.active_agent)
            return True
        except Exception as e:
            print(f"{Fore.RED}Error instantiating agent: {e}{Style.RESET_ALL}")
            return False

    def run_on_questions(self, questions_data: List[Dict]) -> Optional[List[Tuple]]:
        """Run agent on a list of questions and return results."""
        if not self._initialize_agent():
            return None

        results = []
        total = len(questions_data)
        print(f"{Fore.CYAN}Running agent on {total} questions...{Style.RESET_ALL}")

        for idx, item in enumerate(questions_data, 1):
            task_id = item.get("task_id")
            question_text = item.get("question")
            file_name = item.get("file_name")

            if not task_id or question_text is None:
                print(f"\n{Fore.YELLOW}Skipping item with missing task_id or question: {item}{Style.RESET_ALL}\n")
                continue

            print(f"\n{'#' * config.SEPARATOR_WIDTH}")
            print(f"{Fore.CYAN}Processing Question {idx}/{total} - Task ID: {task_id}{Style.RESET_ALL}")
            print(f"{'#' * config.SEPARATOR_WIDTH}")

            try:
                # Track individual question processing with Langfuse
                with track_question_processing(task_id, question_text) as span:
                    answer = self.agent(question_text, file_name=file_name)
                    if span:
                        span.update(output={"answer": str(answer)[:300]})

                print(f"\n{Fore.GREEN}[RESULT] Task ID: {task_id}{Style.RESET_ALL}")
                print(f"Question: {question_text[:config.QUESTION_PREVIEW_LENGTH]}{'...' if len(question_text) > config.QUESTION_PREVIEW_LENGTH else ''}")
                print(f"Answer: {answer}")
                results.append((task_id, question_text, answer))
            except Exception as e:
                print(f"{Fore.RED}[ERROR] Exception running agent on task {task_id}: {e}{Style.RESET_ALL}")
                error_msg = f"AGENT ERROR: {str(e)[:config.ERROR_MESSAGE_LENGTH]}"
                results.append((task_id, question_text, error_msg))

        return results

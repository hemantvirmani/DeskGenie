"""Agent wrapper module."""

from utils.log_streamer import ConsoleLogger, Logger
from agents.langgraphagent import LangGraphAgent

# All agents are imported lazily to avoid loading unnecessary dependencies
# and suppress warnings from unused agent implementations


class MyGAIAAgents:
    """Wrapper class for the LangGraph agent."""

    def __init__(self, logger: Logger = None):
        """Initialize the wrapper with the LangGraph agent.

        Args:
            logger: Optional logger for streaming logs to UI. If None, uses ConsoleLogger.
        """
        # Use ConsoleLogger if no logger provided (CLI mode)
        self.logger = logger or ConsoleLogger()
        self.agent = LangGraphAgent(logger=self.logger)

    def __call__(self, question: str, file_name: str = None) -> str:
        """Invoke the active agent with the given question.

        Args:
            question: The question to answer
            file_name: Optional file name if the question references a file

        Returns:
            The agent's answer as a string
        """
        return self.agent(question, file_name)

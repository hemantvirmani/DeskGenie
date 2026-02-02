"""Agent wrapper module."""

from app import config
from utils.log_streamer import ConsoleLogger, Logger

# All agents are imported lazily to avoid loading unnecessary dependencies
# and suppress warnings from unused agent implementations


class MyGAIAAgents:
    """Wrapper class to manage multiple agent implementations.

    This class provides a unified interface for different agent types.
    The active agent is determined by config.ACTIVE_AGENT.
    """

    def __init__(self, logger: Logger = None):
        """Initialize the wrapper with the active agent.

        Args:
            logger: Optional logger for streaming logs to UI. If None, uses ConsoleLogger.
        """
        # Use ConsoleLogger if no logger provided (CLI mode)
        self.logger = logger or ConsoleLogger()

        if config.ACTIVE_AGENT == config.AGENT_LANGGRAPH:
            from agents.langgraphagent import LangGraphAgent
            self.agent = LangGraphAgent(logger=self.logger)
        elif config.ACTIVE_AGENT == config.AGENT_REACT_LANGGRAPH:
            from agents.reactlanggraphagent import ReActLangGraphAgent
            self.agent = ReActLangGraphAgent(logger=self.logger)
        else:
            # Default to ReActLangGraph if unknown agent type
            from agents.reactlanggraphagent import ReActLangGraphAgent
            self.agent = ReActLangGraphAgent(logger=self.logger)

    def __call__(self, question: str, file_name: str = None) -> str:
        """Invoke the active agent with the given question.

        Args:
            question: The question to answer
            file_name: Optional file name if the question references a file

        Returns:
            The agent's answer as a string
        """
        return self.agent(question, file_name)

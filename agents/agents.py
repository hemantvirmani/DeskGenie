"""Agent wrapper module for DeskGenie."""

import config
from log_streamer import ConsoleLogger, Logger

# All agents are imported lazily to avoid loading unnecessary dependencies
# and suppress warnings from unused agent implementations


class MyGAIAAgents:
    """Wrapper class to manage multiple agent implementations.

    This class provides a unified interface for different agent types.
    The active agent is determined by the ACTIVE_AGENT configuration or constructor parameter.
    """

    def __init__(self, active_agent: str = None, logger: Logger = None):
        """Initialize the wrapper with the active agent.

        Args:
            active_agent: The agent type to use. If None, uses config.ACTIVE_AGENT.
                         Valid values: config.AGENT_LANGGRAPH, config.AGENT_REACT_LANGGRAPH
            logger: Optional logger for streaming logs to UI. If None, uses ConsoleLogger.
        """
        if active_agent is None:
            active_agent = config.ACTIVE_AGENT

        # Use ConsoleLogger if no logger provided (CLI mode)
        self.logger = logger or ConsoleLogger()

        if active_agent == config.AGENT_LANGGRAPH:
            from langgraphagent import LangGraphAgent
            self.agent = LangGraphAgent(logger=self.logger)
        elif active_agent == config.AGENT_REACT_LANGGRAPH:
            from reactlanggraphagent import ReActLangGraphAgent
            self.agent = ReActLangGraphAgent(logger=self.logger)
        else:
            # Default to ReActLangGraph if unknown agent type
            print(f"[WARNING] Unknown agent type '{active_agent}', defaulting to {config.AGENT_REACT_LANGGRAPH}")
            from reactlanggraphagent import ReActLangGraphAgent
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

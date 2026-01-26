import os
import logging
import warnings
import time

# Suppress TensorFlow/Keras warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
logging.getLogger('tensorflow').setLevel(logging.ERROR)
warnings.filterwarnings('ignore', module='tensorflow')
warnings.filterwarnings('ignore', module='tf_keras')

from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_ollama import ChatOllama

from tools.custom_tools import get_custom_tools_list
from resources.system_prompt import SYSTEM_PROMPT
from utils.utils import cleanup_answer, extract_text_from_content
from app import config
from utils.langfuse_tracking import track_agent_execution
from utils.log_streamer import ConsoleLogger, Logger
from resources.ui_strings import AgentStrings as S
from resources.state_strings import AgentReturns as AR, ModelProviders as MP
from resources.error_strings import AgentErrors as AE

from tools.desktop_tools import get_desktop_tools_list

# Suppress BeautifulSoup GuessedAtParserWarning
try:
    from bs4 import GuessedAtParserWarning
    warnings.filterwarnings('ignore', category=GuessedAtParserWarning)
except ImportError:
    pass


class ReActLangGraphAgent:
    """
    ReAct agent implementation using LangGraph's create_react_agent function.

    This agent uses the ReAct (Reasoning + Acting) pattern where the agent
    reasons about what to do and then acts by calling tools iteratively.
    Built on top of LangGraph's prebuilt ReAct agent.
    """

    def __init__(self, logger: Logger = None):
        """Initialize the ReAct agent.

        Args:
            logger: Optional logger for streaming logs to UI. If None, uses ConsoleLogger.
        """
        self.logger = logger or ConsoleLogger()

        # Validate API keys
        if not os.getenv("GOOGLE_API_KEY"):
            self.logger.warning(S.GOOGLE_API_KEY_NOT_FOUND)

        self.tools = self._get_all_tools()
        self.llm = self._create_llm_client()
        self.agent_graph = self._build_agent()

    def _get_all_tools(self) -> list:
        """Get all available tools."""
        tools = get_custom_tools_list()

        # Add desktop tools
        desktop_tools = get_desktop_tools_list()
        tools.extend(desktop_tools)

        return tools

    def _create_llm_client(self, model_provider: str = config.DEFAULT_MODEL_PROVIDER):
        """Create and return the LLM client with tools bound based on the model provider."""

        if model_provider == MP.GOOGLE:

            return ChatGoogleGenerativeAI(
                model=config.ACTIVE_AGENT_LLM_MODEL,
                temperature=0,
                api_key=config.GOOGLE_API_KEY,
                timeout=60  # Add timeout to prevent hanging
                ).bind_tools(self.tools)

        elif model_provider == MP.HUGGINGFACE:

            llmObject = HuggingFaceEndpoint(
                repo_id=config.HUGGINGFACE_LLAMA_MODEL,
                task="text-generation",
                max_new_tokens=512,
                temperature=0.7,
                do_sample=False,
                repetition_penalty=1.03,
                huggingfacehub_api_token=config.HUGGINGFACE_API_KEY
            )
            return ChatHuggingFace(llm=llmObject).bind_tools(self.tools)

        elif model_provider == MP.OLLAMA:
            # Ollama runs locally - ensure Ollama server is running with the model pulled
            # e.g., `ollama serve` then `ollama pull qwen2.5:14b-instruct`
            return ChatOllama(
                model=config.OLLAMA_QWEN_MODEL,
                base_url=config.OLLAMA_BASE_URL,
                temperature=0,
                num_ctx=4096,  # Context window size
            ).bind_tools(self.tools)


    def _build_agent(self):
        """Build and return the ReAct agent graph using LangGraph's create_react_agent."""

        # LangGraph's create_react_agent returns a compiled graph
        # It automatically handles the ReAct loop with tools
        agent_graph = create_react_agent(
            model=self.llm,
            tools=self.tools,
            prompt=SYSTEM_PROMPT  # System prompt is added via the prompt parameter
        )

        return agent_graph

    @track_agent_execution("ReAct")
    def __call__(self, question: str, file_name: str = None) -> str:
        """
        Invoke the ReAct agent with the given question and return the final answer.

        Args:
            question: The question to answer
            file_name: Optional file name if the question references a file

        Returns:
            The agent's answer as a string
        """
        truncated_q = f"{question[:100]}..." if len(question) > 100 else question
        self.logger.step(S.REACT_STARTING.format(question=truncated_q))
        if file_name:
            self.logger.info(S.LANGGRAPH_FILE.format(file_name=file_name))

        try:
            # Build the question with file name if provided
            question_content = question
            if file_name:
                question_content += AR.FILE_REFERENCE_NOTE.format(file_name=file_name)

            # Invoke the agent graph with retry logic for 504 errors
            max_retries = config.MAX_RETRIES
            delay = config.INITIAL_RETRY_DELAY

            for attempt in range(max_retries + 1):
                try:
                    # LangGraph's create_react_agent expects messages as input
                    response = self.agent_graph.invoke(
                        {"messages": [HumanMessage(content=question_content)]},
                        config={"recursion_limit": 80}  # Match the recursion limit from LangGraphAgent
                    )
                    # Success - break out of retry loop
                    break
                except Exception as e:
                    error_msg = str(e)

                    # Check if this is a 504 DEADLINE_EXCEEDED error
                    if "504" in error_msg and "DEADLINE_EXCEEDED" in error_msg:
                        if attempt < max_retries:
                            self.logger.warning(S.RETRY_ATTEMPT.format(attempt=attempt + 1, max_retries=max_retries))
                            self.logger.info(S.RETRY_WAITING.format(delay=delay))
                            time.sleep(delay)
                            delay *= config.RETRY_BACKOFF_FACTOR
                            continue
                        else:
                            self.logger.error(S.RETRIES_EXHAUSTED.format(max_retries=max_retries))
                            self.logger.error(S.AGENT_INVOCATION_FAILED_RETRIES.format(error=e))
                            return AE.AGENT_FAILED_RETRIES.format(max_retries=max_retries, error=str(e)[:100])
                    else:
                        # Not a 504 error - fail immediately without retry
                        self.logger.error(S.AGENT_INVOCATION_FAILED.format(error=e))
                        return AE.AGENT_FAILED.format(error=str(e)[:100])

            # Extract the answer from the response
            # LangGraph's create_react_agent returns the last message in the messages list
            messages = response.get("messages", [])

            if not messages:
                self.logger.warning(S.REACT_NO_MESSAGES)
                return AE.NO_ANSWER

            # Get the last message (the agent's final response)
            last_message = messages[-1]

            # Extract content from the message
            if hasattr(last_message, 'content'):
                content = last_message.content
            else:
                content = str(last_message)

            # Use utility function to extract text from various content formats
            answer = extract_text_from_content(content)

            if not answer or answer is None:
                self.logger.warning(S.REACT_NULL_ANSWER)
                return AE.NO_ANSWER

            # Clean up the answer using utility function
            answer = cleanup_answer(answer)

            truncated_ans = f"{answer[:200]}..." if len(answer) > 200 else answer
            self.logger.result(S.FINAL_ANSWER.format(answer=truncated_ans))
            return answer

        except Exception as e:
            self.logger.error(S.AGENT_INVOCATION_FAILED.format(error=e))
            return AE.GENERIC.format(error=str(e)[:100])

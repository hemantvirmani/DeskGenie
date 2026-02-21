import os
import logging
import warnings
import re
import time

# Suppress TensorFlow/Keras warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
logging.getLogger('tensorflow').setLevel(logging.ERROR)
warnings.filterwarnings('ignore', module='tensorflow')
warnings.filterwarnings('ignore', module='tf_keras')

from typing import TypedDict, Optional, List, Annotated
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import tools_condition
from langgraph.prebuilt import ToolNode
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_ollama import ChatOllama

from tools.custom_tools import get_custom_tools_list
from resources.system_prompt import SYSTEM_PROMPT
from utils.utils import cleanup_answer, extract_text_from_content
from app import config

from tools.desktop_tools import get_desktop_tools_list
from utils.langfuse_tracking import track_agent_execution, track_llm_call
from utils.log_streamer import ConsoleLogger, Logger
from resources.ui_strings import AgentStrings as S
from resources.state_strings import StateKeys as SK, AgentReturns as AR, ModelProviders as MP
from resources.error_strings import AgentErrors as AE

# Suppress BeautifulSoup GuessedAtParserWarning
try:
    from bs4 import GuessedAtParserWarning
    warnings.filterwarnings('ignore', category=GuessedAtParserWarning)
except ImportError:
    pass


class AgentState(TypedDict):
    question: str
    messages: Annotated[list , add_messages]   # for LangGraph
    answer: str
    step_count: int  # Track number of iterations to prevent infinite loops
    file_name: str  # Optional file name for questions that reference files


class LangGraphAgent:

    def __init__(self, logger: Logger = None):
        """Initialize the LangGraph agent.

        Args:
            logger: Optional logger for streaming logs to UI. If None, uses ConsoleLogger.
        """
        self.logger = logger or ConsoleLogger()

        # Validate API keys
        if not os.getenv("GOOGLE_API_KEY"):
            self.logger.warning(S.GOOGLE_API_KEY_NOT_FOUND)

        self.tools = self._get_all_tools()
        self.llm_client_with_tools = self._create_llm_client()
        self.graph = self._build_graph()

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

    # Nodes
    def _init_questions(self, state: AgentState):
        """Initialize the messages in the state with system prompt and user question."""

        # Build the question message, including file name if available
        question_content = state[SK.QUESTION]
        if state.get(SK.FILE_NAME):
            question_content += AR.FILE_REFERENCE_NOTE.format(file_name=state[SK.FILE_NAME])

        return {
            SK.MESSAGES: [
                    SystemMessage(content=SYSTEM_PROMPT),
                    HumanMessage(content=question_content)
                    ],
            SK.STEP_COUNT: 0  # Initialize step counter
                }

    @track_llm_call(config.ACTIVE_AGENT_LLM_MODEL)
    def _assistant(self, state: AgentState):
        """Assistant node which calls the LLM with tools"""

        # Track and log current step
        current_step = state.get(SK.STEP_COUNT, 0) + 1
        self.logger.step(S.STEP_CALLING_LLM.format(step=current_step, count=len(state[SK.MESSAGES])))

        # Invoke LLM with tools enabled, with retry logic for 504 errors
        max_retries = config.MAX_RETRIES
        delay = config.INITIAL_RETRY_DELAY

        for attempt in range(max_retries + 1):
            try:
                response = self.llm_client_with_tools.invoke(state[SK.MESSAGES])
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
                        self.logger.error(S.LLM_INVOCATION_FAILED_RETRIES.format(error=e))
                        return {
                            SK.MESSAGES: [],
                            SK.ANSWER: AE.AGENT_FAILED_RETRIES.format(max_retries=max_retries, error=str(e)[:100]),
                            SK.STEP_COUNT: current_step
                        }
                else:
                    # Not a 504 error - fail immediately without retry
                    self.logger.error(S.LLM_INVOCATION_FAILED.format(error=e))
                    return {
                        SK.MESSAGES: [],
                        SK.ANSWER: AE.AGENT_FAILED.format(error=str(e)[:100]),
                        SK.STEP_COUNT: current_step
                    }

        # If no tool calls, set the final answer
        if not response.tool_calls:
            content = response.content

            # Handle case where content is a list (e.g. mixed content from Gemini)
            if isinstance(content, list):
                # Extract text from list of content parts
                text_parts = []
                for item in content:
                    if isinstance(item, dict) and 'text' in item:
                        text_parts.append(item['text'])
                    elif hasattr(item, 'text'):
                        text_parts.append(item.text)
                    else:
                        text_parts.append(str(item))
                content = " ".join(text_parts)
            elif isinstance(content, dict) and 'text' in content:
                # Handle single dict with 'text' field
                content = content['text']
            elif hasattr(content, 'text'):
                # Handle object with text attribute
                content = content.text
            else:
                # Fallback to string conversion
                content = str(content)

            # Clean up any remaining noise
            content = content.strip()

            return {
                SK.MESSAGES: [response],
                SK.ANSWER: content,
                SK.STEP_COUNT: current_step
            }

        return {
            SK.MESSAGES: [response],
            SK.STEP_COUNT: current_step
        }


    def _should_continue(self, state: AgentState):
        """Check if we should continue or stop based on step count and other conditions."""

        step_count = state.get(SK.STEP_COUNT, 0)

        # Stop if we've exceeded maximum steps
        if step_count >= 40:  # Increased from 25 to handle complex multi-step reasoning
            self.logger.warning(S.LANGGRAPH_MAX_STEPS)
            # Force a final answer if we don't have one
            if not state.get(SK.ANSWER):
                state[SK.ANSWER] = AE.MAX_ITERATIONS
            return END

        # Otherwise use the default tools_condition
        return tools_condition(state)


    def _build_graph(self):
        """Build and return the Compiled Graph for the agent."""

        graph = StateGraph(AgentState)

        # Build graph
        graph.add_node("init", self._init_questions)
        graph.add_node("assistant", self._assistant)
        graph.add_node("tools", ToolNode(self.tools))
        graph.add_edge(START, "init")
        graph.add_edge("init", "assistant")
        graph.add_conditional_edges(
            "assistant",
            # Use custom should_continue instead of tools_condition
            self._should_continue,
        )
        graph.add_edge("tools", "assistant")
        # Compile graph
        return graph.compile()

    @track_agent_execution("LangGraph")
    def __call__(self, question: str, file_name: str = None) -> str:
        """Invoke the agent graph with the given question and return the final answer.

        Args:
            question: The question to answer
            file_name: Optional file name if the question references a file
        """

        truncated_q = f"{question[:30]}..." if len(question) > 30 else question
        self.logger.step(S.LANGGRAPH_STARTING.format(question=truncated_q))
        if file_name:
            self.logger.info(S.LANGGRAPH_FILE.format(file_name=file_name))

        try:
            response = self.graph.invoke(
                {SK.QUESTION: question, SK.MESSAGES: [], SK.ANSWER: None, SK.STEP_COUNT: 0, SK.FILE_NAME: file_name or ""},
                config={"recursion_limit": 80}  # Must be >= 2x step limit (40 * 2 = 80)
            )

            answer = response.get(SK.ANSWER)
            if not answer or answer is None:
                self.logger.warning(S.LANGGRAPH_NULL_ANSWER)
                return AE.NO_ANSWER

            # Use utility function to extract text from various content formats
            answer = extract_text_from_content(answer)

            # Clean up the answer using utility function (includes stripping)
            answer = cleanup_answer(answer)

            truncated_ans = f"{answer[:200]}..." if len(answer) > 200 else answer
            self.logger.result(S.FINAL_ANSWER.format(answer=truncated_ans))
            return answer

        except Exception as e:
            self.logger.error(S.AGENT_INVOCATION_FAILED.format(error=e))
            return AE.GENERIC.format(error=str(e)[:100])

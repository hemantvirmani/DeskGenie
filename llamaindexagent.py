import os
import logging
import warnings
import time
import asyncio
import nest_asyncio

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# Suppress TensorFlow/Keras warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
logging.getLogger('tensorflow').setLevel(logging.ERROR)
warnings.filterwarnings('ignore', module='tensorflow')
warnings.filterwarnings('ignore', module='tf_keras')

# Suppress google.generativeai deprecation warning from llama_index
warnings.filterwarnings('ignore', message='.*google.generativeai.*deprecated.*', category=FutureWarning)
warnings.filterwarnings('ignore', module='google.generativeai')

# Suppress asyncio selector warnings that occur during event loop cleanup on some platforms
warnings.filterwarnings('ignore', message='.*Invalid file descriptor.*')
logging.getLogger('asyncio').setLevel(logging.ERROR)

from llama_index.core.agent import ReActAgent
from llama_index.llms.gemini import Gemini
from llama_index.core.tools import FunctionTool

from custom_tools import get_custom_tools_list
from system_prompt import SYSTEM_PROMPT
from utils import cleanup_answer, extract_text_from_content
import config
from langfuse_tracking import track_agent_execution

# Suppress BeautifulSoup GuessedAtParserWarning
try:
    from bs4 import GuessedAtParserWarning
    warnings.filterwarnings('ignore', category=GuessedAtParserWarning)
except ImportError:
    pass


class LlamaIndexAgent:
    """
    LlamaIndex agent implementation using ReActAgent.

    This agent uses LlamaIndex's ReAct agent pattern which integrates
    with various LLM providers and tools. It provides an alternative
    implementation to LangGraph-based agents.
    """

    def __init__(self):
        # Validate API keys
        if not os.getenv("GOOGLE_API_KEY"):
            print("WARNING: GOOGLE_API_KEY not found - analyze_youtube_video will fail")

        self.langchain_tools = get_custom_tools_list()
        self.llm = self._create_llm_client()
        self.tools = self._convert_tools_to_llamaindex()
        self.agent = self._build_agent()

    def _create_llm_client(self):
        """Create and return the LLM client for LlamaIndex."""
        api_key = os.getenv("GOOGLE_API_KEY")

        # Create Gemini LLM for LlamaIndex
        llm = Gemini(
            model=config.ACTIVE_AGENT_LLM_MODEL,
            api_key=api_key,
            temperature=config.GEMINI_TEMPERATURE,
            max_tokens=config.GEMINI_MAX_TOKENS,
        )

        return llm

    def _convert_tools_to_llamaindex(self) -> list[FunctionTool]:
        """Convert LangChain tools to LlamaIndex FunctionTool format."""
        llamaindex_tools = []

        for langchain_tool in self.langchain_tools:
            # Extract the function from LangChain tool
            tool_func = langchain_tool.func if hasattr(langchain_tool, 'func') else langchain_tool

            # Create LlamaIndex FunctionTool
            llamaindex_tool = FunctionTool.from_defaults(
                fn=tool_func,
                name=langchain_tool.name,
                description=langchain_tool.description,
            )

            llamaindex_tools.append(llamaindex_tool)

        return llamaindex_tools

    def _build_agent(self) -> ReActAgent:
        """Build and return the LlamaIndex ReAct agent."""

        # Create ReAct agent with tools and LLM
        agent = ReActAgent(
            tools=self.tools,
            llm=self.llm,
            verbose=True,
            max_iterations=40,  # Match the step limit from other agents
            system_prompt=SYSTEM_PROMPT,
        )

        return agent

    @track_agent_execution("LlamaIndex")
    def __call__(self, question: str, file_name: str = None) -> str:
        """
        Invoke the LlamaIndex agent with the given question and return the final answer.

        Args:
            question: The question to answer
            file_name: Optional file name if the question references a file

        Returns:
            The agent's answer as a string
        """
        print(f"\n{'='*60}")
        print(f"[LLAMAINDEX AGENT START] Question: {question}")
        if file_name:
            print(f"[FILE] {file_name}")
        print(f"{'='*60}")

        start_time = time.time()

        try:
            # Build the question with file name if provided
            question_content = question
            if file_name:
                question_content += f'\n\nNote: This question references a file: {file_name}'

            # Invoke the agent with retry logic for 504 errors
            max_retries = config.MAX_RETRIES
            delay = config.INITIAL_RETRY_DELAY

            for attempt in range(max_retries + 1):
                try:
                    # Create a dedicated async function to run the agent
                    async def run_agent_async():
                        # Pass max_iterations as a runtime parameter to the workflow
                        return await self.agent.run(question_content, max_iterations=40)

                    # Try different approaches to run the async function
                    try:
                        # Check if a loop is already running
                        loop = asyncio.get_running_loop()
                        # If we reach here, a loop is already running
                        # Use nest_asyncio's patched loop to run coroutine
                        response = loop.run_until_complete(run_agent_async())
                    except RuntimeError:
                        # No running loop, we can use asyncio.run directly
                        # But wrap in try-except to suppress cleanup errors
                        try:
                            response = asyncio.run(run_agent_async())
                        except ValueError as ve:
                            # Suppress "Invalid file descriptor" errors during cleanup
                            if "Invalid file descriptor" not in str(ve):
                                raise

                    # Success - break out of retry loop
                    break
                except Exception as e:
                    error_msg = str(e)

                    # Check if this is a 504 DEADLINE_EXCEEDED error
                    if "504" in error_msg and "DEADLINE_EXCEEDED" in error_msg:
                        if attempt < max_retries:
                            print(f"[RETRY] Attempt {attempt + 1}/{max_retries} failed with 504 DEADLINE_EXCEEDED")
                            print(f"[RETRY] Retrying in {delay:.1f} seconds...")
                            time.sleep(delay)
                            delay *= config.RETRY_BACKOFF_FACTOR
                            continue
                        else:
                            print(f"[RETRY] All {max_retries} retries exhausted for 504 error")
                            print(f"[ERROR] Agent invocation failed after retries: {e}")
                            return f"Error: Agent failed after {max_retries} retries - {str(e)[:100]}"
                    else:
                        # Not a 504 error - fail immediately without retry
                        print(f"[ERROR] Agent invocation failed: {e}")
                        return f"Error: Agent failed - {str(e)[:100]}"

            elapsed_time = time.time() - start_time
            print(f"[LLAMAINDEX AGENT COMPLETE] Time: {elapsed_time:.2f}s")
            print(f"{'='*60}\n")

            # Extract the answer from the response using utility function
            # This handles ChatMessage objects, dicts, lists, and strings
            answer = extract_text_from_content(response)

            if not answer or answer is None:
                print("[WARNING] Agent completed but returned Empty answer")
                return "Error: No answer generated"

            # LlamaIndex ReActAgent may wrap answers in verbose format
            # Check if the response starts with common verbose patterns and extract the core answer
            import re

            # Pattern 1: "Answer: X" or "Final Answer: X" from ReAct format
            react_answer_match = re.search(r'(?:Final\s+)?Answer:\s*(.+)', answer, re.IGNORECASE | re.DOTALL)
            if react_answer_match:
                extracted = react_answer_match.group(1).strip()
                print(f"[LLAMAINDEX] Extracted answer from ReAct format: '{extracted[:100]}...'")
                answer = extracted

            # Clean up the answer using utility function (includes stripping)
            answer = cleanup_answer(answer)

            print(f"[FINAL ANSWER] {answer}")
            return answer

        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"[LLAMAINDEX AGENT ERROR] Failed after {elapsed_time:.2f}s: {e}")
            print(f"{'='*60}\n")
            return f"Error: {str(e)[:100]}"

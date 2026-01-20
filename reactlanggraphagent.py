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


class ReActLangGraphAgent:
    """
    ReAct agent implementation using LangGraph's create_react_agent function.

    This agent uses the ReAct (Reasoning + Acting) pattern where the agent
    reasons about what to do and then acts by calling tools iteratively.
    Built on top of LangGraph's prebuilt ReAct agent.
    """

    def __init__(self):
        # Validate API keys
        if not os.getenv("GOOGLE_API_KEY"):
            print("WARNING: GOOGLE_API_KEY not found - analyze_youtube_video will fail")

        self.tools = get_custom_tools_list()
        self.llm = self._create_llm_client()
        self.agent_graph = self._build_agent()

    def _create_llm_client(self):
        """Create and return the LLM client."""
        apikey = os.getenv("GOOGLE_API_KEY")

        return ChatGoogleGenerativeAI(
            model=config.ACTIVE_AGENT_LLM_MODEL,
            temperature=config.GEMINI_TEMPERATURE,
            api_key=apikey,
            timeout=60
        )

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
        print(f"\n{'='*60}")
        print(f"[REACT AGENT START] Question: {question}")
        if file_name:
            print(f"[FILE] {file_name}")
        print(f"{'='*60}")

        start_time = time.time()

        try:
            # Build the question with file name if provided
            question_content = question
            if file_name:
                question_content += f'\n\nNote: This question references a file: {file_name}'

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
            print(f"[REACT AGENT COMPLETE] Time: {elapsed_time:.2f}s")
            print(f"{'='*60}\n")

            # Extract the answer from the response
            # LangGraph's create_react_agent returns the last message in the messages list
            messages = response.get("messages", [])

            if not messages:
                print("[WARNING] Agent completed but returned no messages")
                return "Error: No answer generated"

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
                print("[WARNING] Agent completed but returned None as answer")
                return "Error: No answer generated"

            # Clean up the answer using utility function
            answer = cleanup_answer(answer)

            print(f"[FINAL ANSWER] {answer}")
            return answer

        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"[REACT AGENT ERROR] Failed after {elapsed_time:.2f}s: {e}")
            print(f"{'='*60}\n")
            return f"Error: {str(e)[:100]}"

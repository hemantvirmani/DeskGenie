"""LLM-based answer scorer using Ollama as a judge.

Uses a local Ollama LLM to evaluate whether a model answer is semantically
equivalent to the expected ground truth. Falls back to generous_question_scorer
if Ollama is unavailable or times out.
"""

from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

from app import config
from utils.generous_scorer import generous_question_scorer

_JUDGE_SYSTEM = (
    "You are an answer evaluation judge. "
    "Determine if a model's answer is semantically equivalent to the expected answer. "
    "Consider numerical equivalence, abbreviations, alternate orderings, and paraphrasing. "
    "Reply with exactly one word: CORRECT or INCORRECT."
)

_llm_client: ChatOllama | None = None


def _get_llm_client() -> ChatOllama:
    """Return the shared Ollama client, creating it on first call."""
    global _llm_client
    if _llm_client is None:
        _llm_client = ChatOllama(
            model=config.OLLAMA_QWEN_MODEL,
            base_url=config.OLLAMA_BASE_URL,
            temperature=0,
        )
    return _llm_client


def llm_question_scorer(
    ground_truth: str,
    model_answer: str,
) -> tuple[bool, str]:
    """Score an answer using an Ollama LLM as judge.

    Sends both answers to the LLM and asks it to judge semantic equivalence.
    Falls back to generous_question_scorer if Ollama is unavailable.

    Args:
        ground_truth: The expected correct answer
        model_answer: The model's answer string

    Returns:
        tuple: (is_correct: bool, match_type: str)
            match_type is "llm_correct", "llm_incorrect",
            or "fallback_<type>" when Ollama is unavailable.
    """
    if model_answer is None:
        model_answer = "None"

    try:
        client = _get_llm_client()
        messages = [
            SystemMessage(content=_JUDGE_SYSTEM),
            HumanMessage(content=f"Expected answer: {ground_truth}\nModel answer: {model_answer}"),
        ]
        response = client.invoke(messages)
        verdict = str(response.content).strip().upper()

        if verdict.startswith("CORRECT"):
            return True, "llm_correct"
        return False, "llm_incorrect"

    except Exception:
        # Ollama unavailable or timed out — fall back to generous scorer
        is_correct, match_type = generous_question_scorer(model_answer, ground_truth)
        return is_correct, f"fallback_{match_type}"

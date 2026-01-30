"""Generous answer scorer with fallback matching strategies.

This module wraps the official GAIA scorer and adds more lenient matching
when the strict match fails. Useful for handling verbose LLM responses.
"""

import re
from external.scorer import question_scorer, normalize_str, normalize_number_str


def extract_numbers(text: str) -> list[float]:
    """Extract all numbers from a text string.

    Handles integers, decimals, and numbers with commas/currency symbols.
    """
    # Pattern matches numbers with optional $ prefix and commas
    pattern = r'[$]?[\d,]+\.?\d*'
    matches = re.findall(pattern, text)

    numbers = []
    for match in matches:
        try:
            num = normalize_number_str(match)
            if num != float("inf"):
                numbers.append(num)
        except (ValueError, TypeError):
            continue
    return numbers


def extract_final_answer(text: str) -> str:
    """Try to extract a final answer from verbose text.

    Looks for patterns like "is X", "are X", "= X", ": X" at the end.
    """
    text = text.strip()

    # Try to find answer after common patterns
    patterns = [
        r'(?:is|are|was|were|equals?|=|:)\s*["\']?([^"\'.,!?]+)["\']?[.,!?]?\s*$',
        r'(?:answer|result|total|value)(?:\s+is)?\s*[:\s]+["\']?([^"\'.,!?]+)["\']?[.,!?]?\s*$',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    # If text is short, return as-is
    if len(text.split()) <= 3:
        return text

    return text


def generous_question_scorer(
    model_answer: str,
    ground_truth: str,
) -> tuple[bool, str]:
    """Score an answer with generous matching strategies.

    First tries the official GAIA scorer, then falls back to more
    lenient matching strategies if strict match fails.

    Args:
        model_answer: The model's answer string
        ground_truth: The expected correct answer

    Returns:
        tuple: (is_correct: bool, match_type: str)
            match_type can be: "exact", "number_extract", "contains", "no_match"
    """
    if model_answer is None:
        model_answer = "None"

    # Strategy 1: Try official GAIA scorer first (exact match)
    if question_scorer(model_answer, ground_truth):
        return True, "exact"

    # Strategy 2: For numeric ground truth, extract numbers from response
    try:
        gt_num = float(ground_truth)
        extracted_nums = extract_numbers(model_answer)
        if gt_num in extracted_nums:
            return True, "number_extract"
        # Also check for integer equivalence (3.0 == 3)
        if any(int(n) == int(gt_num) for n in extracted_nums if n == int(n)):
            return True, "number_extract"
    except (ValueError, TypeError):
        pass

    # Strategy 3: Check if ground truth is contained in normalized answer
    norm_answer = normalize_str(model_answer)
    norm_truth = normalize_str(ground_truth)

    if norm_truth in norm_answer:
        return True, "contains"

    # Strategy 4: Try extracting final answer from verbose response
    extracted = extract_final_answer(model_answer)
    if question_scorer(extracted, ground_truth):
        return True, "extracted"

    # Strategy 5: Word-level containment (all words in truth appear in answer)
    truth_words = set(norm_truth.split()) if norm_truth else set()
    answer_words = set(norm_answer.split()) if norm_answer else set()
    if truth_words and truth_words.issubset(answer_words):
        return True, "words_match"

    # Strategy 6: Unordered comma-separated list comparison
    if ',' in ground_truth and ',' in model_answer:
        truth_items = {normalize_str(item.strip()) for item in ground_truth.split(',')}
        answer_items = {normalize_str(item.strip()) for item in model_answer.split(',')}
        if truth_items and truth_items == answer_items:
            return True, "unordered_list"

    # Strategy 7: Common abbreviation expansion
    abbreviations = {
        'st.': 'saint',
        'st ': 'saint ',
        'mt.': 'mount',
        'mt ': 'mount ',
        'dr.': 'doctor',
        'dr ': 'doctor ',
        'mr.': 'mister',
        'mrs.': 'missus',
        'ft.': 'fort',
        'ft ': 'fort ',
    }

    def expand_abbreviations(text: str) -> str:
        result = text.lower()
        for abbrev, full in abbreviations.items():
            result = result.replace(abbrev, full)
        return result

    expanded_answer = expand_abbreviations(model_answer)
    expanded_truth = expand_abbreviations(ground_truth)
    if normalize_str(expanded_answer) == normalize_str(expanded_truth):
        return True, "abbreviation_match"

    return False, "no_match"


def score_with_details(
    model_answer: str,
    ground_truth: str,
    strict: bool = False
) -> dict:
    """Score an answer and return detailed results.

    Args:
        model_answer: The model's answer string
        ground_truth: The expected correct answer
        strict: If True, only use official GAIA scorer

    Returns:
        dict with keys:
            - correct: bool
            - match_type: str ("exact", "number_extract", "contains", "no_match")
            - strict_correct: bool (result from official scorer only)
    """
    strict_correct = question_scorer(str(model_answer), str(ground_truth))

    if strict:
        return {
            "correct": strict_correct,
            "match_type": "exact" if strict_correct else "no_match",
            "strict_correct": strict_correct
        }

    is_correct, match_type = generous_question_scorer(
        str(model_answer),
        str(ground_truth)
    )

    return {
        "correct": is_correct,
        "match_type": match_type,
        "strict_correct": strict_correct
    }

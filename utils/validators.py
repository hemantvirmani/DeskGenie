"""Input validation utilities."""

import re
from typing import List, Optional, Tuple


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class InputValidator:
    """Validates user inputs."""

    @staticmethod
    def validate_username(username: str) -> str:
        """
        Validate username for submission.

        Args:
            username: The username to validate

        Returns:
            Cleaned username

        Raises:
            ValidationError: If username is invalid
        """
        if not username or not username.strip():
            raise ValidationError("Username cannot be empty")

        cleaned = username.strip()

        if len(cleaned) < 3:
            raise ValidationError("Username must be at least 3 characters")

        if len(cleaned) > 50:
            raise ValidationError("Username must be less than 50 characters")

        # Allow alphanumeric, underscore, hyphen
        if not re.match(r'^[a-zA-Z0-9_-]+$', cleaned):
            raise ValidationError("Username can only contain letters, numbers, underscore, and hyphen")

        return cleaned

    @staticmethod
    def validate_filter_indices(filter_list: Optional[Tuple], max_index: int) -> Optional[List[int]]:
        """
        Validate filter indices for test questions.

        Args:
            filter_list: Tuple/list of indices or None
            max_index: Maximum valid index (exclusive)

        Returns:
            Validated list of indices or None

        Raises:
            ValidationError: If indices are invalid
        """
        if filter_list is None:
            return None

        if not isinstance(filter_list, (list, tuple)):
            raise ValidationError("Filter must be a list or tuple")

        if not filter_list:
            raise ValidationError("Filter cannot be empty (use None for all questions)")

        validated = []
        for idx in filter_list:
            if not isinstance(idx, int):
                raise ValidationError(f"Filter index must be integer, got {type(idx)}")

            if idx < 0:
                raise ValidationError(f"Filter index cannot be negative: {idx}")

            if idx >= max_index:
                raise ValidationError(f"Filter index {idx} out of range (max: {max_index - 1})")

            validated.append(idx)

        return validated

    @staticmethod
    def validate_questions_data(questions_data: any) -> List[dict]:
        """
        Validate questions data structure.

        Args:
            questions_data: Data to validate

        Returns:
            Validated questions list

        Raises:
            ValidationError: If data is invalid
        """
        if not isinstance(questions_data, list):
            raise ValidationError(f"Questions data must be a list, got {type(questions_data)}")

        if not questions_data:
            raise ValidationError("Questions list is empty")

        for idx, item in enumerate(questions_data):
            if not isinstance(item, dict):
                raise ValidationError(f"Question {idx} must be a dict, got {type(item)}")

            if "task_id" not in item:
                raise ValidationError(f"Question {idx} missing 'task_id'")

            if "question" not in item:
                raise ValidationError(f"Question {idx} missing 'question'")

        return questions_data

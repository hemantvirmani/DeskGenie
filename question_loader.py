"""Question loading and fetching functionality."""

import json
import requests
from typing import List, Dict
import config
from utils import retry_with_backoff


class QuestionLoader:
    """Handles loading questions from various sources."""

    def __init__(self, api_url: str = config.DEFAULT_API_URL):
        self.api_url = api_url

    @retry_with_backoff(max_retries=3, initial_delay=1.0, backoff_factor=2.0)
    def _fetch_from_api(self) -> List[Dict]:
        """Fetch questions from the API with retry logic."""
        questions_url = f"{self.api_url}/questions"
        print(f"Fetching questions from: {questions_url}")

        response = requests.get(questions_url, timeout=config.FETCH_TIMEOUT)
        response.raise_for_status()
        questions_data = response.json()

        if not questions_data:
            raise ValueError("Fetched questions list is empty.")

        print(f"Fetched {len(questions_data)} questions.")
        return questions_data

    def _load_from_file(self, file_path: str = config.QUESTIONS_FILE) -> List[Dict]:
        """Load questions from local file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            questions = json.load(f)
            print(f"[INFO] Loaded {len(questions)} questions from {file_path}")
            return questions

    def get_questions(self, test_mode: bool = False) -> List[Dict]:
        """Get questions from local file (test) or API (production)."""
        if test_mode:
            try:
                return self._load_from_file()
            except Exception as e:
                print(f"[WARNING] Offline loading failed: {e}, falling back to API")

        return self._fetch_from_api()

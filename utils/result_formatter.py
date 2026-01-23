"""Result formatting for different output types."""

import pandas as pd
from typing import List, Tuple, Dict
from colorama import Fore, Style


class ResultFormatter:
    """Formats results for different output targets."""

    @staticmethod
    def format_for_api(results: List[Tuple[str, str, str]]) -> List[Dict]:
        """Format results for API submission."""
        return [
            {"task_id": task_id, "submitted_answer": answer}
            for task_id, _, answer in results
        ]

    @staticmethod
    def format_for_display(results: List[Tuple[str, str, str]]) -> List[Dict]:
        """Format results for UI display."""
        return [
            {
                "Task ID": task_id,
                "Question": question_text,
                "Submitted Answer": answer
            }
            for task_id, question_text, answer in results
        ]

    @staticmethod
    def format_for_verification(results: List[Tuple[str, str, str]]) -> List[str]:
        """Format results for test verification output."""
        output = []
        for task_id, question_text, answer in results:
            output.append(f"\nTask ID: {task_id}")
            output.append(f"Question: {question_text}")
            output.append(f"Answer: {answer}")
        return output

    @staticmethod
    def print_dataframe(df: pd.DataFrame) -> None:
        """Print DataFrame with full content (no truncation) with colored output."""
        pd.set_option('display.max_colwidth', None)
        pd.set_option('display.max_rows', None)
        for col in df.columns:
            for val in df[col]:
                val_str = str(val)
                # Color based on content
                if '✓ Correct' in val_str:
                    print(f"{Fore.GREEN}{val}{Style.RESET_ALL}", flush=True)
                elif '✗ Incorrect' in val_str:
                    print(f"{Fore.RED}{val}{Style.RESET_ALL}", flush=True)
                elif val_str.startswith('===') or val_str.startswith('SUMMARY'):
                    print(f"{Fore.CYAN}{val}{Style.RESET_ALL}", flush=True)
                elif 'ERROR' in val_str:
                    print(f"{Fore.RED}{val}{Style.RESET_ALL}", flush=True)
                elif val_str.startswith('Expected:') or val_str.startswith('Got:'):
                    print(f"{Fore.YELLOW}{val}{Style.RESET_ALL}", flush=True)
                else:
                    print(val, flush=True)

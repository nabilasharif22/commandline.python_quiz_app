import json
import random
from datetime import datetime
from pathlib import Path
from typing import Any

from utils import (
    build_hint,
    calculate_category_averages,
    load_secure_data,
    project_path,
    question_id,
    save_secure_data,
    weighted_sample_without_replacement,
)


class QuizEngine:
    def __init__(
        self,
        username: str,
        questions_file: Path | None = None,
        feedback_file: Path | None = None,
        scores_file: Path | None = None,
    ):
        self.username = username
        self.questions_file = questions_file or project_path("questions.json")
        self.feedback_file = feedback_file or project_path("feedback.dat")
        self.scores_file = scores_file or project_path("scores.dat")

    def load_questions(self) -> list[dict[str, Any]]:
        if not self.questions_file.exists():
            print("No JSON files to pull questions")
            return []

        try:
            payload = json.loads(self.questions_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            print("No JSON files to pull questions")
            return []

        questions = payload.get("questions", [])
        if not isinstance(questions, list):
            return []
        return [question for question in questions if isinstance(question, dict)]

    def available_categories(self, questions: list[dict[str, Any]]) -> list[str]:
        return sorted({str(question.get("category", "")).strip() for question in questions if question.get("category")})

    def _load_feedback(self) -> dict[str, dict[str, dict[str, int]]]:
        return load_secure_data(self.feedback_file, {})

    def _save_feedback(self, feedback_data: dict[str, dict[str, dict[str, int]]]) -> None:
        save_secure_data(self.feedback_file, feedback_data)

    def _load_scores(self) -> dict[str, list[dict[str, Any]]]:
        return load_secure_data(self.scores_file, {})

    def _save_scores(self, score_data: dict[str, list[dict[str, Any]]]) -> None:
        save_secure_data(self.scores_file, score_data)

    def _feedback_score(self, question_feedback: dict[str, int] | None) -> float:
        if not question_feedback:
            return 1.0
        likes = int(question_feedback.get("likes", 0))
        dislikes = int(question_feedback.get("dislikes", 0))
        return max(0.2, 1.0 + likes - dislikes)

    def select_questions(
        self,
        all_questions: list[dict[str, Any]],
        category: str,
        count: int,
        difficulty: str,
    ) -> list[dict[str, Any]]:
        filtered = [q for q in all_questions if str(q.get("category", "")).lower() == category.lower()]
        if difficulty != "random":
            filtered = [q for q in filtered if str(q.get("difficulty", "")).lower() == difficulty]

        if not filtered:
            return []

        if count >= len(filtered):
            return random.sample(filtered, len(filtered))

        feedback_data = self._load_feedback().get(self.username, {})
        has_feedback_history = any(question_id(question) in feedback_data for question in filtered)

        if not has_feedback_history:
            return random.sample(filtered, count)

        weights: list[float] = []
        for question in filtered:
            qid = question_id(question)
            weights.append(self._feedback_score(feedback_data.get(qid)))

        return weighted_sample_without_replacement(filtered, weights, count)

    def _is_correct_answer(self, question: dict[str, Any], user_answer: str) -> bool:
        question_type = question.get("type", "")
        expected = str(question.get("answer", "")).strip().lower()
        candidate = user_answer.strip().lower()

        if question_type == "true_false":
            normalize = {
                "t": "true",
                "true": "true",
                "f": "false",
                "false": "false",
            }
            if candidate not in normalize:
                return False
            candidate = normalize[candidate]
        elif question_type == "multiple_choice":
            options = question.get("options", [])
            option_labels = [chr(ord("A") + idx) for idx in range(len(options))]
            if candidate.upper() in option_labels:
                selected_index = ord(candidate.upper()) - ord("A")
                if 0 <= selected_index < len(options):
                    candidate = str(options[selected_index]).strip().lower()

        return candidate == expected

    def _prompt_for_answer(self, question: dict[str, Any]) -> str:
        question_type = question.get("type", "")

        while True:
            user_input = input("Your answer (or type 'hint'): ").strip()
            if user_input.lower() == "hint":
                print(build_hint(question))
                continue

            if question_type == "multiple_choice":
                options = question.get("options", [])
                valid_labels = {chr(ord("A") + idx) for idx in range(len(options))}
                if user_input.upper() not in valid_labels and user_input.lower() not in {str(option).lower() for option in options}:
                    label_list = ", ".join(sorted(valid_labels))
                    print(f"Invalid input. Please enter one of {label_list} or the option text.")
                    continue
                return user_input

            if question_type == "true_false":
                if user_input.lower() not in {"true", "false", "t", "f"}:
                    print("Invalid input. Please enter true/false or t/f.")
                    continue
                return user_input

            if question_type == "short_answer":
                if not user_input:
                    print("Invalid input. Please enter a short answer.")
                    continue
                return user_input

            print("Invalid input. Unsupported question type.")

    def _collect_feedback(self, question: dict[str, Any]) -> None:
        feedback_data = self._load_feedback()
        user_feedback = feedback_data.setdefault(self.username, {})
        qid = question_id(question)
        record = user_feedback.setdefault(qid, {"likes": 0, "dislikes": 0})

        while True:
            choice = input("Did you like this question? (y/n): ").strip().lower()
            if choice == "y":
                record["likes"] = int(record.get("likes", 0)) + 1
                break
            if choice == "n":
                record["dislikes"] = int(record.get("dislikes", 0)) + 1
                break
            print("Invalid input. Please enter y or n.")

        self._save_feedback(feedback_data)

    def _record_score(self, category: str, total: int, correct: int) -> None:
        percentage = (correct / total * 100) if total else 0.0
        score_data = self._load_scores()
        user_records = score_data.setdefault(self.username, [])
        user_records.append(
            {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "category": category,
                "correct": correct,
                "total": total,
                "percentage": round(percentage, 2),
            }
        )
        self._save_scores(score_data)

    def display_category_stats(self) -> None:
        score_data = self._load_scores()
        user_records = score_data.get(self.username, [])
        averages = calculate_category_averages(user_records)

        category = input("Enter a category for stats: ").strip()
        normalized_lookup = {name.casefold(): name for name in averages}
        matched_category = normalized_lookup.get(category.casefold())

        if matched_category is None:
            print("Take more quizes in this category for stats")
            return

        print(f"Average percentage correct for {matched_category}: {averages[matched_category]:.2f}%")

    def run_quiz(self, category: str, question_count: int, difficulty: str) -> None:
        all_questions = self.load_questions()
        selected = self.select_questions(all_questions, category, question_count, difficulty)

        if not selected:
            print("No questions available for your selection.")
            return

        correct_count = 0

        for index, question in enumerate(selected, start=1):
            print(f"\nQuestion {index}/{len(selected)}")
            print(question.get("question", ""))

            if question.get("type") == "multiple_choice":
                options = question.get("options", [])
                for option_index, option in enumerate(options):
                    label = chr(ord("A") + option_index)
                    print(f"  {label}. {option}")

            user_answer = self._prompt_for_answer(question)
            is_correct = self._is_correct_answer(question, user_answer)

            if is_correct:
                correct_count += 1
                print("Correct!")
            else:
                print("Incorrect.")
                print(f"Correct answer: {question.get('answer', '')}")

            self._collect_feedback(question)
            input("Click enter for next question")

        total_questions = len(selected)
        percentage = (correct_count / total_questions * 100) if total_questions else 0.0
        print(f"\nTotal score: {correct_count}/{total_questions}")
        print(f"Percentage score: {percentage:.2f}%")

        self._record_score(category, total_questions, correct_count)

        while True:
            show_stats = input("Check additional stats? (y/n): ").strip().lower()
            if show_stats == "y":
                self.display_category_stats()
                break
            if show_stats == "n":
                break
            print("Invalid input. Please enter y or n.")

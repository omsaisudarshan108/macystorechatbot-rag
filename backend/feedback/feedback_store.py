"""
Feedback storage for answer quality and helpfulness ratings.
Stores feedback in JSON file for development, can be extended to use Cloud Storage or database.
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
import os


class FeedbackStore:
    def __init__(self, storage_path: str = "data/feedback"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.feedback_file = self.storage_path / "feedback.jsonl"

    def save_feedback(
        self,
        question: str,
        answer: str,
        rating: int,
        was_helpful: bool,
        comment: Optional[str] = None,
        store_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> dict:
        """
        Save feedback for an answer.

        Args:
            question: The question that was asked
            answer: The answer that was provided
            rating: Rating from 1-5 stars
            was_helpful: Boolean indicating if answer was helpful
            comment: Optional text feedback
            store_id: Optional store identifier
            session_id: Optional session identifier for tracking

        Returns:
            dict: Saved feedback record with timestamp and ID
        """
        feedback_record = {
            "id": self._generate_id(),
            "timestamp": datetime.utcnow().isoformat(),
            "question": question,
            "answer": answer[:500],  # Store first 500 chars
            "rating": rating,
            "was_helpful": was_helpful,
            "comment": comment,
            "store_id": store_id,
            "session_id": session_id
        }

        # Append to JSONL file
        with open(self.feedback_file, "a") as f:
            f.write(json.dumps(feedback_record) + "\n")

        return feedback_record

    def get_all_feedback(self) -> list[dict]:
        """Retrieve all feedback records."""
        if not self.feedback_file.exists():
            return []

        feedback_list = []
        with open(self.feedback_file, "r") as f:
            for line in f:
                if line.strip():
                    feedback_list.append(json.loads(line))

        return feedback_list

    def get_feedback_stats(self) -> dict:
        """Get statistics about feedback."""
        all_feedback = self.get_all_feedback()

        if not all_feedback:
            return {
                "total_responses": 0,
                "average_rating": 0,
                "helpful_percentage": 0,
                "total_comments": 0
            }

        total = len(all_feedback)
        avg_rating = sum(f["rating"] for f in all_feedback) / total
        helpful_count = sum(1 for f in all_feedback if f["was_helpful"])
        comment_count = sum(1 for f in all_feedback if f.get("comment"))

        return {
            "total_responses": total,
            "average_rating": round(avg_rating, 2),
            "helpful_percentage": round((helpful_count / total) * 100, 1),
            "total_comments": comment_count,
            "rating_distribution": self._get_rating_distribution(all_feedback)
        }

    def _get_rating_distribution(self, feedback_list: list[dict]) -> dict:
        """Get distribution of ratings."""
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for feedback in feedback_list:
            rating = feedback.get("rating", 0)
            if rating in distribution:
                distribution[rating] += 1
        return distribution

    def _generate_id(self) -> str:
        """Generate unique feedback ID."""
        from uuid import uuid4
        return f"fb_{uuid4().hex[:12]}"

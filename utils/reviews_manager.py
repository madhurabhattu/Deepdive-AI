"""
DeepDive AI — Reviews & Ratings Management

Handles loading, saving, and computing metrics for community reviews.
Logic is kept strictly decoupled from the UI (Constitution §IV).
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Storage configuration
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
REVIEWS_FILE = DATA_DIR / "reviews.json"


@dataclass
class Review:
    """Dataclass representing a user submitted review/rating."""

    name: str
    rating: int
    comment: str
    timestamp: str
    consent: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Serialize Review instance to a dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Review:
        """Create a Review instance from a dictionary."""
        return cls(
            name=str(data.get("name", "")).strip(),
            rating=int(data.get("rating", 5)),
            comment=str(data.get("comment", "")).strip(),
            timestamp=str(data.get("timestamp", "")).strip(),
            consent=bool(data.get("consent", True)),
        )


def load_reviews() -> list[Review]:
    """Load all reviews from storage. Returns empty list if file doesn't exist."""
    if not REVIEWS_FILE.exists():
        return []
    try:
        with open(REVIEWS_FILE, encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            data = json.loads(content)
            if not isinstance(data, list):
                logger.warning("Reviews JSON is not a list. Resetting.")
                return []
            return [Review.from_dict(item) for item in data]
    except Exception as e:
        logger.error("Failed to load reviews: %s", e)
        return []


def save_review(review: Review) -> None:
    """Append a new review to the persistent storage atomically."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    reviews = load_reviews()
    reviews.append(review)
    try:
        temp_file = REVIEWS_FILE.with_suffix(".tmp")
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(
                [r.to_dict() for r in reviews],
                f,
                indent=2,
                ensure_ascii=False,
            )
        temp_file.replace(REVIEWS_FILE)
    except Exception as e:
        logger.error("Failed to save review: %s", e)
        raise e


def calculate_average_rating(reviews: list[Review]) -> float:
    """Calculate the average rating rounded to 1 decimal place."""
    if not reviews:
        return 0.0
    total = sum(r.rating for r in reviews)
    return round(total / len(reviews), 1)


def get_rating_distribution(reviews: list[Review]) -> dict[int, int]:
    """Calculate count of ratings for each star level (1 to 5)."""
    dist = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    for r in reviews:
        if 1 <= r.rating <= 5:
            dist[r.rating] += 1
    return dist


def render_sidebar_review_form() -> None:
    """Render the Rate DeepDive AI form in the Streamlit sidebar."""
    from datetime import datetime

    import streamlit as st

    st.sidebar.markdown("## ⭐ Rate DeepDive AI")

    # Use unique keys to identify values in session state
    name_key = "sidebar_review_name"
    rating_key = "sidebar_review_rating"
    comment_key = "sidebar_review_comment"
    consent_key = "sidebar_review_consent"
    submit_key = "sidebar_review_submit"

    review_name = st.sidebar.text_input("Your Name", key=name_key)
    review_rating = st.sidebar.slider(
        "Rating",
        min_value=1,
        max_value=5,
        value=5,
        key=rating_key,
    )
    review_comment = st.sidebar.text_area(
        "Feedback (Optional)",
        key=comment_key,
    )
    
    # GDPR-style consent checkbox
    review_consent = st.sidebar.checkbox(
        "I consent to the collection and public display of my review and name.",
        value=False,
        key=consent_key,
    )

    submit_review = st.sidebar.button(
        "Submit Review",
        key=submit_key,
    )

    if submit_review:
        name_val = review_name.strip()
        comment_val = review_comment.strip()
        if not name_val:
            st.sidebar.error("Name cannot be empty.")
        elif not review_consent:
            st.sidebar.error("You must consent to the storage and display of your review.")
        else:
            last_sub = st.session_state.get("last_submitted_review")
            if last_sub == (name_val, review_rating, comment_val):
                st.sidebar.warning("You have already submitted this review.")
            else:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
                new_review = Review(
                    name=name_val,
                    rating=review_rating,
                    comment=comment_val,
                    timestamp=current_time,
                    consent=True,
                )
                save_review(new_review)
                st.session_state["last_submitted_review"] = (
                    name_val,
                    review_rating,
                    comment_val,
                )
                st.session_state["review_success_msg"] = "Thank you for your review!"
                # Clear fields
                st.session_state[name_key] = ""
                st.session_state[comment_key] = ""
                st.session_state[consent_key] = False
                st.rerun()

    if "review_success_msg" in st.session_state:
        st.sidebar.success(st.session_state["review_success_msg"])
        del st.session_state["review_success_msg"]

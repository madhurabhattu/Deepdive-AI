"""
DeepDive AI — Unit Tests for Reviews Management
"""

from __future__ import annotations

import pytest

from utils.reviews_manager import (
    Review,
    calculate_average_rating,
    get_rating_distribution,
    load_reviews,
    save_review,
)


@pytest.fixture
def temp_reviews_file(tmp_path, monkeypatch):
    """Fixture to mock the reviews file path to a temp file."""
    temp_file = tmp_path / "reviews.json"
    monkeypatch.setattr("utils.reviews_manager.REVIEWS_FILE", temp_file)
    monkeypatch.setattr("utils.reviews_manager.DATA_DIR", tmp_path)
    return temp_file


def test_review_serialization():
    """Verify Review dataclass to_dict and from_dict roundtripping."""
    rev_dict = {
        "name": "Madhura",
        "rating": 5,
        "comment": "Superb tool!",
        "timestamp": "2026-06-12 10:30",
        "consent": True,
    }
    r = Review.from_dict(rev_dict)
    assert r.name == "Madhura"
    assert r.rating == 5
    assert r.comment == "Superb tool!"
    assert r.timestamp == "2026-06-12 10:30"
    assert r.consent is True
    assert r.to_dict() == rev_dict


def test_load_reviews_empty_file(temp_reviews_file):
    """Verify loading from non-existent or empty reviews file returns empty list."""
    # File does not exist yet
    assert load_reviews() == []

    # File exists but is empty
    temp_reviews_file.write_text("", encoding="utf-8")
    assert load_reviews() == []


def test_save_and_load_reviews(temp_reviews_file):
    """Verify reviews can be successfully saved and loaded."""
    rev1 = Review("User A", 5, "Comment A", "2026-06-12 11:00")
    rev2 = Review("User B", 4, "", "2026-06-12 11:05")

    save_review(rev1)
    save_review(rev2)

    loaded = load_reviews()
    assert len(loaded) == 2
    assert loaded[0].name == "User A"
    assert loaded[0].rating == 5
    assert loaded[1].name == "User B"
    assert loaded[1].comment == ""


def test_calculate_average_rating():
    """Verify average rating math."""
    # No reviews
    assert calculate_average_rating([]) == 0.0

    # Normal reviews
    reviews = [
        Review("A", 5, "", ""),
        Review("B", 4, "", ""),
        Review("C", 3, "", ""),
    ]
    assert calculate_average_rating(reviews) == 4.0

    # Let's check with values that round unambiguously
    reviews_frac2 = [
        Review("A", 5, "", ""),
        Review("B", 4, "", ""),
        Review("C", 5, "", ""),
    ]
    # Sum: 14 / 3 = 4.666... -> rounds to 4.7
    assert calculate_average_rating(reviews_frac2) == 4.7


def test_get_rating_distribution():
    """Verify rating distribution count dictionary generation."""
    reviews = [
        Review("A", 5, "", ""),
        Review("B", 5, "", ""),
        Review("C", 4, "", ""),
        Review("D", 2, "", ""),
    ]
    dist = get_rating_distribution(reviews)
    assert dist[5] == 2
    assert dist[4] == 1
    assert dist[3] == 0
    assert dist[2] == 1
    assert dist[1] == 0

"""Tests for delay cascade algorithm."""

import pytest
from datetime import datetime, timedelta
from peewee import SqliteDatabase

from lcr.models import database, Problem, Review
from lcr.database.repository import ProblemRepository, ReviewRepository
from lcr.utils.delay_cascade import DelayCascade


@pytest.fixture
def test_db():
    """Create an in-memory test database."""
    from lcr.database import get_db
    
    # Initialize in-memory database
    db = get_db(":memory:")
    yield db
    
    # Cleanup
    db.drop_tables([Problem, Review])
    db.close()


@pytest.fixture
def sample_problem(test_db):
    """Create a sample problem."""
    return ProblemRepository.create("1", "Two Sum")


class TestDelayCascade:
    """Tests for DelayCascade class."""

    def test_calculate_delay_no_delay(self):
        """Test calculating delay when completed on time."""
        scheduled = datetime(2024, 1, 1, 12, 0, 0)
        completed = datetime(2024, 1, 1, 12, 0, 0)

        delay = DelayCascade.calculate_delay(scheduled, completed)
        assert delay == 0

    def test_calculate_delay_early_completion(self):
        """Test that early completion counts as 0 delay."""
        scheduled = datetime(2024, 1, 5, 12, 0, 0)
        completed = datetime(2024, 1, 3, 12, 0, 0)

        delay = DelayCascade.calculate_delay(scheduled, completed)
        assert delay == 0  # No penalty for early completion

    def test_calculate_delay_late_completion(self):
        """Test calculating delay for late completion."""
        scheduled = datetime(2024, 1, 1, 12, 0, 0)
        completed = datetime(2024, 1, 5, 12, 0, 0)

        delay = DelayCascade.calculate_delay(scheduled, completed)
        assert delay == 4

    def test_calculate_delay_very_late(self):
        """Test calculating delay for very late completion."""
        scheduled = datetime(2024, 1, 1, 12, 0, 0)
        completed = datetime(2024, 2, 1, 12, 0, 0)

        delay = DelayCascade.calculate_delay(scheduled, completed)
        assert delay == 31

    def test_apply_cascade_no_delay(self, test_db, sample_problem):
        """Test that no cascade occurs when completed on time."""
        now = datetime.utcnow()

        # Create a chain of reviews
        review1 = ReviewRepository.create(
            sample_problem, "chain-123", now, iteration_number=1
        )
        review2 = ReviewRepository.create(
            sample_problem, "chain-123", now + timedelta(days=7), iteration_number=2
        )

        # Complete review1 on time
        review1.complete(now)

        # Apply cascade
        updated_count = DelayCascade.apply_cascade(review1, now)

        # No reviews should be updated
        assert updated_count == 0

        # Review2 date should be unchanged
        review2_refreshed = Review.get_by_id(review2.id)
        assert review2_refreshed.scheduled_date == now + timedelta(days=7)

    def test_apply_cascade_with_delay(self, test_db, sample_problem):
        """Test cascade when review completed late."""
        now = datetime.utcnow()

        # Create a chain of reviews
        review1 = ReviewRepository.create(
            sample_problem, "chain-123", now, iteration_number=1
        )
        review2 = ReviewRepository.create(
            sample_problem, "chain-123", now + timedelta(days=7), iteration_number=2
        )
        review3 = ReviewRepository.create(
            sample_problem, "chain-123", now + timedelta(days=18), iteration_number=3
        )

        # Complete review1 3 days late
        late_completion = now + timedelta(days=3)
        review1.complete(late_completion)

        # Apply cascade
        updated_count = DelayCascade.apply_cascade(review1, late_completion)

        # Both future reviews should be updated
        assert updated_count == 2

        # Verify reviews are delayed by 3 days
        review2_refreshed = Review.get_by_id(review2.id)
        assert review2_refreshed.scheduled_date == now + timedelta(days=10)

        review3_refreshed = Review.get_by_id(review3.id)
        assert review3_refreshed.scheduled_date == now + timedelta(days=21)

    def test_apply_cascade_no_future_reviews(self, test_db, sample_problem):
        """Test cascade when there are no future reviews."""
        now = datetime.utcnow()

        # Create only one review
        review1 = ReviewRepository.create(
            sample_problem, "chain-123", now, iteration_number=1
        )

        # Complete late
        late_completion = now + timedelta(days=5)
        review1.complete(late_completion)

        # Apply cascade
        updated_count = DelayCascade.apply_cascade(review1, late_completion)

        # No reviews to update
        assert updated_count == 0

    def test_apply_cascade_validation_not_completed(self, test_db, sample_problem):
        """Test that cascade fails if review not completed."""
        now = datetime.utcnow()

        review = ReviewRepository.create(
            sample_problem, "chain-123", now, iteration_number=1
        )

        with pytest.raises(ValueError, match="must be completed"):
            DelayCascade.apply_cascade(review, now)

    def test_apply_cascade_validation_no_completion_date(self, test_db, sample_problem):
        """Test that cascade fails without completion date."""
        now = datetime.utcnow()

        review = ReviewRepository.create(
            sample_problem, "chain-123", now, iteration_number=1
        )
        review.status = "completed"
        review.save()

        with pytest.raises(ValueError, match="must have an actual_completion_date"):
            DelayCascade.apply_cascade(review)

    def test_preview_cascade(self, test_db, sample_problem):
        """Test previewing cascade without applying it."""
        now = datetime.utcnow()

        # Create a chain
        review1 = ReviewRepository.create(
            sample_problem, "chain-123", now, iteration_number=1
        )
        review2 = ReviewRepository.create(
            sample_problem, "chain-123", now + timedelta(days=7), iteration_number=2
        )
        review3 = ReviewRepository.create(
            sample_problem, "chain-123", now + timedelta(days=18), iteration_number=3
        )

        # Complete review1 late
        late_completion = now + timedelta(days=3)
        review1.complete(late_completion)

        # Preview cascade
        preview = DelayCascade.preview_cascade(review1, late_completion)

        # Should preview 2 updates
        assert len(preview) == 2

        # Check first preview
        assert preview[0]['review_id'] == review2.id
        assert preview[0]['iteration'] == 2
        assert preview[0]['old_date'] == now + timedelta(days=7)
        assert preview[0]['new_date'] == now + timedelta(days=10)
        assert preview[0]['delay_days'] == 3

        # Check second preview
        assert preview[1]['review_id'] == review3.id
        assert preview[1]['iteration'] == 3
        assert preview[1]['old_date'] == now + timedelta(days=18)
        assert preview[1]['new_date'] == now + timedelta(days=21)
        assert preview[1]['delay_days'] == 3

        # Verify original dates unchanged
        review2_check = Review.get_by_id(review2.id)
        assert review2_check.scheduled_date == now + timedelta(days=7)

    def test_preview_cascade_no_delay(self, test_db, sample_problem):
        """Test preview returns empty list when no delay."""
        now = datetime.utcnow()

        review1 = ReviewRepository.create(
            sample_problem, "chain-123", now, iteration_number=1
        )
        review1.complete(now)

        preview = DelayCascade.preview_cascade(review1, now)
        assert preview == []

    def test_calculate_total_delay_in_chain(self, test_db, sample_problem):
        """Test calculating total delay across chain."""
        now = datetime.utcnow()

        # Create and complete reviews with varying delays
        review1 = ReviewRepository.create(
            sample_problem, "chain-123", now - timedelta(days=10), iteration_number=1
        )
        review1.complete(now - timedelta(days=7))  # 3 days late

        review2 = ReviewRepository.create(
            sample_problem, "chain-123", now - timedelta(days=3), iteration_number=2
        )
        review2.complete(now - timedelta(days=1))  # 2 days late

        # Pending review (shouldn't count)
        ReviewRepository.create(
            sample_problem, "chain-123", now + timedelta(days=7), iteration_number=3
        )

        total_delay = DelayCascade.calculate_total_delay_in_chain("chain-123")
        assert total_delay == 5  # 3 + 2

    def test_calculate_total_delay_empty_chain(self, test_db):
        """Test total delay for non-existent chain."""
        total_delay = DelayCascade.calculate_total_delay_in_chain("nonexistent")
        assert total_delay == 0

    def test_get_cascade_statistics(self, test_db, sample_problem):
        """Test getting cascade statistics."""
        now = datetime.utcnow()

        # Create mixed chain
        review1 = ReviewRepository.create(
            sample_problem, "chain-123", now - timedelta(days=20), iteration_number=1
        )
        review1.complete(now - timedelta(days=17))  # 3 days late

        review2 = ReviewRepository.create(
            sample_problem, "chain-123", now - timedelta(days=10), iteration_number=2
        )
        review2.complete(now - timedelta(days=10))  # On time

        review3 = ReviewRepository.create(
            sample_problem, "chain-123", now - timedelta(days=3), iteration_number=3
        )
        review3.complete(now - timedelta(days=1))  # 2 days late

        # Pending review
        ReviewRepository.create(
            sample_problem, "chain-123", now + timedelta(days=7), iteration_number=4
        )

        stats = DelayCascade.get_cascade_statistics("chain-123")

        assert stats['total_reviews'] == 4
        assert stats['completed_reviews'] == 3
        assert stats['pending_reviews'] == 1
        assert stats['total_delay_days'] == 5
        assert stats['average_delay_days'] == pytest.approx(5/3, rel=0.01)
        assert stats['max_delay_days'] == 3
        assert stats['reviews_with_delay'] == 2

    def test_get_cascade_statistics_empty_chain(self, test_db):
        """Test statistics for empty chain."""
        stats = DelayCascade.get_cascade_statistics("empty-chain")

        assert stats['total_reviews'] == 0
        assert stats['completed_reviews'] == 0
        assert stats['pending_reviews'] == 0
        assert stats['total_delay_days'] == 0
        assert stats['average_delay_days'] == 0.0
        assert stats['max_delay_days'] == 0
        assert stats['reviews_with_delay'] == 0

    def test_cascade_multiple_chains(self, test_db, sample_problem):
        """Test that cascade only affects reviews in the same chain."""
        now = datetime.utcnow()

        # Chain 1
        review1a = ReviewRepository.create(
            sample_problem, "chain-1", now, iteration_number=1
        )
        review1b = ReviewRepository.create(
            sample_problem, "chain-1", now + timedelta(days=7), iteration_number=2
        )

        # Chain 2
        review2a = ReviewRepository.create(
            sample_problem, "chain-2", now, iteration_number=1
        )
        review2b = ReviewRepository.create(
            sample_problem, "chain-2", now + timedelta(days=7), iteration_number=2
        )

        # Complete chain-1 review1a late
        late_completion = now + timedelta(days=5)
        review1a.complete(late_completion)
        DelayCascade.apply_cascade(review1a, late_completion)

        # Chain 1 should be delayed
        review1b_check = Review.get_by_id(review1b.id)
        assert review1b_check.scheduled_date == now + timedelta(days=12)

        # Chain 2 should be unchanged
        review2b_check = Review.get_by_id(review2b.id)
        assert review2b_check.scheduled_date == now + timedelta(days=7)

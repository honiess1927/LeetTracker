"""Tests for repository layer."""

import pytest
from datetime import datetime, timedelta
from peewee import SqliteDatabase

from lcr.models import database, Problem, Review, Session
from lcr.database.repository import (
    ProblemRepository,
    ReviewRepository,
    SessionRepository,
)


@pytest.fixture
def test_db():
    """Create an in-memory test database."""
    test_database = SqliteDatabase(":memory:")
    # Bind models to test database
    database.bind([Problem, Review, Session], bind_refs=False, bind_backrefs=False)
    database.init(":memory:", pragmas={"foreign_keys": 1})
    database.connect()
    # Explicitly enable foreign keys for this connection
    database.execute_sql('PRAGMA foreign_keys = ON;')
    database.create_tables([Problem, Review, Session])
    yield database
    database.drop_tables([Problem, Review, Session])
    database.close()


class TestProblemRepository:
    """Tests for ProblemRepository."""

    def test_create_problem(self, test_db):
        """Test creating a problem."""
        problem = ProblemRepository.create("1", "Two Sum")
        assert problem.problem_id == "1"
        assert problem.title == "Two Sum"

    def test_get_by_id(self, test_db):
        """Test getting a problem by ID."""
        ProblemRepository.create("1", "Two Sum")
        problem = ProblemRepository.get_by_id("1")
        assert problem is not None
        assert problem.problem_id == "1"

        # Test non-existent problem
        assert ProblemRepository.get_by_id("999") is None

    def test_get_or_create(self, test_db):
        """Test get_or_create functionality."""
        # Create new
        problem1 = ProblemRepository.get_or_create("1", "Two Sum")
        assert problem1.problem_id == "1"
        assert problem1.title == "Two Sum"

        # Get existing
        problem2 = ProblemRepository.get_or_create("1", "Different Title")
        assert problem2.id == problem1.id
        assert problem2.title == "Two Sum"  # Title not updated

    def test_get_all(self, test_db):
        """Test getting all problems."""
        ProblemRepository.create("1", "Two Sum")
        ProblemRepository.create("2", "Add Two Numbers")
        ProblemRepository.create("3", "Longest Substring")

        problems = ProblemRepository.get_all()
        assert len(problems) == 3


class TestReviewRepository:
    """Tests for ReviewRepository."""

    @pytest.fixture
    def sample_problem(self, test_db):
        """Create a sample problem."""
        return ProblemRepository.create("1", "Two Sum")

    def test_create_review(self, test_db, sample_problem):
        """Test creating a review."""
        scheduled = datetime.utcnow() + timedelta(days=1)
        review = ReviewRepository.create(
            sample_problem, "chain-123", scheduled, iteration_number=1
        )
        assert review.problem == sample_problem
        assert review.chain_id == "chain-123"
        assert review.scheduled_date == scheduled
        assert review.iteration_number == 1

    def test_get_pending_for_problem(self, test_db, sample_problem):
        """Test getting pending reviews for a problem."""
        # Create multiple reviews
        ReviewRepository.create(
            sample_problem,
            "chain-123",
            datetime.utcnow() + timedelta(days=1),
            iteration_number=1,
        )
        ReviewRepository.create(
            sample_problem,
            "chain-123",
            datetime.utcnow() + timedelta(days=7),
            iteration_number=2,
        )

        # Create and complete one
        review3 = ReviewRepository.create(
            sample_problem,
            "chain-123",
            datetime.utcnow() - timedelta(days=1),
            iteration_number=0,
        )
        review3.complete()

        pending = ReviewRepository.get_pending_for_problem(sample_problem)
        assert len(pending) == 2
        assert all(r.status == "pending" for r in pending)

    def test_get_earliest_pending_for_problem(self, test_db, sample_problem):
        """Test getting earliest pending review."""
        # Create reviews with different dates
        review1 = ReviewRepository.create(
            sample_problem,
            "chain-123",
            datetime.utcnow() + timedelta(days=7),
            iteration_number=2,
        )
        review2 = ReviewRepository.create(
            sample_problem,
            "chain-123",
            datetime.utcnow() + timedelta(days=1),
            iteration_number=1,
        )

        earliest = ReviewRepository.get_earliest_pending_for_problem(sample_problem)
        assert earliest.id == review2.id

    def test_get_due_reviews(self, test_db, sample_problem):
        """Test getting due reviews."""
        now = datetime.utcnow()

        # Create overdue review
        ReviewRepository.create(
            sample_problem, "chain-123", now - timedelta(days=2), iteration_number=1
        )

        # Create due today
        ReviewRepository.create(
            sample_problem, "chain-123", now - timedelta(hours=1), iteration_number=2
        )

        # Create future review
        ReviewRepository.create(
            sample_problem, "chain-123", now + timedelta(days=1), iteration_number=3
        )

        due_reviews = ReviewRepository.get_due_reviews(now)
        assert len(due_reviews) == 2

    def test_get_future_reviews_in_chain(self, test_db, sample_problem):
        """Test getting future reviews in a chain."""
        # Create chain of reviews
        ReviewRepository.create(
            sample_problem,
            "chain-123",
            datetime.utcnow() + timedelta(days=1),
            iteration_number=1,
        )
        ReviewRepository.create(
            sample_problem,
            "chain-123",
            datetime.utcnow() + timedelta(days=7),
            iteration_number=2,
        )
        ReviewRepository.create(
            sample_problem,
            "chain-123",
            datetime.utcnow() + timedelta(days=18),
            iteration_number=3,
        )

        # Get reviews after iteration 1
        future_reviews = ReviewRepository.get_future_reviews_in_chain("chain-123", 1)
        assert len(future_reviews) == 2
        assert future_reviews[0].iteration_number == 2
        assert future_reviews[1].iteration_number == 3

    def test_check_duplicate(self, test_db, sample_problem):
        """Test checking for duplicate reviews."""
        scheduled = datetime.utcnow() + timedelta(days=1)
        ReviewRepository.create(
            sample_problem, "chain-123", scheduled, iteration_number=1
        )

        # Same date should find duplicate
        duplicate = ReviewRepository.check_duplicate(
            sample_problem, scheduled, "chain-123"
        )
        assert duplicate is not None

        # Different date should not find duplicate
        different_date = scheduled + timedelta(days=1)
        not_duplicate = ReviewRepository.check_duplicate(
            sample_problem, different_date, "chain-123"
        )
        assert not_duplicate is None

    def test_get_completed_reviews(self, test_db, sample_problem):
        """Test getting completed reviews."""
        now = datetime.utcnow()

        # Create and complete reviews
        review1 = ReviewRepository.create(
            sample_problem, "chain-123", now - timedelta(days=10), iteration_number=1
        )
        review1.complete(now - timedelta(days=8))  # Completed 8 days ago

        review2 = ReviewRepository.create(
            sample_problem, "chain-123", now - timedelta(days=3), iteration_number=2
        )
        review2.complete(now - timedelta(days=2))  # Completed 2 days ago

        # Create pending review
        ReviewRepository.create(
            sample_problem, "chain-123", now + timedelta(days=1), iteration_number=3
        )

        completed = ReviewRepository.get_completed_reviews()
        assert len(completed) == 2

        # Test with date range - only review2 should be in range
        start_date = now - timedelta(days=3)  # 3 days ago
        end_date = now
        filtered = ReviewRepository.get_completed_reviews(start_date, end_date)
        assert len(filtered) == 1, f"Expected 1 review in range, got {len(filtered)}"
        assert filtered[0].id == review2.id


class TestSessionRepository:
    """Tests for SessionRepository."""

    @pytest.fixture
    def sample_problem(self, test_db):
        """Create a sample problem."""
        return ProblemRepository.create("1", "Two Sum")

    def test_create_session(self, test_db, sample_problem):
        """Test creating a session."""
        session = SessionRepository.create(sample_problem)
        assert session.problem == sample_problem
        assert session.status == "active"
        assert session.start_time is not None

    def test_create_session_with_start_time(self, test_db, sample_problem):
        """Test creating a session with specific start time."""
        start = datetime.utcnow() - timedelta(minutes=10)
        session = SessionRepository.create(sample_problem, start)
        assert session.start_time == start

    def test_get_active_session_for_problem(self, test_db, sample_problem):
        """Test getting active session."""
        session = SessionRepository.create(sample_problem)
        active = SessionRepository.get_active_session_for_problem(sample_problem)
        assert active.id == session.id

        # End the session
        session.end()

        # Should not find active session
        assert SessionRepository.get_active_session_for_problem(sample_problem) is None

    def test_get_sessions_for_problem(self, test_db, sample_problem):
        """Test getting all sessions for a problem."""
        # Create multiple sessions
        session1 = SessionRepository.create(
            sample_problem, datetime.utcnow() - timedelta(days=2)
        )
        session1.end()

        session2 = SessionRepository.create(
            sample_problem, datetime.utcnow() - timedelta(days=1)
        )
        session2.end()

        SessionRepository.create(sample_problem)

        sessions = SessionRepository.get_sessions_for_problem(sample_problem)
        assert len(sessions) == 3
        # Should be sorted by start_time descending
        assert sessions[0].status == "active"

    def test_get_completed_sessions(self, test_db, sample_problem):
        """Test getting completed sessions."""
        now = datetime.utcnow()

        # Create and complete sessions
        session1 = SessionRepository.create(
            sample_problem, now - timedelta(days=10)
        )
        session1.end(now - timedelta(days=10, hours=-1))

        session2 = SessionRepository.create(sample_problem, now - timedelta(days=5))
        session2.end(now - timedelta(days=5, hours=-1))

        # Create active session
        SessionRepository.create(sample_problem)

        completed = SessionRepository.get_completed_sessions()
        assert len(completed) == 2

        # Test with date range
        start_date = now - timedelta(days=6)
        filtered = SessionRepository.get_completed_sessions(start_date=start_date)
        assert len(filtered) == 1

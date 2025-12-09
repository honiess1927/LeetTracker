"""Tests for database models."""

import pytest
from datetime import datetime, timedelta
from peewee import SqliteDatabase

from lcr.models import database, Problem, Review, Session


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


@pytest.fixture
def sample_problem(test_db):
    """Create a sample problem for testing."""
    return Problem.create(problem_id="1", title="Two Sum")


class TestProblemModel:
    """Tests for Problem model."""

    def test_create_problem(self, test_db):
        """Test creating a problem."""
        problem = Problem.create(problem_id="42", title="Trapping Rain Water")
        assert problem.problem_id == "42"
        assert problem.title == "Trapping Rain Water"
        assert problem.created_at is not None
        assert problem.updated_at is not None

    def test_create_problem_without_title(self, test_db):
        """Test creating a problem without a title."""
        problem = Problem.create(problem_id="100")
        assert problem.problem_id == "100"
        assert problem.title is None

    def test_problem_unique_constraint(self, test_db, sample_problem):
        """Test that problem_id must be unique."""
        with pytest.raises(Exception):  # IntegrityError
            Problem.create(problem_id="1", title="Duplicate")

    def test_problem_str_representation(self, test_db):
        """Test string representation of problem."""
        problem = Problem.create(problem_id="1", title="Two Sum")
        assert str(problem) == "Problem 1: Two Sum"

        problem_no_title = Problem.create(problem_id="2")
        assert str(problem_no_title) == "Problem 2"

    def test_problem_update_timestamp(self, test_db, sample_problem):
        """Test that updated_at changes on save."""
        original_updated = sample_problem.updated_at
        sample_problem.title = "Updated Title"
        sample_problem.save()
        assert sample_problem.updated_at > original_updated


class TestReviewModel:
    """Tests for Review model."""

    def test_create_review(self, test_db, sample_problem):
        """Test creating a review."""
        scheduled = datetime.utcnow() + timedelta(days=1)
        review = Review.create(
            problem=sample_problem,
            chain_id="chain-123",
            scheduled_date=scheduled,
            iteration_number=1,
        )
        assert review.problem == sample_problem
        assert review.chain_id == "chain-123"
        assert review.scheduled_date == scheduled
        assert review.status == "pending"
        assert review.iteration_number == 1
        assert review.actual_completion_date is None

    def test_review_complete(self, test_db, sample_problem):
        """Test completing a review."""
        scheduled = datetime.utcnow() - timedelta(days=1)
        review = Review.create(
            problem=sample_problem,
            chain_id="chain-123",
            scheduled_date=scheduled,
            iteration_number=1,
        )

        completion_date = datetime.utcnow()
        review.complete(completion_date)

        assert review.status == "completed"
        assert review.actual_completion_date == completion_date

    def test_review_is_overdue(self, test_db, sample_problem):
        """Test checking if review is overdue."""
        # Create overdue review
        past_date = datetime.utcnow() - timedelta(days=2)
        overdue_review = Review.create(
            problem=sample_problem,
            chain_id="chain-123",
            scheduled_date=past_date,
            iteration_number=1,
        )
        assert overdue_review.is_overdue() is True

        # Create future review
        future_date = datetime.utcnow() + timedelta(days=2)
        future_review = Review.create(
            problem=sample_problem,
            chain_id="chain-456",
            scheduled_date=future_date,
            iteration_number=1,
        )
        assert future_review.is_overdue() is False

        # Completed review should not be overdue
        overdue_review.complete()
        assert overdue_review.is_overdue() is False

    def test_review_delay_days(self, test_db, sample_problem):
        """Test calculating delay days."""
        scheduled = datetime.utcnow() - timedelta(days=5)
        review = Review.create(
            problem=sample_problem,
            chain_id="chain-123",
            scheduled_date=scheduled,
            iteration_number=1,
        )

        # Not completed yet
        assert review.delay_days() == 0

        # Complete on time
        review.complete(scheduled)
        assert review.delay_days() == 0

        # Complete late
        review2 = Review.create(
            problem=sample_problem,
            chain_id="chain-456",
            scheduled_date=scheduled,
            iteration_number=1,
        )
        late_completion = scheduled + timedelta(days=3)
        review2.complete(late_completion)
        assert review2.delay_days() == 3

    def test_review_str_representation(self, test_db, sample_problem):
        """Test string representation of review."""
        scheduled = datetime.utcnow()
        review = Review.create(
            problem=sample_problem,
            chain_id="chain-123",
            scheduled_date=scheduled,
            iteration_number=2,
        )
        str_repr = str(review)
        assert "Review #2" in str_repr
        assert "Problem 1" in str_repr

    def test_review_foreign_key_cascade(self, test_db, sample_problem):
        """Test that deleting problem cascades to reviews."""
        review = Review.create(
            problem=sample_problem,
            chain_id="chain-123",
            scheduled_date=datetime.utcnow(),
            iteration_number=1,
        )
        
        review_id = review.id
        problem_id = sample_problem.id
        
        # Delete the problem
        sample_problem.delete_instance()
        
        # Check if review was deleted by counting directly
        # Use .count() to avoid trying to load the problem foreign key
        count = Review.select().where(Review.id == review_id).count()
        assert count == 0, f"Review {review_id} should be deleted when problem {problem_id} is deleted"


class TestSessionModel:
    """Tests for Session model."""

    def test_create_session(self, test_db, sample_problem):
        """Test creating a session."""
        start = datetime.utcnow()
        session = Session.create(problem=sample_problem, start_time=start)
        assert session.problem == sample_problem
        assert session.start_time == start
        assert session.status == "active"
        assert session.end_time is None
        assert session.duration is None

    def test_session_end(self, test_db, sample_problem):
        """Test ending a session."""
        start = datetime.utcnow()
        session = Session.create(problem=sample_problem, start_time=start)

        end = start + timedelta(minutes=30)
        session.end(end)

        assert session.status == "completed"
        assert session.end_time == end
        assert session.duration == 1800  # 30 minutes in seconds

    def test_session_format_duration(self, test_db, sample_problem):
        """Test formatting duration."""
        session = Session.create(
            problem=sample_problem, start_time=datetime.utcnow()
        )

        # Test various durations
        session.duration = 0
        assert session.format_duration() == "0s"

        session.duration = 45
        assert session.format_duration() == "45s"

        session.duration = 90
        assert session.format_duration() == "1m 30s"

        session.duration = 3600
        assert session.format_duration() == "1h"

        session.duration = 3665
        assert session.format_duration() == "1h 1m 5s"

    def test_session_get_current_duration(self, test_db, sample_problem):
        """Test getting current duration."""
        start = datetime.utcnow() - timedelta(seconds=10)
        session = Session.create(problem=sample_problem, start_time=start)

        # Active session
        current = session.get_current_duration()
        assert current >= 10

        # Completed session
        session.duration = 100
        session.status = "completed"
        assert session.get_current_duration() == 100

    def test_session_str_representation(self, test_db, sample_problem):
        """Test string representation of session."""
        session = Session.create(
            problem=sample_problem, start_time=datetime.utcnow()
        )
        assert "Active session" in str(session)
        assert "Problem 1" in str(session)

        session.duration = 120
        session.status = "completed"
        str_repr = str(session)
        assert "Session for Problem 1" in str_repr
        assert "2m" in str_repr

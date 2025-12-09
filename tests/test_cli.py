"""Tests for CLI commands."""

import pytest
from datetime import datetime, timedelta
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

from lcr.cli.commands import app
from lcr.database import get_db, ProblemRepository, ReviewRepository, SessionRepository
from lcr.models import Problem, Review, Session
from lcr.utils import DateTimeHelper

runner = CliRunner()


@pytest.fixture
def setup_db():
    """Setup test database."""
    # Reset global db manager to ensure clean state
    import lcr.database.connection as conn
    conn._db_manager = None
    
    # Initialize fresh database
    db = get_db(":memory:")
    yield db
    
    # Cleanup
    db.close()
    conn._db_manager = None


@pytest.fixture
def sample_problem(setup_db):
    """Create a sample problem."""
    return ProblemRepository.get_or_create("1", "Two Sum")


@pytest.fixture
def sample_review(setup_db, sample_problem):
    """Create a sample review."""
    now = DateTimeHelper.now_utc()
    return ReviewRepository.create(
        sample_problem,
        "test-chain",
        now + timedelta(days=1),
        iteration_number=1
    )


class TestAddCommand:
    """Tests for the 'add' command."""

    def test_add_problem_default_times(self, setup_db):
        """Test adding a problem with default intervals."""
        result = runner.invoke(app, ["add", "42"])
        
        assert result.exit_code == 0
        assert "Created" in result.stdout
        assert "42" in result.stdout
        
        # Verify problem was created
        problem = ProblemRepository.get_by_id("42")
        assert problem is not None
        
        # Verify reviews were created
        pending = ReviewRepository.get_pending_for_problem(problem)
        assert len(pending) == 4  # Default is 4 reviews

    def test_add_problem_custom_times(self, setup_db):
        """Test adding a problem with custom number of reviews."""
        result = runner.invoke(app, ["add", "100", "--times", "2"])
        
        assert result.exit_code == 0
        
        problem = ProblemRepository.get_by_id("100")
        pending = ReviewRepository.get_pending_for_problem(problem)
        assert len(pending) == 2

    def test_add_problem_with_title(self, setup_db):
        """Test adding a problem with title."""
        result = runner.invoke(app, ["add", "200", "--title", "Test Problem"])
        
        assert result.exit_code == 0
        
        problem = ProblemRepository.get_by_id("200")
        assert problem.title == "Test Problem"

    def test_add_problem_specific_date(self, setup_db):
        """Test adding a problem with specific date."""
        result = runner.invoke(app, ["add", "300", "--date", "2024-12-25"])
        
        assert result.exit_code == 0
        assert "2024-12-25" in result.stdout
        
        problem = ProblemRepository.get_by_id("300")
        pending = ReviewRepository.get_pending_for_problem(problem)
        assert len(pending) == 1

    def test_add_problem_invalid_date(self, setup_db):
        """Test adding a problem with invalid date format."""
        result = runner.invoke(app, ["add", "400", "--date", "invalid-date"])
        
        assert result.exit_code == 1
        assert "Error" in result.stdout

    def test_add_problem_duplicate_prevention(self, setup_db):
        """Test that adding same problem creates separate review chains."""
        # Add problem first time
        result1 = runner.invoke(app, ["add", "500", "--times", "2"])
        assert result1.exit_code == 0
        
        # Add again - creates new chain with potentially overlapping dates
        result2 = runner.invoke(app, ["add", "500", "--times", "2"])
        assert result2.exit_code == 0
        
        problem = ProblemRepository.get_by_id("500")
        pending = ReviewRepository.get_pending_for_problem(problem)
        # Each add creates its own chain, so we get 4 reviews total
        # (2 from first add + 2 from second add)
        assert len(pending) == 4


class TestCheckinCommand:
    """Tests for the 'checkin' command."""

    def test_checkin_existing_review(self, setup_db, sample_problem):
        """Test checking in an existing review."""
        # Create a pending review
        now = DateTimeHelper.now_utc()
        review = ReviewRepository.create(
            sample_problem, "test", now - timedelta(days=1), iteration_number=1
        )
        
        result = runner.invoke(app, ["checkin", "1"])
        
        assert result.exit_code == 0
        assert "Completed" in result.stdout
        
        # Verify review was marked complete
        review = Review.get_by_id(review.id)
        assert review.status == "completed"
        assert review.actual_completion_date is not None

    def test_checkin_on_time(self, setup_db, sample_problem):
        """Test checking in a review on time."""
        now = DateTimeHelper.now_utc()
        review = ReviewRepository.create(
            sample_problem, "test", now - timedelta(hours=1), iteration_number=1
        )
        
        result = runner.invoke(app, ["checkin", "1"])
        
        assert result.exit_code == 0
        assert "on time" in result.stdout.lower()

    def test_checkin_late_with_cascade(self, setup_db, sample_problem):
        """Test checking in a late review triggers cascade."""
        now = DateTimeHelper.now_utc()
        
        # Create review chain
        review1 = ReviewRepository.create(
            sample_problem, "test", now - timedelta(days=5), iteration_number=1
        )
        review2 = ReviewRepository.create(
            sample_problem, "test", now + timedelta(days=2), iteration_number=2
        )
        
        result = runner.invoke(app, ["checkin", "1"])
        
        assert result.exit_code == 0
        assert "late" in result.stdout.lower()
        assert "Updated" in result.stdout
        
        # Verify cascade was applied
        review2 = Review.get_by_id(review2.id)
        # Should be pushed forward by 5+ days
        assert review2.scheduled_date > now + timedelta(days=2)

    def test_checkin_orphan(self, setup_db, sample_problem):
        """Test orphan check-in (no pending review)."""
        result = runner.invoke(app, ["checkin", "1"])
        
        assert result.exit_code == 0
        assert "No pending review" in result.stdout
        assert "standalone" in result.stdout.lower()
        
        # Verify orphan log was created
        completed = ReviewRepository.get_completed_reviews(
            DateTimeHelper.now_utc() - timedelta(days=1),
            DateTimeHelper.now_utc()
        )
        assert len(completed) > 0

    def test_checkin_nonexistent_problem(self, setup_db):
        """Test checking in a problem that doesn't exist."""
        result = runner.invoke(app, ["checkin", "999"])
        
        assert result.exit_code == 1
        assert "not found" in result.stdout.lower()


class TestListCommand:
    """Tests for the 'list' command."""

    def test_list_empty(self, setup_db):
        """Test listing when no reviews are due."""
        result = runner.invoke(app, ["list"])
        
        assert result.exit_code == 0
        assert "No reviews due" in result.stdout

    def test_list_with_due_reviews(self, setup_db):
        """Test listing due reviews."""
        # Create problems with due reviews
        now = DateTimeHelper.now_utc()
        
        problem1 = ProblemRepository.get_or_create("10", "Problem 10")
        ReviewRepository.create(problem1, "test1", now - timedelta(days=1), 1)
        
        problem2 = ProblemRepository.get_or_create("20", "Problem 20")
        ReviewRepository.create(problem2, "test2", now - timedelta(hours=6), 1)
        
        result = runner.invoke(app, ["list"])
        
        assert result.exit_code == 0
        assert "10" in result.stdout
        assert "20" in result.stdout
        assert "Total:" in result.stdout

    def test_list_shows_delay(self, setup_db):
        """Test that list shows delay information."""
        now = DateTimeHelper.now_utc()
        problem = ProblemRepository.get_or_create("30", "Delayed Problem")
        ReviewRepository.create(problem, "test", now - timedelta(days=3), 1)
        
        result = runner.invoke(app, ["list"])
        
        assert result.exit_code == 0
        assert "day(s)" in result.stdout

    def test_list_excludes_future_reviews(self, setup_db):
        """Test that future reviews are not listed."""
        now = DateTimeHelper.now_utc()
        problem = ProblemRepository.get_or_create("40", "Future Problem")
        ReviewRepository.create(problem, "test", now + timedelta(days=5), 1)
        
        result = runner.invoke(app, ["list"])
        
        assert result.exit_code == 0
        assert "40" not in result.stdout


class TestReviewCommand:
    """Tests for the 'review' command."""

    def test_review_empty(self, setup_db):
        """Test review command with no data."""
        result = runner.invoke(app, ["review"])
        
        assert result.exit_code == 0
        assert "No reviews found" in result.stdout

    def test_review_with_past_reviews(self, setup_db):
        """Test showing past completed reviews."""
        now = DateTimeHelper.now_utc()
        problem = ProblemRepository.get_or_create("50", "Past Problem")
        review = ReviewRepository.create(
            problem, "test", now - timedelta(days=3), 1
        )
        review.complete(now - timedelta(days=2))
        
        result = runner.invoke(app, ["review"])
        
        assert result.exit_code == 0
        assert "Past Reviews" in result.stdout
        assert "50" in result.stdout

    def test_review_with_future_reviews(self, setup_db):
        """Test showing future scheduled reviews."""
        now = DateTimeHelper.now_utc()
        problem = ProblemRepository.get_or_create("60", "Future Problem")
        ReviewRepository.create(problem, "test", now + timedelta(days=3), 1)
        
        result = runner.invoke(app, ["review"])
        
        assert result.exit_code == 0
        assert "Future Reviews" in result.stdout
        assert "60" in result.stdout

    def test_review_custom_days(self, setup_db):
        """Test review command with custom day range."""
        result = runner.invoke(app, ["review", "--days", "14"])
        
        assert result.exit_code == 0

    def test_review_shows_status(self, setup_db):
        """Test that review shows on-time/delayed status."""
        now = DateTimeHelper.now_utc()
        problem = ProblemRepository.get_or_create("70", "Status Problem")
        
        # On-time review
        review1 = ReviewRepository.create(
            problem, "test1", now - timedelta(days=2), 1
        )
        review1.complete(now - timedelta(days=2))
        
        # Delayed review
        review2 = ReviewRepository.create(
            problem, "test2", now - timedelta(days=5), 2
        )
        review2.complete(now - timedelta(days=3))
        
        result = runner.invoke(app, ["review"])
        
        assert result.exit_code == 0
        assert "On Time" in result.stdout or "Delayed" in result.stdout


class TestStartCommand:
    """Tests for the 'start' command."""

    def test_start_new_session(self, setup_db):
        """Test starting a new timer session."""
        result = runner.invoke(app, ["start", "80"])
        
        assert result.exit_code == 0
        assert "Timer started" in result.stdout
        assert "80" in result.stdout
        
        # Verify session was created
        problem = ProblemRepository.get_by_id("80")
        session = SessionRepository.get_active_session_for_problem(problem)
        assert session is not None

    def test_start_existing_session(self, setup_db, sample_problem):
        """Test starting a session when one already exists."""
        # Create active session
        SessionRepository.create(sample_problem)
        
        result = runner.invoke(app, ["start", "1"])
        
        assert result.exit_code == 0
        assert "already active" in result.stdout.lower()

    def test_start_creates_problem(self, setup_db):
        """Test that start creates problem if it doesn't exist."""
        result = runner.invoke(app, ["start", "999"])
        
        assert result.exit_code == 0
        
        # Verify problem was created
        problem = ProblemRepository.get_by_id("999")
        assert problem is not None


class TestEndCommand:
    """Tests for the 'end' command."""

    def test_end_active_session(self, setup_db, sample_problem):
        """Test ending an active session."""
        # Create active session
        session = SessionRepository.create(sample_problem)
        
        # Create pending review
        now = DateTimeHelper.now_utc()
        ReviewRepository.create(sample_problem, "test", now, 1)
        
        result = runner.invoke(app, ["end", "1"])
        
        assert result.exit_code == 0
        assert "Timer stopped" in result.stdout
        assert "Duration:" in result.stdout
        
        # Verify session was ended
        session = Session.get_by_id(session.id)
        assert session.end_time is not None

    def test_end_no_active_session(self, setup_db, sample_problem):
        """Test ending when no active session exists."""
        result = runner.invoke(app, ["end", "1"])
        
        assert result.exit_code == 0
        assert "No active session" in result.stdout

    def test_end_auto_checkin(self, setup_db, sample_problem):
        """Test that end automatically checks in the review."""
        # Create session and review
        SessionRepository.create(sample_problem)
        now = DateTimeHelper.now_utc()
        review = ReviewRepository.create(sample_problem, "test", now, 1)
        
        result = runner.invoke(app, ["end", "1"])
        
        assert result.exit_code == 0
        assert "Auto-checking in" in result.stdout
        assert "completed" in result.stdout.lower()
        
        # Verify review was completed
        review = Review.get_by_id(review.id)
        assert review.status == "completed"

    def test_end_nonexistent_problem(self, setup_db):
        """Test ending session for nonexistent problem."""
        result = runner.invoke(app, ["end", "999"])
        
        assert result.exit_code == 1
        assert "not found" in result.stdout.lower()


class TestIntegrationScenarios:
    """Integration tests for complete workflows."""

    def test_full_workflow(self, setup_db):
        """Test complete workflow: add -> list -> start -> end -> checkin."""
        # Add problem
        result = runner.invoke(app, ["add", "integration", "--times", "2"])
        assert result.exit_code == 0
        
        # Check it doesn't appear in list (future reviews)
        result = runner.invoke(app, ["list"])
        assert "integration" not in result.stdout or "No reviews due" in result.stdout
        
        # Start session
        result = runner.invoke(app, ["start", "integration"])
        assert result.exit_code == 0
        
        # End session (auto-checkin with orphan since reviews are in future)
        result = runner.invoke(app, ["end", "integration"])
        assert result.exit_code == 0

    def test_cascade_workflow(self, setup_db):
        """Test workflow with delay cascade."""
        now = DateTimeHelper.now_utc()
        
        # Add problem with reviews
        problem = ProblemRepository.get_or_create("cascade", "Cascade Test")
        
        # Create review chain - one overdue, one future
        review1 = ReviewRepository.create(
            problem, "test", now - timedelta(days=3), 1
        )
        review2 = ReviewRepository.create(
            problem, "test", now + timedelta(days=1), 2
        )
        
        # Check in late review
        result = runner.invoke(app, ["checkin", "cascade"])
        assert result.exit_code == 0
        assert "late" in result.stdout.lower()
        assert "Updated" in result.stdout
        
        # Verify cascade effect
        review2 = Review.get_by_id(review2.id)
        assert review2.scheduled_date > now + timedelta(days=1)


class TestErrorHandling:
    """Tests for error handling."""

    def test_invalid_command(self):
        """Test invalid command."""
        result = runner.invoke(app, ["invalid"])
        assert result.exit_code != 0

    def test_missing_argument(self):
        """Test command with missing required argument."""
        result = runner.invoke(app, ["add"])
        assert result.exit_code != 0

    def test_invalid_option_value(self, setup_db):
        """Test command with invalid option value."""
        result = runner.invoke(app, ["add", "test", "--times", "invalid"])
        assert result.exit_code != 0

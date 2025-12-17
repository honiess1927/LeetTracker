"""Repository layer for database operations."""

from typing import List, Optional
from datetime import datetime, date
from peewee import fn

from lcr.models import Problem, Review, Session


class ProblemRepository:
    """Repository for Problem model operations."""

    @staticmethod
    def create(problem_id: str, title: Optional[str] = None) -> Problem:
        """Create a new problem.
        
        Args:
            problem_id: The LeetCode problem identifier
            title: Optional problem title
            
        Returns:
            The created Problem instance
        """
        return Problem.create(problem_id=problem_id, title=title)

    @staticmethod
    def get_by_id(problem_id: str) -> Optional[Problem]:
        """Get a problem by its ID.
        
        Args:
            problem_id: The problem identifier
            
        Returns:
            The Problem instance or None if not found
        """
        try:
            return Problem.get(Problem.problem_id == problem_id)
        except Problem.DoesNotExist:
            return None

    @staticmethod
    def get_or_create(problem_id: str, title: Optional[str] = None) -> Problem:
        """Get an existing problem or create it if it doesn't exist.
        
        Parses the title to extract difficulty and clean title, storing them separately.
        
        Args:
            problem_id: The problem identifier
            title: Optional problem title (may include difficulty prefix like "(E) Two Sum")
            
        Returns:
            The Problem instance
        """
        # Import here to avoid circular dependency
        from lcr.utils import TitleParser
        
        # Parse title to extract difficulty and clean title
        if title:
            difficulty, clean_title = TitleParser.parse_title(title)
            difficulty_letter = TitleParser.difficulty_to_letter(difficulty)
        else:
            clean_title = None
            difficulty_letter = None
        
        problem, created = Problem.get_or_create(
            problem_id=problem_id,
            defaults={
                "title": clean_title,
                "difficulty": difficulty_letter
            }
        )
        
        # Update if exists and title provided
        if not created and title:
            problem.title = clean_title
            problem.difficulty = difficulty_letter
            problem.save()
        
        return problem

    @staticmethod
    def get_all() -> List[Problem]:
        """Get all problems.
        
        Returns:
            List of all Problem instances
        """
        return list(Problem.select())


class ReviewRepository:
    """Repository for Review model operations."""

    @staticmethod
    def create(
        problem: Problem,
        chain_id: str,
        scheduled_date: datetime,
        iteration_number: int = 1,
    ) -> Review:
        """Create a new review.
        
        Args:
            problem: The Problem instance
            chain_id: Chain identifier for related reviews
            scheduled_date: When the review is scheduled
            iteration_number: Which iteration this is
            
        Returns:
            The created Review instance
        """
        return Review.create(
            problem=problem,
            chain_id=chain_id,
            scheduled_date=scheduled_date,
            iteration_number=iteration_number,
        )

    @staticmethod
    def get_pending_for_problem(problem: Problem) -> List[Review]:
        """Get all pending reviews for a problem.
        
        Args:
            problem: The Problem instance
            
        Returns:
            List of pending Review instances, sorted by scheduled date
        """
        return list(
            Review.select()
            .where((Review.problem == problem) & (Review.status == "pending"))
            .order_by(Review.scheduled_date)
        )

    @staticmethod
    def get_earliest_pending_for_problem(problem: Problem) -> Optional[Review]:
        """Get the earliest pending review for a problem.
        
        Args:
            problem: The Problem instance
            
        Returns:
            The earliest pending Review or None
        """
        try:
            return (
                Review.select()
                .where((Review.problem == problem) & (Review.status == "pending"))
                .order_by(Review.scheduled_date)
                .get()
            )
        except Review.DoesNotExist:
            return None

    @staticmethod
    def get_due_reviews(as_of_date: Optional[datetime] = None) -> List[Review]:
        """Get all reviews that are due (scheduled on or before today's date in local time).
        
        Compares by DATE in local timezone, so all reviews scheduled for today (local time)
        will appear regardless of their specific time.
        
        Args:
            as_of_date: Date to check against (defaults to now in UTC)
            
        Returns:
            List of due Review instances, sorted by scheduled date
        """
        from lcr.utils import DateTimeHelper
        
        # Use DateTimeHelper to get end of today in local time, expressed as UTC
        # This allows us to match all reviews scheduled for "today" in the user's timezone
        end_of_today_utc = DateTimeHelper.end_of_today_local_in_utc(as_of_date)
        
        # Get all reviews scheduled up to end of today (in local timezone)
        return list(
            Review.select()
            .where((Review.status == "pending") & (Review.scheduled_date <= end_of_today_utc))
            .order_by(Review.scheduled_date)
        )

    @staticmethod
    def get_future_reviews_in_chain(
        chain_id: str, after_iteration: int
    ) -> List[Review]:
        """Get all future pending reviews in a chain after a specific iteration.
        
        Args:
            chain_id: The chain identifier
            after_iteration: Get reviews after this iteration number
            
        Returns:
            List of Review instances
        """
        return list(
            Review.select()
            .where(
                (Review.chain_id == chain_id)
                & (Review.status == "pending")
                & (Review.iteration_number > after_iteration)
            )
            .order_by(Review.iteration_number)
        )

    @staticmethod
    def check_duplicate(
        problem: Problem, scheduled_date: datetime, chain_id: str
    ) -> Optional[Review]:
        """Check if a review already exists for this date.
        
        Args:
            problem: The Problem instance
            scheduled_date: The scheduled date to check
            chain_id: The chain identifier
            
        Returns:
            Existing Review or None
        """
        # Convert datetime to date for comparison
        scheduled_date_only = scheduled_date.date()

        try:
            return (
                Review.select()
                .where(
                    (Review.problem == problem)
                    & (Review.chain_id == chain_id)
                    & (Review.status == "pending")
                    & (fn.DATE(Review.scheduled_date) == scheduled_date_only)
                )
                .get()
            )
        except Review.DoesNotExist:
            return None

    @staticmethod
    def get_completed_reviews(
        start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> List[Review]:
        """Get completed reviews within a date range.
        
        Args:
            start_date: Start of date range (optional)
            end_date: End of date range (optional)
            
        Returns:
            List of completed Review instances
        """
        query = Review.select().where(Review.status == "completed")

        if start_date:
            query = query.where(Review.actual_completion_date >= start_date)
        if end_date:
            query = query.where(Review.actual_completion_date <= end_date)

        return list(query.order_by(Review.actual_completion_date.desc()))


class SessionRepository:
    """Repository for Session model operations."""

    @staticmethod
    def create(problem: Problem, start_time: Optional[datetime] = None) -> Session:
        """Create a new session.
        
        Args:
            problem: The Problem instance
            start_time: When the session started (defaults to now in UTC)
            
        Returns:
            The created Session instance
        """
        if start_time is None:
            from datetime import timezone
            start_time = datetime.now(timezone.utc)

        return Session.create(problem=problem, start_time=start_time, status="active")

    @staticmethod
    def get_active_session_for_problem(problem: Problem) -> Optional[Session]:
        """Get the active session for a problem.
        
        Args:
            problem: The Problem instance
            
        Returns:
            The active Session or None
        """
        try:
            return Session.get(
                (Session.problem == problem) & (Session.status == "active")
            )
        except Session.DoesNotExist:
            return None

    @staticmethod
    def get_sessions_for_problem(problem: Problem) -> List[Session]:
        """Get all sessions for a problem.
        
        Args:
            problem: The Problem instance
            
        Returns:
            List of Session instances, sorted by start time descending
        """
        return list(
            Session.select()
            .where(Session.problem == problem)
            .order_by(Session.start_time.desc())
        )

    @staticmethod
    def get_completed_sessions(
        start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> List[Session]:
        """Get completed sessions within a date range.
        
        Args:
            start_date: Start of date range (optional)
            end_date: End of date range (optional)
            
        Returns:
            List of completed Session instances
        """
        query = Session.select().where(Session.status == "completed")

        if start_date:
            query = query.where(Session.end_time >= start_date)
        if end_date:
            query = query.where(Session.end_time <= end_date)

        return list(query.order_by(Session.end_time.desc()))

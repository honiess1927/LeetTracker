"""Review model for tracking scheduled and completed reviews."""

from peewee import (
    CharField,
    DateTimeField,
    ForeignKeyField,
    IntegerField,
)
from datetime import datetime
from .base import BaseModel
from .problem import Problem


class Review(BaseModel):
    """Model representing a scheduled or completed review.
    
    Attributes:
        problem: Foreign key reference to the Problem being reviewed
        chain_id: UUID linking related reviews for cascade delay updates
        scheduled_date: When this review is scheduled to occur
        actual_completion_date: When the review was actually completed (nullable)
        status: Current status ('pending' or 'completed')
        iteration_number: Which review this is (1st, 2nd, 3rd, etc.)
        created_at: Timestamp when the review was created
        updated_at: Timestamp when the review was last updated
    """

    problem = ForeignKeyField(Problem, backref="reviews", on_delete="CASCADE")
    chain_id = CharField(index=True, max_length=50)
    scheduled_date = DateTimeField(index=True)
    actual_completion_date = DateTimeField(null=True)
    status = CharField(
        max_length=20, default="pending", index=True
    )  # 'pending' or 'completed'
    iteration_number = IntegerField(default=1)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = "reviews"
        indexes = (
            # Composite index for efficient queries
            (("problem", "status", "scheduled_date"), False),
            (("chain_id", "iteration_number"), False),
        )

    def __str__(self) -> str:
        """String representation of the review."""
        status_str = "✓" if self.status == "completed" else "○"
        return (
            f"{status_str} Review #{self.iteration_number} for "
            f"Problem {self.problem.problem_id} on {self.scheduled_date.date()}"
        )

    def save(self, *args, **kwargs) -> int:
        """Override save to update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def complete(self, completion_date: datetime = None) -> None:
        """Mark this review as completed.
        
        Args:
            completion_date: When the review was completed (defaults to now)
        """
        self.status = "completed"
        self.actual_completion_date = completion_date or datetime.utcnow()
        self.save()

    def is_overdue(self) -> bool:
        """Check if this review is overdue.
        
        Returns:
            True if the review is pending and past its scheduled date
        """
        if self.status != "pending":
            return False
        return datetime.utcnow() > self.scheduled_date

    def delay_days(self) -> int:
        """Calculate how many days this review was delayed.
        
        Returns:
            Number of days between scheduled and actual completion.
            Returns 0 if completed on time or not yet completed.
        """
        if not self.actual_completion_date:
            return 0
        delta = self.actual_completion_date - self.scheduled_date
        return max(0, delta.days)

"""Problem model for tracking LeetCode problems."""

from peewee import CharField, DateTimeField
from datetime import datetime
from .base import BaseModel


class Problem(BaseModel):
    """Model representing a LeetCode problem.
    
    Attributes:
        problem_id: The LeetCode problem identifier (e.g., '1', '42', '100')
        title: Optional problem title for reference
        created_at: Timestamp when the problem was first registered
        updated_at: Timestamp when the problem was last updated
    """

    problem_id = CharField(unique=True, index=True, max_length=50)
    title = CharField(null=True, max_length=255)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = "problems"

    def __str__(self) -> str:
        """String representation of the problem."""
        if self.title:
            return f"Problem {self.problem_id}: {self.title}"
        return f"Problem {self.problem_id}"

    def save(self, *args, **kwargs) -> int:
        """Override save to update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

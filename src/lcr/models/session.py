"""Session model for tracking problem-solving time."""

from peewee import CharField, DateTimeField, ForeignKeyField, IntegerField
from datetime import datetime
from .base import BaseModel
from .problem import Problem


class Session(BaseModel):
    """Model representing a timed problem-solving session.
    
    Attributes:
        problem: Foreign key reference to the Problem being worked on
        start_time: When the timer was started
        end_time: When the timer was stopped (nullable for active sessions)
        duration: Duration in seconds (calculated when session ends)
        status: Current status ('active' or 'completed')
        created_at: Timestamp when the session was created
        updated_at: Timestamp when the session was last updated
    """

    problem = ForeignKeyField(Problem, backref="sessions", on_delete="CASCADE")
    start_time = DateTimeField(index=True)
    end_time = DateTimeField(null=True)
    duration = IntegerField(null=True)  # Duration in seconds
    status = CharField(
        max_length=20, default="active", index=True
    )  # 'active' or 'completed'
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = "sessions"
        indexes = ((("problem", "status"), False),)

    def __str__(self) -> str:
        """String representation of the session."""
        if self.status == "active":
            return f"Active session for Problem {self.problem.problem_id}"
        duration_str = self.format_duration()
        return f"Session for Problem {self.problem.problem_id}: {duration_str}"

    def save(self, *args, **kwargs) -> int:
        """Override save to update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def end(self, end_time: datetime = None) -> None:
        """End the session and calculate duration.
        
        Args:
            end_time: When the session ended (defaults to now)
        """
        if self.status == "completed":
            return

        self.end_time = end_time or datetime.utcnow()
        self.duration = int((self.end_time - self.start_time).total_seconds())
        self.status = "completed"
        self.save()

    def format_duration(self) -> str:
        """Format the duration as a human-readable string.
        
        Returns:
            Formatted duration string (e.g., "1h 23m" or "45m 30s")
        """
        if not self.duration:
            return "0s"

        hours = self.duration // 3600
        minutes = (self.duration % 3600) // 60
        seconds = self.duration % 60

        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if seconds > 0 or not parts:
            parts.append(f"{seconds}s")

        return " ".join(parts)

    def get_current_duration(self) -> int:
        """Get the current duration in seconds.
        
        For active sessions, calculates time elapsed since start.
        For completed sessions, returns the stored duration.
        
        Returns:
            Duration in seconds
        """
        if self.status == "completed":
            return self.duration or 0

        elapsed = datetime.utcnow() - self.start_time
        return int(elapsed.total_seconds())

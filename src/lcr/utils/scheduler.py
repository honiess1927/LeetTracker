"""Spaced repetition scheduler for LeetCode review intervals.

This module implements a customizable spaced repetition algorithm based on
research showing optimal learning intervals. The default intervals are designed
for coding problem review, but can be customized for different use cases.
"""

import random
from datetime import datetime, timedelta
from typing import List, Optional


class SpacedRepetitionScheduler:
    """Scheduler for generating spaced repetition review dates.
    
    The scheduler uses a set of base intervals with optional randomization to
    prevent clustering of reviews on the same day. Intervals can be clamped
    to enforce minimum and maximum values.
    
    Default intervals: [1, 7, 18, 35] days
    These intervals are based on the forgetting curve and provide optimal
    spacing for long-term retention.
    """

    def __init__(
        self,
        base_intervals: Optional[List[int]] = None,
        randomization_percentage: float = 15.0,
        min_interval: int = 1,
        max_interval: int = 365,
    ):
        """Initialize the spaced repetition scheduler.
        
        Args:
            base_intervals: List of base intervals in days. Defaults to [1, 7, 18, 35].
            randomization_percentage: Percentage of randomization to apply (0-100).
                                     Default is 15%, meaning intervals can vary by ±15%.
            min_interval: Minimum allowed interval in days. Default is 1.
            max_interval: Maximum allowed interval in days. Default is 365.
        """
        # Validate empty list explicitly before defaulting
        if base_intervals is not None and len(base_intervals) == 0:
            raise ValueError("base_intervals cannot be empty")
            
        self.base_intervals = base_intervals or [1, 7, 18, 35]
        self.randomization_percentage = randomization_percentage
        self.min_interval = min_interval
        self.max_interval = max_interval

        # Validate inputs
        if not all(isinstance(i, int) and i > 0 for i in self.base_intervals):
            raise ValueError("All base_intervals must be positive integers")
        if not 0 <= randomization_percentage <= 100:
            raise ValueError("randomization_percentage must be between 0 and 100")
        if min_interval < 1:
            raise ValueError("min_interval must be at least 1")
        if max_interval < min_interval:
            raise ValueError("max_interval must be >= min_interval")

    def get_interval(self, iteration: int, apply_randomization: bool = True) -> int:
        """Get the interval for a specific iteration.
        
        Args:
            iteration: The iteration number (0-indexed). For example:
                      0 = first review, 1 = second review, etc.
            apply_randomization: Whether to apply randomization to the interval.
                               Default is True.
        
        Returns:
            The interval in days for the given iteration, with randomization
            and clamping applied if enabled.
            
        Raises:
            ValueError: If iteration is negative.
        """
        if iteration < 0:
            raise ValueError("iteration must be non-negative")

        # Use the last interval if iteration exceeds available intervals
        if iteration >= len(self.base_intervals):
            base_interval = self.base_intervals[-1]
        else:
            base_interval = self.base_intervals[iteration]

        # Apply randomization if enabled
        if apply_randomization and self.randomization_percentage > 0:
            interval = self._apply_randomization(base_interval)
        else:
            interval = base_interval

        # Clamp to min/max bounds
        interval = max(self.min_interval, min(interval, self.max_interval))

        return interval

    def _apply_randomization(self, base_interval: int) -> int:
        """Apply randomization to a base interval.
        
        Args:
            base_interval: The base interval in days.
            
        Returns:
            The randomized interval, rounded to nearest integer.
        """
        # Calculate the randomization range
        variation = base_interval * (self.randomization_percentage / 100.0)

        # Apply random variation within ±variation
        randomized = base_interval + random.uniform(-variation, variation)

        # Round to nearest integer and ensure at least 1
        return max(1, round(randomized))

    def generate_schedule(
        self,
        start_date: datetime,
        num_reviews: Optional[int] = None,
        apply_randomization: bool = True,
    ) -> List[datetime]:
        """Generate a complete review schedule.
        
        Args:
            start_date: The starting date for the schedule.
            num_reviews: Number of reviews to generate. If None, generates
                        one review for each base interval.
            apply_randomization: Whether to apply randomization to intervals.
                               Default is True.
        
        Returns:
            List of datetime objects representing scheduled review dates.
            
        Raises:
            ValueError: If num_reviews is less than 1.
        """
        if num_reviews is None:
            num_reviews = len(self.base_intervals)
        elif num_reviews < 1:
            raise ValueError("num_reviews must be at least 1")

        schedule = []
        current_date = start_date

        for iteration in range(num_reviews):
            interval = self.get_interval(iteration, apply_randomization)
            next_date = current_date + timedelta(days=interval)
            schedule.append(next_date)
            current_date = next_date

        return schedule

    def get_next_review_date(
        self,
        last_review_date: datetime,
        iteration: int,
        apply_randomization: bool = True,
    ) -> datetime:
        """Calculate the next review date based on the last review.
        
        Args:
            last_review_date: The date of the last review.
            iteration: The iteration number for the next review.
            apply_randomization: Whether to apply randomization.
                               Default is True.
        
        Returns:
            The datetime for the next scheduled review.
        """
        interval = self.get_interval(iteration, apply_randomization)
        return last_review_date + timedelta(days=interval)


# Default scheduler instance with standard intervals
default_scheduler = SpacedRepetitionScheduler()

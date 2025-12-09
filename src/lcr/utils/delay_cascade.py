"""Delay cascade algorithm for updating future review dates.

This module implements the delay cascade mechanism that automatically adjusts
future review dates when a review is completed late. This ensures that the
spacing between reviews remains optimal even when reviews are delayed.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from lcr.models import Review
from lcr.database.repository import ReviewRepository


class DelayCascade:
    """Handles cascading delays to future reviews in a chain.
    
    When a review is completed late, all subsequent pending reviews in the
    same chain are shifted by the delay amount to maintain proper spacing.
    """

    @staticmethod
    def calculate_delay(
        scheduled_date: datetime, actual_completion_date: datetime
    ) -> int:
        """Calculate the delay in days between scheduled and actual completion.
        
        Args:
            scheduled_date: When the review was scheduled.
            actual_completion_date: When the review was actually completed.
            
        Returns:
            Number of days delayed (positive if late, 0 if on time or early).
        """
        delta = actual_completion_date - scheduled_date
        # Only count positive delays (late completions)
        return max(0, delta.days)

    @staticmethod
    def apply_cascade(
        completed_review: Review,
        actual_completion_date: Optional[datetime] = None,
    ) -> int:
        """Apply delay cascade to all future reviews in the chain.
        
        Args:
            completed_review: The review that was just completed.
            actual_completion_date: When the review was completed. If None,
                                   uses the review's actual_completion_date.
            
        Returns:
            Number of future reviews that were updated.
            
        Raises:
            ValueError: If the review is not completed or has no actual completion date.
        """
        # Use provided date or get from review
        completion_date = actual_completion_date or completed_review.actual_completion_date
        
        if not completion_date:
            raise ValueError("Review must have an actual_completion_date")
        
        if completed_review.status != "completed":
            raise ValueError("Review must be completed before applying cascade")

        # Calculate delay
        delay_days = DelayCascade.calculate_delay(
            completed_review.scheduled_date, completion_date
        )

        # If no delay, no cascade needed
        if delay_days == 0:
            return 0

        # Get all future pending reviews in the same chain
        future_reviews = ReviewRepository.get_future_reviews_in_chain(
            completed_review.chain_id, completed_review.iteration_number
        )

        # Update each future review
        updated_count = 0
        for review in future_reviews:
            review.scheduled_date = review.scheduled_date + timedelta(days=delay_days)
            review.save()
            updated_count += 1

        return updated_count

    @staticmethod
    def preview_cascade(
        completed_review: Review,
        actual_completion_date: Optional[datetime] = None,
    ) -> List[dict]:
        """Preview the cascade effect without applying it.
        
        Args:
            completed_review: The review that would be completed.
            actual_completion_date: When the review would be completed.
            
        Returns:
            List of dictionaries containing preview information:
            [
                {
                    'review_id': int,
                    'iteration': int,
                    'old_date': datetime,
                    'new_date': datetime,
                    'delay_days': int
                },
                ...
            ]
        """
        completion_date = actual_completion_date or completed_review.actual_completion_date
        
        if not completion_date:
            return []

        # Calculate delay
        delay_days = DelayCascade.calculate_delay(
            completed_review.scheduled_date, completion_date
        )

        if delay_days == 0:
            return []

        # Get future reviews
        future_reviews = ReviewRepository.get_future_reviews_in_chain(
            completed_review.chain_id, completed_review.iteration_number
        )

        # Build preview
        preview = []
        for review in future_reviews:
            new_date = review.scheduled_date + timedelta(days=delay_days)
            preview.append({
                'review_id': review.id,
                'iteration': review.iteration_number,
                'old_date': review.scheduled_date,
                'new_date': new_date,
                'delay_days': delay_days,
            })

        return preview

    @staticmethod
    def calculate_total_delay_in_chain(chain_id: str) -> int:
        """Calculate the total accumulated delay for all completed reviews in a chain.
        
        Args:
            chain_id: The chain identifier.
            
        Returns:
            Total delay in days across all completed reviews in the chain.
        """
        from lcr.models import Review
        
        # Get all completed reviews in the chain
        completed_reviews = list(
            Review.select()
            .where(
                (Review.chain_id == chain_id) & (Review.status == "completed")
            )
            .order_by(Review.iteration_number)
        )

        total_delay = 0
        for review in completed_reviews:
            if review.actual_completion_date:
                delay = DelayCascade.calculate_delay(
                    review.scheduled_date, review.actual_completion_date
                )
                total_delay += delay

        return total_delay

    @staticmethod
    def get_cascade_statistics(chain_id: str) -> dict:
        """Get statistical information about delays in a chain.
        
        Args:
            chain_id: The chain identifier.
            
        Returns:
            Dictionary with cascade statistics:
            {
                'total_reviews': int,
                'completed_reviews': int,
                'pending_reviews': int,
                'total_delay_days': int,
                'average_delay_days': float,
                'max_delay_days': int,
                'reviews_with_delay': int
            }
        """
        from lcr.models import Review
        
        all_reviews = list(
            Review.select()
            .where(Review.chain_id == chain_id)
            .order_by(Review.iteration_number)
        )

        if not all_reviews:
            return {
                'total_reviews': 0,
                'completed_reviews': 0,
                'pending_reviews': 0,
                'total_delay_days': 0,
                'average_delay_days': 0.0,
                'max_delay_days': 0,
                'reviews_with_delay': 0,
            }

        completed = [r for r in all_reviews if r.status == "completed"]
        pending = [r for r in all_reviews if r.status == "pending"]

        delays = []
        for review in completed:
            if review.actual_completion_date:
                delay = DelayCascade.calculate_delay(
                    review.scheduled_date, review.actual_completion_date
                )
                delays.append(delay)

        total_delay = sum(delays)
        reviews_with_delay = sum(1 for d in delays if d > 0)
        
        return {
            'total_reviews': len(all_reviews),
            'completed_reviews': len(completed),
            'pending_reviews': len(pending),
            'total_delay_days': total_delay,
            'average_delay_days': total_delay / len(delays) if delays else 0.0,
            'max_delay_days': max(delays) if delays else 0,
            'reviews_with_delay': reviews_with_delay,
        }

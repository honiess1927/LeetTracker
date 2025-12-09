"""Tests for spaced repetition scheduler."""

import pytest
import random
from datetime import datetime, timedelta

from lcr.utils.scheduler import SpacedRepetitionScheduler


class TestSpacedRepetitionScheduler:
    """Tests for SpacedRepetitionScheduler class."""

    def test_init_default_values(self):
        """Test initialization with default values."""
        scheduler = SpacedRepetitionScheduler()
        assert scheduler.base_intervals == [1, 7, 18, 35]
        assert scheduler.randomization_percentage == 15.0
        assert scheduler.min_interval == 1
        assert scheduler.max_interval == 365

    def test_init_custom_values(self):
        """Test initialization with custom values."""
        scheduler = SpacedRepetitionScheduler(
            base_intervals=[2, 5, 10],
            randomization_percentage=20.0,
            min_interval=2,
            max_interval=100,
        )
        assert scheduler.base_intervals == [2, 5, 10]
        assert scheduler.randomization_percentage == 20.0
        assert scheduler.min_interval == 2
        assert scheduler.max_interval == 100

    def test_init_validation_empty_intervals(self):
        """Test that empty intervals raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            SpacedRepetitionScheduler(base_intervals=[])

    def test_init_validation_invalid_intervals(self):
        """Test that invalid intervals raise ValueError."""
        with pytest.raises(ValueError, match="must be positive integers"):
            SpacedRepetitionScheduler(base_intervals=[1, -5, 10])

        with pytest.raises(ValueError, match="must be positive integers"):
            SpacedRepetitionScheduler(base_intervals=[1.5, 2, 3])

    def test_init_validation_randomization_percentage(self):
        """Test randomization percentage validation."""
        with pytest.raises(ValueError, match="must be between 0 and 100"):
            SpacedRepetitionScheduler(randomization_percentage=-5)

        with pytest.raises(ValueError, match="must be between 0 and 100"):
            SpacedRepetitionScheduler(randomization_percentage=150)

    def test_init_validation_min_interval(self):
        """Test min_interval validation."""
        with pytest.raises(ValueError, match="must be at least 1"):
            SpacedRepetitionScheduler(min_interval=0)

    def test_init_validation_max_interval(self):
        """Test max_interval validation."""
        with pytest.raises(ValueError, match="must be >= min_interval"):
            SpacedRepetitionScheduler(min_interval=10, max_interval=5)

    def test_get_interval_without_randomization(self):
        """Test getting intervals without randomization."""
        scheduler = SpacedRepetitionScheduler()

        assert scheduler.get_interval(0, apply_randomization=False) == 1
        assert scheduler.get_interval(1, apply_randomization=False) == 7
        assert scheduler.get_interval(2, apply_randomization=False) == 18
        assert scheduler.get_interval(3, apply_randomization=False) == 35

    def test_get_interval_beyond_available(self):
        """Test getting interval beyond available intervals."""
        scheduler = SpacedRepetitionScheduler()

        # Should use last interval (35) for iterations beyond available
        assert scheduler.get_interval(4, apply_randomization=False) == 35
        assert scheduler.get_interval(10, apply_randomization=False) == 35

    def test_get_interval_negative_iteration(self):
        """Test that negative iteration raises ValueError."""
        scheduler = SpacedRepetitionScheduler()

        with pytest.raises(ValueError, match="must be non-negative"):
            scheduler.get_interval(-1)

    def test_get_interval_with_randomization(self):
        """Test that randomization produces values within expected range."""
        scheduler = SpacedRepetitionScheduler(
            base_intervals=[10], randomization_percentage=20.0
        )

        # Set seed for reproducibility
        random.seed(42)

        # Test multiple iterations to ensure randomization is working
        intervals = [scheduler.get_interval(0, apply_randomization=True) for _ in range(100)]

        # All intervals should be within ±20% of 10 (8-12)
        # and clamped to at least 1
        assert all(1 <= i <= 12 for i in intervals)
        # Should have some variation
        assert len(set(intervals)) > 1

    def test_get_interval_randomization_distribution(self):
        """Test that randomization follows expected distribution."""
        scheduler = SpacedRepetitionScheduler(
            base_intervals=[100], randomization_percentage=15.0
        )

        random.seed(42)
        intervals = [scheduler.get_interval(0, apply_randomization=True) for _ in range(1000)]

        # Mean should be close to 100
        mean = sum(intervals) / len(intervals)
        assert 95 <= mean <= 105

        # Should have good spread within ±15% (85-115)
        assert min(intervals) >= 85
        assert max(intervals) <= 115

    def test_get_interval_clamping_min(self):
        """Test that intervals are clamped to min_interval."""
        scheduler = SpacedRepetitionScheduler(
            base_intervals=[1], randomization_percentage=50.0, min_interval=5
        )

        random.seed(42)
        intervals = [scheduler.get_interval(0, apply_randomization=True) for _ in range(100)]

        # All should be >= min_interval
        assert all(i >= 5 for i in intervals)

    def test_get_interval_clamping_max(self):
        """Test that intervals are clamped to max_interval."""
        scheduler = SpacedRepetitionScheduler(
            base_intervals=[100], randomization_percentage=50.0, max_interval=50
        )

        random.seed(42)
        intervals = [scheduler.get_interval(0, apply_randomization=True) for _ in range(100)]

        # All should be <= max_interval
        assert all(i <= 50 for i in intervals)

    def test_generate_schedule_default(self):
        """Test generating a schedule with default settings."""
        scheduler = SpacedRepetitionScheduler()
        start_date = datetime(2024, 1, 1, 12, 0, 0)

        schedule = scheduler.generate_schedule(start_date, apply_randomization=False)

        # Should generate 4 reviews (one for each base interval)
        assert len(schedule) == 4

        # Verify dates
        assert schedule[0] == datetime(2024, 1, 2, 12, 0, 0)  # +1 day
        assert schedule[1] == datetime(2024, 1, 9, 12, 0, 0)  # +7 days
        assert schedule[2] == datetime(2024, 1, 27, 12, 0, 0)  # +18 days
        assert schedule[3] == datetime(2024, 3, 2, 12, 0, 0)  # +35 days (2024 is leap year, Feb has 29 days)

    def test_generate_schedule_custom_num_reviews(self):
        """Test generating schedule with custom number of reviews."""
        scheduler = SpacedRepetitionScheduler()
        start_date = datetime(2024, 1, 1, 12, 0, 0)

        schedule = scheduler.generate_schedule(
            start_date, num_reviews=2, apply_randomization=False
        )

        assert len(schedule) == 2
        assert schedule[0] == datetime(2024, 1, 2, 12, 0, 0)
        assert schedule[1] == datetime(2024, 1, 9, 12, 0, 0)

    def test_generate_schedule_invalid_num_reviews(self):
        """Test that invalid num_reviews raises ValueError."""
        scheduler = SpacedRepetitionScheduler()
        start_date = datetime(2024, 1, 1, 12, 0, 0)

        with pytest.raises(ValueError, match="must be at least 1"):
            scheduler.generate_schedule(start_date, num_reviews=0)

    def test_generate_schedule_with_randomization(self):
        """Test that schedule generation with randomization works."""
        scheduler = SpacedRepetitionScheduler()
        start_date = datetime(2024, 1, 1, 12, 0, 0)

        random.seed(42)
        schedule = scheduler.generate_schedule(start_date, apply_randomization=True)

        # Should have 4 reviews
        assert len(schedule) == 4

        # All should be after start_date
        assert all(date > start_date for date in schedule)

        # Should be in chronological order
        for i in range(len(schedule) - 1):
            assert schedule[i] < schedule[i + 1]

    def test_get_next_review_date(self):
        """Test calculating next review date."""
        scheduler = SpacedRepetitionScheduler()
        last_review = datetime(2024, 1, 1, 12, 0, 0)

        # Test each iteration
        next_date = scheduler.get_next_review_date(
            last_review, iteration=0, apply_randomization=False
        )
        assert next_date == datetime(2024, 1, 2, 12, 0, 0)

        next_date = scheduler.get_next_review_date(
            last_review, iteration=1, apply_randomization=False
        )
        assert next_date == datetime(2024, 1, 8, 12, 0, 0)

        next_date = scheduler.get_next_review_date(
            last_review, iteration=2, apply_randomization=False
        )
        assert next_date == datetime(2024, 1, 19, 12, 0, 0)

    def test_default_scheduler(self):
        """Test that default scheduler instance exists and works."""
        from lcr.utils.scheduler import default_scheduler

        assert isinstance(default_scheduler, SpacedRepetitionScheduler)
        assert default_scheduler.base_intervals == [1, 7, 18, 35]

        # Test it works
        interval = default_scheduler.get_interval(0, apply_randomization=False)
        assert interval == 1

    def test_zero_randomization(self):
        """Test scheduler with 0% randomization."""
        scheduler = SpacedRepetitionScheduler(
            base_intervals=[10], randomization_percentage=0.0
        )

        # With 0% randomization, should always return base interval
        intervals = [scheduler.get_interval(0, apply_randomization=True) for _ in range(10)]
        assert all(i == 10 for i in intervals)

    def test_edge_case_single_interval(self):
        """Test scheduler with only one base interval."""
        scheduler = SpacedRepetitionScheduler(base_intervals=[5])

        # All iterations should use this interval
        assert scheduler.get_interval(0, apply_randomization=False) == 5
        assert scheduler.get_interval(5, apply_randomization=False) == 5
        assert scheduler.get_interval(100, apply_randomization=False) == 5

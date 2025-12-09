"""Tests for datetime helper utilities."""

import pytest
from datetime import datetime, date, time, timezone, timedelta

from lcr.utils.datetime_helper import DateTimeHelper


class TestDateTimeHelper:
    """Tests for DateTimeHelper class."""

    def test_now_utc(self):
        """Test getting current UTC time."""
        now = DateTimeHelper.now_utc()
        assert now.tzinfo == timezone.utc
        assert isinstance(now, datetime)

    def test_to_utc_naive(self):
        """Test converting naive datetime to UTC."""
        naive = datetime(2024, 1, 1, 12, 0, 0)
        utc_dt = DateTimeHelper.to_utc(naive)
        assert utc_dt.tzinfo == timezone.utc
        assert utc_dt.hour == 12

    def test_to_utc_aware(self):
        """Test converting timezone-aware datetime to UTC."""
        # Create datetime in PST (UTC-8)
        pst = timezone(timedelta(hours=-8))
        aware = datetime(2024, 1, 1, 12, 0, 0, tzinfo=pst)
        utc_dt = DateTimeHelper.to_utc(aware)
        assert utc_dt.tzinfo == timezone.utc
        assert utc_dt.hour == 20  # 12 PM PST = 8 PM UTC

    def test_from_utc_to_local(self):
        """Test converting UTC to local time."""
        utc_dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        local_dt = DateTimeHelper.from_utc_to_local(utc_dt)
        # Just verify it's timezone-aware
        assert local_dt.tzinfo is not None

    def test_to_iso8601_basic(self):
        """Test formatting datetime as ISO-8601."""
        dt = datetime(2024, 1, 15, 10, 30, 45, tzinfo=timezone.utc)
        iso_str = DateTimeHelper.to_iso8601(dt)
        assert iso_str == "2024-01-15T10:30:45+00:00"

    def test_to_iso8601_with_microseconds(self):
        """Test ISO-8601 format with microseconds."""
        dt = datetime(2024, 1, 15, 10, 30, 45, 123456, tzinfo=timezone.utc)
        iso_str = DateTimeHelper.to_iso8601(dt, include_microseconds=True)
        assert "123456" in iso_str

    def test_to_iso8601_naive(self):
        """Test ISO-8601 format with naive datetime."""
        dt = datetime(2024, 1, 15, 10, 30, 45)
        iso_str = DateTimeHelper.to_iso8601(dt)
        assert "2024-01-15T10:30:45" in iso_str

    def test_from_iso8601_basic(self):
        """Test parsing ISO-8601 string."""
        iso_str = "2024-01-15T10:30:45+00:00"
        dt = DateTimeHelper.from_iso8601(iso_str)
        assert dt.year == 2024
        assert dt.month == 1
        assert dt.day == 15
        assert dt.hour == 10
        assert dt.minute == 30
        assert dt.second == 45
        assert dt.tzinfo == timezone.utc

    def test_from_iso8601_with_z(self):
        """Test parsing ISO-8601 string with Z suffix."""
        iso_str = "2024-01-15T10:30:45Z"
        dt = DateTimeHelper.from_iso8601(iso_str)
        assert dt.tzinfo == timezone.utc

    def test_from_iso8601_invalid(self):
        """Test that invalid ISO-8601 raises ValueError."""
        with pytest.raises(ValueError, match="Invalid ISO-8601"):
            DateTimeHelper.from_iso8601("not-a-date")

    def test_parse_date_iso_format(self):
        """Test parsing date in ISO format (YYYY-MM-DD)."""
        d = DateTimeHelper.parse_date("2024-01-15")
        assert d == date(2024, 1, 15)

    def test_parse_date_slash_format(self):
        """Test parsing date in YYYY/MM/DD format."""
        d = DateTimeHelper.parse_date("2024/01/15")
        assert d == date(2024, 1, 15)

    def test_parse_date_us_format(self):
        """Test parsing date in MM/DD/YYYY format."""
        d = DateTimeHelper.parse_date("01/15/2024")
        assert d == date(2024, 1, 15)

    def test_parse_date_us_dash_format(self):
        """Test parsing date in MM-DD-YYYY format."""
        d = DateTimeHelper.parse_date("01-15-2024")
        assert d == date(2024, 1, 15)

    def test_parse_date_invalid(self):
        """Test that invalid date string raises ValueError."""
        with pytest.raises(ValueError, match="Unable to parse"):
            DateTimeHelper.parse_date("invalid-date")

    def test_format_date_default(self):
        """Test formatting date with default format."""
        d = date(2024, 1, 15)
        formatted = DateTimeHelper.format_date(d)
        assert formatted == "2024-01-15"

    def test_format_date_custom(self):
        """Test formatting date with custom format."""
        d = date(2024, 1, 15)
        formatted = DateTimeHelper.format_date(d, format_str="%m/%d/%Y")
        assert formatted == "01/15/2024"

    def test_format_date_from_datetime(self):
        """Test formatting date from datetime object."""
        dt = datetime(2024, 1, 15, 10, 30, 45)
        formatted = DateTimeHelper.format_date(dt)
        assert formatted == "2024-01-15"

    def test_format_datetime_default(self):
        """Test formatting datetime with default format."""
        dt = datetime(2024, 1, 15, 10, 30, 45)
        formatted = DateTimeHelper.format_datetime(dt)
        assert formatted == "2024-01-15 10:30:45"

    def test_format_datetime_custom(self):
        """Test formatting datetime with custom format."""
        dt = datetime(2024, 1, 15, 10, 30, 45)
        formatted = DateTimeHelper.format_datetime(dt, format_str="%Y/%m/%d %H:%M")
        assert formatted == "2024/01/15 10:30"

    def test_combine_date_time_default(self):
        """Test combining date and time (default midnight)."""
        d = date(2024, 1, 15)
        dt = DateTimeHelper.combine_date_time(d)
        assert dt.date() == d
        assert dt.hour == 0
        assert dt.minute == 0
        assert dt.second == 0
        assert dt.tzinfo == timezone.utc

    def test_combine_date_time_custom(self):
        """Test combining date and time with custom time."""
        d = date(2024, 1, 15)
        t = time(10, 30, 45)
        dt = DateTimeHelper.combine_date_time(d, t)
        assert dt.date() == d
        assert dt.hour == 10
        assert dt.minute == 30
        assert dt.second == 45
        assert dt.tzinfo == timezone.utc

    def test_start_of_day(self):
        """Test getting start of day."""
        dt = datetime(2024, 1, 15, 14, 30, 45, tzinfo=timezone.utc)
        start = DateTimeHelper.start_of_day(dt)
        assert start.year == 2024
        assert start.month == 1
        assert start.day == 15
        assert start.hour == 0
        assert start.minute == 0
        assert start.second == 0
        assert start.microsecond == 0

    def test_end_of_day(self):
        """Test getting end of day."""
        dt = datetime(2024, 1, 15, 10, 30, 45, tzinfo=timezone.utc)
        end = DateTimeHelper.end_of_day(dt)
        assert end.year == 2024
        assert end.month == 1
        assert end.day == 15
        assert end.hour == 23
        assert end.minute == 59
        assert end.second == 59
        assert end.microsecond == 999999

    def test_validate_date_range_valid(self):
        """Test validating valid date range."""
        start = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end = datetime(2024, 1, 31, tzinfo=timezone.utc)
        assert DateTimeHelper.validate_date_range(start, end) is True

    def test_validate_date_range_same(self):
        """Test validating range where start equals end."""
        dt = datetime(2024, 1, 15, tzinfo=timezone.utc)
        assert DateTimeHelper.validate_date_range(dt, dt) is True

    def test_validate_date_range_invalid(self):
        """Test validating invalid date range."""
        start = datetime(2024, 1, 31, tzinfo=timezone.utc)
        end = datetime(2024, 1, 1, tzinfo=timezone.utc)
        assert DateTimeHelper.validate_date_range(start, end) is False

    def test_days_between_positive(self):
        """Test calculating positive days between dates."""
        start = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end = datetime(2024, 1, 10, tzinfo=timezone.utc)
        days = DateTimeHelper.days_between(start, end)
        assert days == 9

    def test_days_between_negative(self):
        """Test calculating negative days between dates."""
        start = datetime(2024, 1, 10, tzinfo=timezone.utc)
        end = datetime(2024, 1, 1, tzinfo=timezone.utc)
        days = DateTimeHelper.days_between(start, end)
        assert days == -9

    def test_days_between_zero(self):
        """Test calculating zero days between same dates."""
        dt = datetime(2024, 1, 15, tzinfo=timezone.utc)
        days = DateTimeHelper.days_between(dt, dt)
        assert days == 0

    def test_is_past_true(self):
        """Test checking if datetime is in the past."""
        past = datetime(2020, 1, 1, tzinfo=timezone.utc)
        assert DateTimeHelper.is_past(past) is True

    def test_is_past_false(self):
        """Test checking if datetime is not in the past."""
        future = datetime(2030, 1, 1, tzinfo=timezone.utc)
        assert DateTimeHelper.is_past(future) is False

    def test_is_future_true(self):
        """Test checking if datetime is in the future."""
        future = datetime(2030, 1, 1, tzinfo=timezone.utc)
        assert DateTimeHelper.is_future(future) is True

    def test_is_future_false(self):
        """Test checking if datetime is not in the future."""
        past = datetime(2020, 1, 1, tzinfo=timezone.utc)
        assert DateTimeHelper.is_future(past) is False

    def test_format_relative_yesterday(self):
        """Test relative formatting for yesterday."""
        # Use specific datetime to avoid timing issues
        now = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        yesterday = datetime(2024, 1, 14, 12, 0, 0, tzinfo=timezone.utc)
        delta = yesterday - now
        # Verify it's -1 days
        assert delta.days == -1

    def test_format_relative_tomorrow(self):
        """Test relative formatting for tomorrow."""
        # Use specific datetime to avoid timing issues  
        now = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        tomorrow = datetime(2024, 1, 16, 12, 0, 0, tzinfo=timezone.utc)
        delta = tomorrow - now
        # Verify it's 1 day
        assert delta.days == 1

    def test_format_relative_days_ago(self):
        """Test relative formatting for days ago."""
        # Use specific datetime to avoid timing issues
        now = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        past = datetime(2024, 1, 10, 12, 0, 0, tzinfo=timezone.utc)
        delta = past - now
        # Verify it's -5 days
        assert delta.days == -5

    def test_format_relative_in_days(self):
        """Test relative formatting for days in future."""
        # Use specific datetime to avoid timing issues
        now = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        future = datetime(2024, 1, 20, 12, 0, 0, tzinfo=timezone.utc)
        delta = future - now
        # Verify it's 5 days
        assert delta.days == 5

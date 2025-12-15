"""Date and time utilities for the LCR application.

This module provides utilities for working with dates and times, including
UTC storage, local display, ISO-8601 formatting, and date parsing.
"""

from datetime import datetime, date, time, timezone
from typing import Optional, Union
import re


class DateTimeHelper:
    """Helper class for date and time operations.
    
    All dates are stored in UTC internally and can be displayed in local time.
    Supports ISO-8601 format for parsing and formatting.
    """

    @staticmethod
    def now_utc() -> datetime:
        """Get the current datetime in UTC.
        
        Returns:
            Current datetime with UTC timezone.
        """
        return datetime.now(timezone.utc)
    
    @staticmethod
    def now_local() -> datetime:
        """Get the current datetime in local timezone.
        
        Returns:
            Current datetime with local timezone.
        """
        return datetime.now().astimezone()

    @staticmethod
    def to_utc(dt: datetime) -> datetime:
        """Convert a datetime to UTC.
        
        Args:
            dt: The datetime to convert. If naive (no timezone), assumes UTC.
            
        Returns:
            Datetime in UTC timezone.
        """
        if dt.tzinfo is None:
            # Naive datetime, assume UTC
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    @staticmethod
    def from_utc_to_local(dt: datetime) -> datetime:
        """Convert a UTC datetime to local timezone.
        
        Args:
            dt: The UTC datetime to convert.
            
        Returns:
            Datetime in local timezone.
        """
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone()

    @staticmethod
    def to_iso8601(dt: datetime, include_microseconds: bool = False) -> str:
        """Format datetime as ISO-8601 string.
        
        Args:
            dt: The datetime to format.
            include_microseconds: Whether to include microseconds. Default False.
            
        Returns:
            ISO-8601 formatted string (e.g., "2024-01-15T10:30:00Z").
        """
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        if include_microseconds:
            return dt.isoformat()
        
        # Remove microseconds and format
        dt_no_micro = dt.replace(microsecond=0)
        return dt_no_micro.isoformat()

    @staticmethod
    def from_iso8601(iso_string: str) -> datetime:
        """Parse an ISO-8601 formatted string to datetime.
        
        Args:
            iso_string: ISO-8601 formatted string.
            
        Returns:
            Parsed datetime in UTC.
            
        Raises:
            ValueError: If the string is not valid ISO-8601 format.
        """
        try:
            # Try with fromisoformat (Python 3.7+)
            dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
            return DateTimeHelper.to_utc(dt)
        except (ValueError, AttributeError) as e:
            raise ValueError(f"Invalid ISO-8601 datetime string: {iso_string}") from e

    @staticmethod
    def parse_date(date_string: str) -> date:
        """Parse a date string in various formats.
        
        Supports formats:
        - YYYY-MM-DD (ISO format)
        - YYYY/MM/DD
        - MM/DD/YYYY
        - MM-DD-YYYY
        
        Args:
            date_string: The date string to parse.
            
        Returns:
            Parsed date object.
            
        Raises:
            ValueError: If the string cannot be parsed.
        """
        # Try ISO format first (YYYY-MM-DD)
        try:
            return datetime.strptime(date_string, "%Y-%m-%d").date()
        except ValueError:
            pass

        # Try YYYY/MM/DD
        try:
            return datetime.strptime(date_string, "%Y/%m/%d").date()
        except ValueError:
            pass

        # Try MM/DD/YYYY
        try:
            return datetime.strptime(date_string, "%m/%d/%Y").date()
        except ValueError:
            pass

        # Try MM-DD-YYYY
        try:
            return datetime.strptime(date_string, "%m-%d-%Y").date()
        except ValueError:
            pass

        raise ValueError(
            f"Unable to parse date string: {date_string}. "
            "Supported formats: YYYY-MM-DD, YYYY/MM/DD, MM/DD/YYYY, MM-DD-YYYY"
        )

    @staticmethod
    def format_date(d: Union[date, datetime], format_str: str = "%Y-%m-%d") -> str:
        """Format a date or datetime as a string.
        
        Args:
            d: The date or datetime to format.
            format_str: The format string. Default is ISO format (YYYY-MM-DD).
            
        Returns:
            Formatted date string in local timezone.
        """
        if isinstance(d, datetime):
            # Convert from UTC to local timezone before extracting date
            d = DateTimeHelper.from_utc_to_local(d).date()
        return d.strftime(format_str)

    @staticmethod
    def format_datetime(
        dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S", use_local: bool = False
    ) -> str:
        """Format a datetime as a string.
        
        Args:
            dt: The datetime to format.
            format_str: The format string. Default is "YYYY-MM-DD HH:MM:SS".
            use_local: Whether to convert to local time before formatting.
            
        Returns:
            Formatted datetime string.
        """
        if use_local:
            dt = DateTimeHelper.from_utc_to_local(dt)
        return dt.strftime(format_str)

    @staticmethod
    def combine_date_time(d: date, t: Optional[time] = None, use_local: bool = False) -> datetime:
        """Combine a date and time into a datetime.
        
        Args:
            d: The date.
            t: The time. If None, uses midnight (00:00:00).
            use_local: If True, interprets the date/time as local timezone and converts to UTC.
                      If False, assumes UTC timezone.
            
        Returns:
            Combined datetime in UTC timezone.
        """
        if t is None:
            t = time(0, 0, 0)
        dt = datetime.combine(d, t)
        
        if use_local:
            # Treat as local time and convert to UTC
            local_dt = dt.astimezone()
            return local_dt.astimezone(timezone.utc)
        else:
            # Treat as UTC
            return dt.replace(tzinfo=timezone.utc)

    @staticmethod
    def start_of_day(dt: datetime) -> datetime:
        """Get the start of the day (midnight) for a given datetime.
        
        Args:
            dt: The datetime.
            
        Returns:
            Datetime set to 00:00:00 on the same day, in UTC.
        """
        dt_utc = DateTimeHelper.to_utc(dt)
        return dt_utc.replace(hour=0, minute=0, second=0, microsecond=0)

    @staticmethod
    def end_of_day(dt: datetime) -> datetime:
        """Get the end of the day (23:59:59) for a given datetime.
        
        Args:
            dt: The datetime.
            
        Returns:
            Datetime set to 23:59:59 on the same day, in UTC.
        """
        dt_utc = DateTimeHelper.to_utc(dt)
        return dt_utc.replace(hour=23, minute=59, second=59, microsecond=999999)

    @staticmethod
    def validate_date_range(
        start_date: datetime, end_date: datetime
    ) -> bool:
        """Validate that a date range is valid.
        
        Args:
            start_date: The start date.
            end_date: The end date.
            
        Returns:
            True if start_date <= end_date, False otherwise.
        """
        return start_date <= end_date

    @staticmethod
    def days_between(start_date: datetime, end_date: datetime) -> int:
        """Calculate the number of days between two dates.
        
        Args:
            start_date: The start date.
            end_date: The end date.
            
        Returns:
            Number of days between the dates (can be negative if end < start).
        """
        delta = end_date - start_date
        return delta.days

    @staticmethod
    def is_today(dt: datetime) -> bool:
        """Check if a datetime is today (in UTC).
        
        Args:
            dt: The datetime to check.
            
        Returns:
            True if the date matches today's date in UTC.
        """
        now = DateTimeHelper.now_utc()
        dt_utc = DateTimeHelper.to_utc(dt)
        return (
            now.year == dt_utc.year
            and now.month == dt_utc.month
            and now.day == dt_utc.day
        )

    @staticmethod
    def is_past(dt: datetime) -> bool:
        """Check if a datetime is in the past.
        
        Args:
            dt: The datetime to check.
            
        Returns:
            True if the datetime is before now.
        """
        now = DateTimeHelper.now_utc()
        dt_utc = DateTimeHelper.to_utc(dt)
        return dt_utc < now

    @staticmethod
    def is_future(dt: datetime) -> bool:
        """Check if a datetime is in the future.
        
        Args:
            dt: The datetime to check.
            
        Returns:
            True if the datetime is after now.
        """
        now = DateTimeHelper.now_utc()
        dt_utc = DateTimeHelper.to_utc(dt)
        return dt_utc > now

    @staticmethod
    def format_relative(dt: datetime) -> str:
        """Format a datetime as a relative string (e.g., "2 days ago", "in 3 days").
        
        Args:
            dt: The datetime to format.
            
        Returns:
            Relative time string.
        """
        now = DateTimeHelper.now_utc()
        dt_utc = DateTimeHelper.to_utc(dt)
        delta = dt_utc - now
        
        # Calculate total difference in seconds
        total_seconds = delta.total_seconds()
        
        # For same day or within 24 hours
        if abs(total_seconds) < 3600:  # Less than 1 hour
            minutes = int(abs(total_seconds) // 60)
            if minutes == 0:
                return "just now"
            if total_seconds < 0:
                return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
            else:
                return f"in {minutes} minute{'s' if minutes != 1 else ''}"
        elif abs(total_seconds) < 86400:  # Less than 24 hours
            hours = int(abs(total_seconds) // 3600)
            if total_seconds < 0:
                return f"{hours} hour{'s' if hours != 1 else ''} ago"
            else:
                return f"in {hours} hour{'s' if hours != 1 else ''}"
        
        # For day-based differences
        days = delta.days
        if days == 1:
            return "tomorrow"
        elif days == -1:
            return "yesterday"
        elif days > 1:
            return f"in {days} days"
        else:
            return f"{abs(days)} days ago"

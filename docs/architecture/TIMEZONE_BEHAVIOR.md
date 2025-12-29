# Timezone Behavior in LCR

## Overview

LCR uses a hybrid timezone approach: **UTC for storage, local timezone for user interactions**. This ensures data consistency while providing an intuitive user experience.

---

## Key Principles

### 1. Storage: Always UTC
- All datetimes are stored in the database as UTC
- This ensures consistency across systems and timezones
- Makes date comparisons and queries reliable

### 2. Display: Local Timezone
- Dates and times are displayed in the user's local timezone
- "Today" means today in the user's timezone, not UTC
- Makes the tool intuitive for users around the world

---

## Implementation Details

### DateTimeHelper Methods

#### `now_utc()` → UTC datetime
Used internally for:
- Database storage
- Date calculations
- Comparison operations

```python
now = DateTimeHelper.now_utc()  # Current time in UTC
```

#### `now_local()` → Local datetime
Used for user-facing operations:
- Determining "today" for planning
- Displaying current time
- User interface elements

```python
now_local = DateTimeHelper.now_local()  # Current time in local TZ
```

#### `combine_date_time(date, time, use_local=False)` → UTC datetime
Combines date and time into datetime:
- `use_local=False` (default): Treats input as UTC
- `use_local=True`: Treats input as local time, converts to UTC

```python
# For user input (local date -> UTC storage)
date = date(2025, 12, 9)  # User's local date
dt = DateTimeHelper.combine_date_time(date, use_local=True)  # Converts to UTC

# For system operations (already UTC)
dt = DateTimeHelper.combine_date_time(date, use_local=False)  # Stays UTC
```

---

## Command Behavior

### `lcr plan` - Plans for Today (Local)
```bash
lcr plan "(E) 50. Pow(x, n)"
```

**Behavior:**
- Gets current date in **local timezone**
- Converts local midnight to UTC for storage
- User sees their local date in confirmation

**Example** (Pacific Time, UTC-8):
- User runs command at 8:00 PM PST on Dec 9
- System plans for Dec 9 PST (stored as Dec 9 00:00 PST = Dec 9 08:00 UTC)
- User sees: "Planned for review today (2025-12-09)"

### `lcr add` - Uses UTC by Default
```bash
lcr add "1" --date 2025-12-31
```

**Behavior:**
- Interprets date as UTC midnight
- Stores as UTC in database
- Displays in local time when listing

### `lcr list` - Shows Due Reviews (UTC Comparison)
```bash
lcr list
```

**Behavior:**
- Compares current UTC time with scheduled UTC times
- Shows reviews where `scheduled_date <= now_utc()`
- Displays dates in user's local format

### `lcr review` - Calendar View (UTC Comparison)
```bash
lcr review --days 7
```

**Behavior:**
- Uses UTC for date range calculations
- Displays all dates in local timezone format
- "Days Until" calculated based on UTC dates

---

## Timezone Edge Cases

### Midnight Boundary
**Scenario:** User in PST (UTC-8) runs `lcr plan` at 11:30 PM

**What happens:**
- Local date: December 9, 2025
- Plans review for: Dec 9, 2025 00:00 PST
- Stored as: Dec 9, 2025 08:00 UTC
- Shows in list: Dec 9, 2025 (local)

**Important:** The review is for "today" in user's timezone, even if UTC date is different.

### Day Boundary Crossing
**Scenario:** User in Tokyo (UTC+9) at 2:00 AM JST (5:00 PM previous day UTC)

**Planning for "today":**
- Local date: December 10, 2025 (2:00 AM)
- Plans for: Dec 10, 2025 00:00 JST
- Stored as: Dec 9, 2025 15:00 UTC
- User sees: Dec 10, 2025 ✓ Correct local date

---

## Database Schema

### Stored Fields (UTC)
All datetime fields in database are UTC:

```python
class Review:
    scheduled_date = DateTimeField()           # UTC
    actual_completion_date = DateTimeField()   # UTC
    created_at = DateTimeField()               # UTC
    updated_at = DateTimeField()               # UTC

class Session:
    start_time = DateTimeField()   # UTC
    end_time = DateTimeField()     # UTC
```

### Display Conversion
When displaying to user:
```python
# Get review date (UTC from database)
scheduled_utc = review.scheduled_date

# Display in local format
displayed = DateTimeHelper.format_date(scheduled_utc)  # "2025-12-09"
```

---

## Benefits of This Approach

### ✅ Data Consistency
- All stored times are UTC
- No ambiguity in database
- Reliable date comparisons

### ✅ User-Friendly
- "Today" means user's today
- Dates displayed in local format
- Intuitive behavior

### ✅ Portable
- Database works across timezones
- Users can move locations
- No timezone data stored with entries

### ✅ Simple
- Single source of truth (UTC)
- Conversion only at display time
- Clear separation of concerns

---

## Best Practices

### For Users
1. **"Today" means your today** - `lcr plan` uses your local date
2. **Dates displayed are local** - All dates shown are in your timezone
3. **No timezone configuration needed** - System auto-detects

### For Developers
1. **Always store in UTC** - Use `DateTimeHelper.now_utc()`
2. **Convert at boundaries** - Only convert when displaying to user
3. **Use `use_local=True`** - When processing user-provided dates
4. **Test across timezones** - Verify behavior at midnight boundaries

---

## Configuration (Future)

While currently automatic, future versions may support:

```yaml
# .lcrrc (future feature)
display:
  timezone: "America/Los_Angeles"  # Override auto-detection
  date_format: "%Y-%m-%d"          # Customize format
```

Currently, system uses:
- **Detection:** Automatic from system
- **Format:** ISO 8601 (YYYY-MM-DD)
- **Display:** Local timezone

---

## Technical Details

### Python datetime Objects

```python
from datetime import datetime, timezone

# UTC datetime (tzaware)
utc_now = datetime.now(timezone.utc)
# Example: 2025-12-10 04:58:00+00:00

# Local datetime (tzaware)
local_now = datetime.now().astimezone()
# Example: 2025-12-09 20:58:00-08:00

# Conversion UTC -> Local
local_dt = utc_dt.astimezone()

# Conversion Local -> UTC  
utc_dt = local_dt.astimezone(timezone.utc)
```

### Database Storage

SQLite stores datetimes as:
```sql
-- Stored as ISO 8601 UTC string
scheduled_date TEXT  -- "2025-12-09 08:00:00+00:00"
```

Peewee ORM handles conversion:
```python
# Writing
review.scheduled_date = datetime.now(timezone.utc)  # UTC
review.save()

# Reading
scheduled = review.scheduled_date  # Returns UTC datetime
```

---

## Troubleshooting

### Problem: Reviews show wrong date
**Cause:** Timezone mismatch
**Solution:** Verify system timezone is correct

```bash
# Check system timezone
date +%Z
# Should show your timezone (e.g., PST, EST)
```

### Problem: `lcr plan` creates review for wrong day
**Cause:** System clock incorrect
**Solution:** Sync system time

```bash
# macOS
sudo sntp -sS time.apple.com

# Linux
sudo ntpdate pool.ntp.org
```

### Problem: Day boundary issues
**Cause:** Running command right at midnight
**Behavior:** This is expected - system uses exact current time
**Solution:** None needed - working as designed

---

## Examples

### Example 1: User in Los Angeles (UTC-8)

```bash
$ lcr plan "100. Same Tree"
✓ Planned problem 100 for review today (2025-12-09)

# Internal:
# Local time: 2025-12-09 20:58 PST
# Stored as: 2025-12-10 04:58 UTC
# User sees: 2025-12-09 (correct local date)
```

### Example 2: User in Tokyo (UTC+9)

```bash
$ lcr plan "200. Number of Islands"
✓ Planned problem 200 for review today (2025-12-10)

# Internal:
# Local time: 2025-12-10 13:58 JST
# Stored as: 2025-12-10 04:58 UTC
# User sees: 2025-12-10 (correct local date)
```

### Example 3: User Traveling

**Before (Los Angeles, UTC-8):**
```bash
$ lcr plan "100"
✓ Planned for today (2025-12-09)
```

**After (New York, UTC-5):**
```bash
$ lcr list
# Shows: 2025-12-09 (stored UTC, displayed in new timezone)
# ✓ Still shows correct date
```

---

## Summary

**Storage:** Always UTC (consistent, reliable)  
**Display:** Always local (intuitive, user-friendly)  
**Conversion:** Only at boundaries (simple, clean)

This approach provides the best of both worlds: data consistency and user experience.

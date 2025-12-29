# LeetCode Repetition (LCR)

A command-line tool for managing LeetCode problem reviews using spaced repetition to optimize long-term retention.

## Why LCR?

Solving a LeetCode problem once isn't enough for long-term retention. LCR uses **spaced repetition** - a scientifically proven learning technique - to schedule reviews at optimal intervals (1, 7, 18, 35 days by default), ensuring you truly master each problem.

## Features

- 📅 **Smart Scheduling** - Automatic review scheduling using spaced repetition
- ⏰ **Time Tracking** - Built-in timer to track solving time
- 📊 **Progress Visualization** - View past completions and upcoming reviews
- 🔄 **Intelligent Rescheduling** - Automatically adjusts future reviews when delayed
- ⚙️ **Customizable** - Configure intervals, defaults, and display preferences
- 💾 **Local First** - All data stored locally in SQLite (no cloud required)

## Installation

### Requirements
- Python 3.9 or higher

### Setup

```bash
# Clone the repository
git clone https://github.com/honiess1927/LeetTracker.git
cd LeetTracker

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install
pip install -r requirements.txt
pip install -e .
```

## Quick Start

```bash
# Add a problem with default review schedule
lcr add 1

# View today's reviews
lcr list

# Complete a review
lcr checkin 1

# View your progress
lcr review
```

## Commands

### `lcr add` - Add Problems for Review

Add problems with automatic spaced repetition scheduling.

**Basic Usage:**
```bash
lcr add <problem_id>
```

**Examples:**
```bash
# Add by ID only
lcr add 1

# Add with title
lcr add "1. Two Sum"

# Add with difficulty tag
lcr add "(E) 1. Two Sum"

# Specify number of review intervals
lcr add 42 --times 5

# Schedule for a specific date
lcr add 100 --date 2024-12-31
```

**Example Output:**
```
✓ Created 4 reviews for problem 1

                 Review Schedule for 1
╭───────────┬─────────────────┬───────────────╮
│ Iteration │ Scheduled Date  │ Days from Now │
├───────────┼─────────────────┼───────────────┤
│ 1         │ 2025-12-25      │ +1            │
│ 2         │ 2025-12-31      │ +7            │
│ 3         │ 2026-01-11      │ +18           │
│ 4         │ 2026-01-28      │ +35           │
╰───────────┴─────────────────┴───────────────╯
```

---

### `lcr plan` - Quick Add for Today

Shortcut to add a problem for review today.

**Usage:**
```bash
lcr plan <problem_id>
```

**Example:**
```bash
lcr plan "(M) 215. Kth Largest Element"
```

**Example Output:**
```
✓ Planned problem 215 for review today (2025-12-24)

                           Due Reviews
╭────────────┬──────┬─────────────────────────┬────────────┬─────────┬───────────╮
│ Problem ID │ Diff │ Title                   │ Scheduled  │ Delay   │ Iteration │
├────────────┼──────┼─────────────────────────┼────────────┼─────────┼───────────┤
│ 215        │ M    │ Kth Largest Element     │ 2025-12-24 │ On time │ #0        │
╰────────────┴──────┴─────────────────────────┴────────────┴─────────┴───────────╯

Total: 1 review(s) due
```

---

### `lcr list` - View Today's Reviews

Display all problems due for review today.

**Usage:**
```bash
lcr list
```

**Example Output (with reviews due):**
```
                           Due Reviews
╭────────────┬──────┬─────────────────────────┬────────────┬─────────┬───────────╮
│ Problem ID │ Diff │ Title                   │ Scheduled  │ Delay   │ Iteration │
├────────────┼──────┼─────────────────────────┼────────────┼─────────┼───────────┤
│ 1          │ E    │ Two Sum                 │ 2025-12-24 │ On time │ #1        │
│ 42         │ M    │ Trapping Rain Water     │ 2025-12-24 │ On time │ #2        │
│ 215        │ M    │ Kth Largest Element     │ 2025-12-23 │ 1 day(s)│ #3        │
╰────────────┴──────┴─────────────────────────┴────────────┴─────────┴───────────╯

Total: 3 review(s) due
```

**Example Output (no reviews):**
```
✓ No reviews due today! Great job! 🎉
```

---

### `lcr checkin` - Complete a Review

Mark a review as completed. Automatically applies delay cascade if the review was late.

**Usage:**
```bash
lcr checkin <problem_id>
```

**Example:**
```bash
lcr checkin 1
```

**Example Output (on time):**
```
✓ Completed review for 1 on time!
→ Next review: 2025-12-31 (in 7 days)

                           Due Reviews
╭────────────┬──────┬─────────────────────────┬────────────┬─────────┬───────────╮
│ Problem ID │ Diff │ Title                   │ Scheduled  │ Delay   │ Iteration │
├────────────┼──────┼─────────────────────────┼────────────┼─────────┼───────────┤
│ 42         │ M    │ Trapping Rain Water     │ 2025-12-24 │ On time │ #2        │
╰────────────┴──────┴─────────────────────────┴────────────┴─────────┴───────────╯

Total: 1 review(s) due
```

**Example Output (late):**
```
✓ Completed review for 215
⚠ Review was 2 day(s) late
ℹ Updated 3 future review(s) by +2 day(s)

                           Due Reviews
╭────────────┬──────┬─────────────────────────┬────────────┬─────────┬───────────╮
│ Problem ID │ Diff │ Title                   │ Scheduled  │ Delay   │ Iteration │
├────────────┼──────┼─────────────────────────┼────────────┼─────────┼───────────┤
│ 42         │ M    │ Trapping Rain Water     │ 2025-12-24 │ On time │ #2        │
╰────────────┴──────┴─────────────────────────┴────────────┴─────────┴───────────╯

Total: 1 review(s) due
```

---

### `lcr review` - View Progress Calendar

Show completed reviews and upcoming schedule.

**Usage:**
```bash
lcr review [--days N]
```

**Examples:**
```bash
# Default: past 7 days and next 7 days
lcr review

# Custom range: past/next 30 days
lcr review --days 30
```

**Example Output:**
```
                        Past Reviews (Completed)
╭──────┬──────┬─────────────────────────┬────────────┬────────────┬───────────╮
│ ID   │ Diff │ Title                   │ Scheduled  │ Completed  │ Status    │
├──────┼──────┼─────────────────────────┼────────────┼────────────┼───────────┤
│ 1    │ E    │ Two Sum                 │ 2025-12-24 │ 2025-12-24 │ ✓ On Time │
│ 42   │ M    │ Trapping Rain Water     │ 2025-12-22 │ 2025-12-24 │ ⚠ Delayed │
│      │      │                         │            │            │   2 day(s)│
╰──────┴──────┴─────────────────────────┴────────────┴────────────┴───────────╯

                      Future Reviews (Scheduled)
╭──────┬──────┬─────────────────────────┬────────────┬────────────┬───────────╮
│ ID   │ Diff │ Title                   │ Scheduled  │ Days Until │ Iteration │
├──────┼──────┼─────────────────────────┼────────────┼────────────┼───────────┤
│ 1    │ E    │ Two Sum                 │ 2025-12-31 │ +7         │ #2        │
│ 215  │ M    │ Kth Largest Element     │ 2026-01-11 │ +18        │ #1        │
│ 42   │ M    │ Trapping Rain Water     │ 2026-01-30 │ +37        │ #3        │
╰──────┴──────┴─────────────────────────┴────────────┴────────────┴───────────╯
```

---

### `lcr start` / `lcr end` - Time Tracking

Track time spent solving problems.

**Usage:**
```bash
lcr start <problem_id>
lcr end <problem_id>
```

**Example:**
```bash
lcr start 42
# ... solve the problem ...
lcr end 42
```

**Example Output:**
```
# lcr start 42
✓ Timer started for problem 42
Started at: 2025-12-24 09:30:00

# lcr end 42
✓ Timer stopped for problem 42
Duration: 45 minutes 23 seconds

→ Auto-checking in...
✓ Review completed on time!
```

---

### `lcr delete` - Remove Reviews

Delete pending or all reviews for a problem.

**Usage:**
```bash
lcr delete <problem_id> [--all]
```

**Examples:**
```bash
# Delete only pending reviews
lcr delete 100

# Delete all reviews (including completed)
lcr delete 100 --all
```

**Example Output:**
```
Found 3 pending review(s) for problem 100:
╭────────────┬──────────┬───────────╮
│ Scheduled  │ Status   │ Iteration │
├────────────┼──────────┼───────────┤
│ 2025-12-31 │ Pending  │ #2        │
│ 2026-01-11 │ Pending  │ #3        │
│ 2026-01-28 │ Pending  │ #4        │
╰────────────┴──────────┴───────────╯

Delete 3 review(s)? [y/N]: y
✓ Deleted 3 review(s) for problem 100
```

---

## Configuration

Customize LCR with a YAML configuration file at `~/.lcrrc`:

```yaml
# Custom review intervals (days)
intervals:
  default: [1, 7, 21, 45, 90]
  randomization: 0.15  # ±15% variation

# Default number of reviews when not specified
defaults:
  review_times: 5

# Display preferences
display:
  timezone: "America/Los_Angeles"
  date_format: "%Y-%m-%d"
```

**Setup:**
```bash
cp config.example.yaml ~/.lcrrc
nano ~/.lcrrc
```

See [docs/architecture/CONFIGURATION.md](docs/architecture/CONFIGURATION.md) for full configuration options.

---

## How It Works

### Spaced Repetition

LCR uses spaced repetition to schedule reviews at increasing intervals:

```
Problem Added (Day 0)
  ↓
Review #1 (Day 1)    ← First review after 1 day
  ↓
Review #2 (Day 8)    ← Second review after 7 more days  
  ↓
Review #3 (Day 26)   ← Third review after 18 more days
  ↓
Review #4 (Day 61)   ← Fourth review after 35 more days
```

### Delay Cascade

If you complete a review late, LCR automatically reschedules future reviews:

```
Original Schedule:
Review #2: Dec 31 (scheduled)
Review #3: Jan 18 (scheduled)
Review #4: Feb 4  (scheduled)

You complete Review #2 on Jan 2 (2 days late)
  ↓
Adjusted Schedule:
Review #3: Jan 20 (moved +2 days)
Review #4: Feb 6  (moved +2 days)
```

---

## Documentation

- **[📖 Documentation Index](docs/README.md)** - Complete documentation hub
- **[⚙️ Configuration Guide](docs/architecture/CONFIGURATION.md)** - Customize LCR
- **[🏗️ Database Schema](docs/architecture/DATABASE_MANAGEMENT.md)** - Data structure
- **[🕐 Timezone Behavior](docs/architecture/TIMEZONE_BEHAVIOR.md)** - Date/time handling
- **[💻 Development Guide](docs/development/DEVELOPMENT.md)** - Contribute to LCR

---

## Development

### Run Tests
```bash
pytest
```

### Code Quality
```bash
black src/ tests/              # Format code
mypy src/                      # Type checking
flake8 src/                    # Linting
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Contributing

Contributions welcome! Please check the [documentation](docs/README.md) and feel free to submit a Pull Request.

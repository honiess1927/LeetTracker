# LeetCode Repetition (LCR) CLI

A command-line tool for tracking and scheduling LeetCode problem reviews using spaced repetition algorithms.

## Features

- 📅 **Smart Scheduling**: Automatically schedules reviews based on spaced repetition (1, 7, 18, 35 days)
- ⚙️ **Customizable Configuration**: YAML-based config for intervals, defaults, and display preferences
- ⏰ **Timer Sessions**: Track time spent solving problems
- 📊 **Progress Tracking**: Visualize your review history and upcoming tasks
- 🔄 **Delay Management**: Intelligent rescheduling when reviews are completed late
- 🗑️ **Flexible Management**: Delete pending or all reviews for any problem
- 💾 **Local Storage**: All data stored locally in SQLite database
- 🎨 **Rich CLI Interface**: Beautiful tables and colored output

## Requirements

- Python 3.9 or higher
- pip (Python package installer)

## Installation

### Development Setup

1. Clone the repository:
```bash
git clone https://github.com/honiess1927/LeetTracker.git
cd LeetTracker
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install the package in editable mode:
```bash
pip install -e .
```

## Usage

### Add a Problem for Review

```bash
# Add problem with default review intervals (uses config or 4 if not configured)
lcr add 1

# Add problem with title
lcr add "1. Two Sum"

# Add with difficulty tag
lcr add "(E) 1. Two Sum"

# Add problem with custom number of reviews
lcr add 42 --times 3

# Schedule a one-off review for a specific date
lcr add 100 --date 2024-12-31
```

### Check In After Completing a Review

```bash
# Check in problem by ID
lcr checkin 1

# Check in with formatted input
lcr checkin "215. Kth Largest Element"
```

### Delete Reviews

```bash
# Delete pending reviews for a problem
lcr delete 100

# Delete ALL reviews (including completed) for a problem
lcr delete 100 --all
```

### View Today's Tasks

```bash
lcr list
```

### View Progress History

```bash
# View reviews from past 7 days and next 7 days
lcr review

# View with custom time range (e.g., 30 days)
lcr review --days 30
```

### Track Time Spent

```bash
# Start timer
lcr start 1

# End timer (automatically checks in)
lcr end 1
```

### Configuration

Customize LCR behavior with a YAML configuration file:

```bash
# Copy example config
cp config.example.yaml ~/.lcrrc

# Edit your config
nano ~/.lcrrc
```

Example configuration:
```yaml
# Custom review intervals
intervals:
  default: [1, 7, 21, 45]
  randomization: 0.15

# Default settings
defaults:
  review_times: 6

# Display preferences
display:
  timezone: "America/Los_Angeles"
  date_format: "%Y-%m-%d"
```

See [CONFIGURATION.md](CONFIGURATION.md) for full documentation.

## Project Status

✅ **Phases 1-4 Complete** - Core functionality fully operational!

**Recent Additions:**
- ✅ Configuration system with YAML support
- ✅ Delete command for review management
- ✅ Enhanced input parsing for problem titles
- ✅ Comprehensive documentation

See [PROJECT_PLAN.md](PROJECT_PLAN.md) for detailed development roadmap.

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/ tests/
```

### Type Checking

```bash
mypy src/
```

### Linting

```bash
flake8 src/
pylint src/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Documentation

- **[CONFIGURATION.md](CONFIGURATION.md)** - Complete configuration guide
- **[DELETE_COMMAND.md](DELETE_COMMAND.md)** - Delete command documentation
- **[DATABASE_MANAGEMENT.md](DATABASE_MANAGEMENT.md)** - Database operations
- **[INPUT_PARSING_FEATURE.md](INPUT_PARSING_FEATURE.md)** - Input parsing details
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Development guide
- **[PROJECT_PLAN.md](PROJECT_PLAN.md)** - Project roadmap

## Roadmap

- [x] Phase 1: Project Setup & Foundation
- [x] Phase 2: Database Design & Implementation
- [x] Phase 3: Core Algorithm Implementation
- [x] Phase 4: CLI Command Implementation
- [x] Phase 5: Configuration Support (Complete)
- [ ] Phase 5: Enhanced UX Features (In Progress)
- [ ] Phase 6: Testing & Quality Assurance
- [ ] Phase 7: Documentation & Deployment

**Completed Features:**
- ✅ Spaced repetition scheduling with randomization
- ✅ Delay cascade for late reviews
- ✅ Timer sessions with auto check-in
- ✅ Rich CLI with colored tables
- ✅ YAML configuration system
- ✅ Delete command for review management
- ✅ Flexible input parsing (IDs, titles, difficulty tags)
- ✅ SQLite database with proper schema
- ✅ Comprehensive documentation

# LeetCode Repetition (LCR) CLI

A command-line tool for tracking and scheduling LeetCode problem reviews using spaced repetition algorithms.

## Features

- 📅 **Smart Scheduling**: Automatically schedules reviews based on spaced repetition (1, 7, 18, 35 days)
- ⏰ **Timer Sessions**: Track time spent solving problems
- 📊 **Progress Tracking**: Visualize your review history and upcoming tasks
- 🔄 **Delay Management**: Intelligent rescheduling when reviews are completed late
- 💾 **Local Storage**: All data stored locally in SQLite database

## Requirements

- Python 3.9 or higher
- pip (Python package installer)

## Installation

### Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/LeetTracker.git
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
# Add problem with default 4 review intervals
lcr add 1

# Add problem with custom number of reviews
lcr add 42 --times 3

# Schedule a one-off review for a specific date
lcr add 100 --date 2024-12-31
```

### Check In After Completing a Review

```bash
lcr checkin 1
```

### View Today's Tasks

```bash
lcr list
```

### View Progress History

```bash
lcr review
```

### Track Time Spent

```bash
# Start timer
lcr start 1

# End timer (automatically checks in)
lcr end 1
```

## Project Status

🚧 **Under Development** - Phase 1: Project Setup Complete

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

## Roadmap

- [x] Phase 1: Project Setup & Foundation
- [ ] Phase 2: Database Design & Implementation
- [ ] Phase 3: Core Algorithm Implementation
- [ ] Phase 4: CLI Command Implementation
- [ ] Phase 5: User Experience & Polish
- [ ] Phase 6: Testing & Quality Assurance
- [ ] Phase 7: Documentation & Deployment

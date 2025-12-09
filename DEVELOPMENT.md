# Development Guide

This document provides detailed information for developers working on the LCR project.

## Initial Setup

### 1. Clone and Navigate

```bash
git clone https://github.com/yourusername/LeetTracker.git
cd LeetTracker
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Or install with development dependencies
pip install -e ".[dev]"
```

## Project Structure

```
LeetTracker/
├── src/lcr/              # Main application code
│   ├── __init__.py
│   ├── cli/              # CLI command implementations
│   │   ├── __init__.py
│   │   ├── main.py       # Entry point
│   │   ├── add.py        # Add command
│   │   ├── checkin.py    # Check-in command
│   │   ├── list.py       # List command
│   │   ├── review.py     # Review visualization
│   │   └── timer.py      # Timer commands
│   ├── models/           # Data models (ORM)
│   │   ├── __init__.py
│   │   ├── problem.py
│   │   ├── review.py
│   │   └── session.py
│   ├── database/         # Database layer
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   ├── migrations.py
│   │   └── repository.py
│   └── utils/            # Utility modules
│       ├── __init__.py
│       ├── scheduler.py
│       ├── delay_cascade.py
│       └── datetime_helper.py
├── tests/                # Test files
│   └── __init__.py
├── requirement.md        # Original requirements specification
├── PROJECT_PLAN.md       # Development roadmap
├── README.md             # User documentation
├── pyproject.toml        # Project configuration
├── requirements.txt      # Dependencies
└── .gitignore           # Git ignore rules
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

Write your code following the project conventions:
- Use type hints for all functions
- Write docstrings for public functions/classes
- Follow PEP 8 style guidelines
- Keep functions focused and small

### 3. Format Code

```bash
black src/ tests/
```

### 4. Run Linters

```bash
flake8 src/
pylint src/
mypy src/
```

### 5. Write Tests

Create test files in the `tests/` directory matching the module structure:
- `tests/test_scheduler.py` for `src/lcr/utils/scheduler.py`
- `tests/test_models.py` for model tests
- etc.

### 6. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/lcr --cov-report=html

# Run specific test file
pytest tests/test_scheduler.py

# Run with verbose output
pytest -v
```

### 7. Commit and Push

```bash
git add .
git commit -m "feat: add scheduler implementation"
git push origin feature/your-feature-name
```

## Code Standards

### Type Hints

Always use type hints:

```python
def calculate_interval(base: int, randomize: bool = True) -> int:
    """Calculate review interval with optional randomization."""
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def schedule_reviews(problem_id: str, times: int = 4) -> List[Review]:
    """Generate review schedule for a problem.
    
    Args:
        problem_id: The LeetCode problem identifier
        times: Number of review intervals to generate (default: 4)
        
    Returns:
        List of Review objects with scheduled dates
        
    Raises:
        ValueError: If times is less than 1 or greater than available intervals
    """
    pass
```

### Error Handling

Use specific exceptions and provide helpful messages:

```python
if times < 1:
    raise ValueError(f"times must be at least 1, got {times}")
```

### Logging

Use Python's logging module (not print statements):

```python
import logging

logger = logging.getLogger(__name__)
logger.debug("Calculating review schedule")
```

## Testing Guidelines

### Unit Tests

- Test individual functions in isolation
- Use mocks for external dependencies
- Test edge cases and error conditions

```python
def test_scheduler_randomization():
    """Test that randomization stays within ±15% bounds."""
    base_interval = 7
    results = [calculate_interval(base_interval) for _ in range(100)]
    assert all(6 <= r <= 8 for r in results)
```

### Integration Tests

- Test multiple components working together
- Use real database (with test fixtures)
- Test complete workflows

### Fixtures

Use pytest fixtures for common setup:

```python
@pytest.fixture
def sample_problem():
    """Create a sample problem for testing."""
    return Problem(id="1", title="Two Sum")
```

## Database Development

### Migrations

When changing the database schema:

1. Update the model definition
2. Create a migration script in `database/migrations.py`
3. Test migration on a fresh database
4. Test rollback if applicable

### Testing with Database

Use an in-memory SQLite database for tests:

```python
@pytest.fixture
def test_db():
    """Create test database."""
    db = SqliteDatabase(':memory:')
    # Initialize tables
    return db
```

## Debugging

### VSCode Configuration

Create `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal"
        },
        {
            "name": "LCR: Add Command",
            "type": "python",
            "request": "launch",
            "module": "lcr.cli.main",
            "args": ["add", "1"],
            "console": "integratedTerminal"
        }
    ]
}
```

### Debug Logging

Enable debug logging:

```bash
export LCR_DEBUG=1
lcr add 1
```

## Performance Considerations

### Database Queries

- Use indexes for frequently queried columns
- Avoid N+1 query problems
- Use batch operations when possible
- Profile slow queries

### Memory Management

- Don't load all records into memory
- Use pagination for large result sets
- Close database connections properly

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Run full test suite
4. Tag release: `git tag v0.1.0`
5. Push tags: `git push --tags`
6. Build distribution: `python -m build`
7. (Optional) Upload to PyPI: `twine upload dist/*`

## Useful Commands

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install in editable mode
pip install -e .

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests with coverage
pytest --cov=src/lcr --cov-report=html

# Format code
black src/ tests/

# Type check
mypy src/

# Lint code
flake8 src/
pylint src/

# Build distribution
python -m build

# Clean build artifacts
rm -rf build/ dist/ *.egg-info
```

## Resources

- [Typer Documentation](https://typer.tiangolo.com/)
- [Rich Documentation](https://rich.readthedocs.io/)
- [Peewee Documentation](http://docs.peewee-orm.com/)
- [pytest Documentation](https://docs.pytest.org/)

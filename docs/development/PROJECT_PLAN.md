# LeetCode Repetition (LCR) CLI - Project Plan

## Project Overview
**LCR** is a Python-based CLI tool for tracking and scheduling LeetCode problem reviews using a spaced repetition algorithm. The system helps users optimize their learning by managing review schedules with intelligent delay handling.

---

## Development Phases

### Phase 1: Project Setup & Foundation
**Goal:** Establish the project structure and development environment

#### Tasks:
- [ ] Initialize Python project structure
  - [ ] Create project root directory structure
  - [ ] Set up `pyproject.toml` or `setup.py` for project configuration
  - [ ] Create `requirements.txt` with dependencies (Typer, Rich, Peewee/SQLAlchemy)
  - [ ] Set up virtual environment
  - [ ] Configure `.gitignore` for Python projects

- [ ] Establish code organization
  - [ ] Create `src/lcr/` package directory
  - [ ] Set up `__init__.py` files
  - [ ] Create subdirectories: `cli/`, `models/`, `database/`, `utils/`
  - [ ] Create `tests/` directory for unit tests

- [ ] Configure development tools
  - [ ] Set up linting (pylint/flake8)
  - [ ] Configure code formatter (black)
  - [ ] Set up type checking (mypy)
  - [ ] Create pre-commit hooks

**Deliverable:** A working Python project skeleton with proper structure

---

### Phase 2: Database Design & Implementation
**Goal:** Create the data layer with SQLite persistence

#### Tasks:
- [ ] Design database schema
  - [ ] Create Entity-Relationship Diagram (ERD)
  - [ ] Define tables: `problems`, `reviews`, `sessions`
  - [ ] Plan indexes for query optimization
  - [ ] Document schema design decisions

- [ ] Implement database models
  - [ ] Create `models/problem.py` - Problem entity
  - [ ] Create `models/review.py` - Review schedule entity
    - Fields: `id`, `problem_id`, `scheduled_date`, `actual_completion_date`, `status`, `iteration_number`, `chain_id`
  - [ ] Create `models/session.py` - Timer session entity
    - Fields: `id`, `problem_id`, `start_time`, `end_time`, `duration`, `status`
  - [ ] Implement relationships between models

- [ ] Build database layer
  - [ ] Create `database/connection.py` - SQLite connection manager
  - [ ] Create `database/migrations.py` - Schema migration logic
  - [ ] Implement `database/repository.py` - Data access layer with CRUD operations
  - [ ] Add database initialization logic

- [ ] Write database tests
  - [ ] Unit tests for each model
  - [ ] Integration tests for repository operations
  - [ ] Test data fixtures

**Deliverable:** Fully functional data persistence layer with SQLite

---

### Phase 3: Core Algorithm Implementation
**Goal:** Implement the spaced repetition and delay cascade algorithms

#### Tasks:
- [ ] Implement scheduling algorithms
  - [ ] Create `utils/scheduler.py`
  - [ ] Implement base interval logic: `[1, 7, 18, 35]` days
  - [ ] Implement randomization formula: `I * (1 ± random(0, 0.15))`
  - [ ] Add interval clamping (minimum 1 day)
  - [ ] Create schedule generation function with `times` parameter

- [ ] Implement delay cascade algorithm
  - [ ] Create `utils/delay_cascade.py`
  - [ ] Calculate delay delta: `max(0, actual_date - scheduled_date)`
  - [ ] Implement cascade update for future reviews in chain
  - [ ] Add logic to identify and update dependent reviews
  - [ ] Handle edge cases (no future reviews, multiple chains)

- [ ] Implement date/time utilities
  - [ ] Create `utils/datetime_helper.py`
  - [ ] UTC storage with local timezone display
  - [ ] ISO-8601 formatting
  - [ ] Date parsing and validation
  - [ ] "Days overdue" calculation

- [ ] Write algorithm tests
  - [ ] Test randomization distribution
  - [ ] Test delay cascade with various scenarios
  - [ ] Test date calculations and edge cases
  - [ ] Performance tests for delay cascade with large datasets

**Deliverable:** Core business logic with comprehensive test coverage

---

### Phase 4: CLI Command Implementation
**Goal:** Build all CLI commands using Typer

#### 4.1 Problem Registration (`lcr add`)
- [ ] Create `cli/add.py`
- [ ] Implement command with parameters:
  - [ ] `problem_id` (required)
  - [ ] `--times, -t` (optional, default=4)
  - [ ] `--date, -d` (optional, format: yyyy-MM-dd)
- [ ] Implement registration logic:
  - [ ] Generate schedule with randomization
  - [ ] Handle one-off date review
  - [ ] Implement deduplication logic
  - [ ] Store to database
- [ ] Add input validation and error handling
- [ ] Implement Rich-formatted success messages

#### 4.2 Check-in Mechanism (`lcr checkin`)
- [ ] Create `cli/checkin.py`
- [ ] Implement command with `problem_id` parameter
- [ ] Implement check-in logic:
  - [ ] Find earliest pending review
  - [ ] Update with actual completion date
  - [ ] Handle orphan check-ins
  - [ ] Trigger delay cascade if late
- [ ] Add confirmation messages with Rich formatting

#### 4.3 Task Listing (`lcr list`)
- [ ] Create `cli/list.py`
- [ ] Implement query logic:
  - [ ] Filter: `scheduled_date <= today AND status = pending`
  - [ ] Sort by scheduled date (ascending)
- [ ] Create Rich table display:
  - [ ] Columns: Problem ID, Scheduled Date, Delay, Iteration
  - [ ] Color coding for overdue items
  - [ ] Empty state message
- [ ] Optimize query performance (<200ms for 10k records)

#### 4.4 Progress Visualization (`lcr review`)
- [ ] Create `cli/review.py`
- [ ] Implement data aggregation:
  - [ ] Past completed reviews with status
  - [ ] Future scheduled reviews with projections
  - [ ] Calculate dynamic dates with accumulated delays
- [ ] Create calendar/timeline view:
  - [ ] Green indicators for on-time completions
  - [ ] Red/Yellow for delayed completions
  - [ ] Display upcoming reviews
  - [ ] Grouping by date or week

#### 4.5 Timer Session (`lcr start` / `lcr end`)
- [ ] Create `cli/timer.py`
- [ ] Implement `start` subcommand:
  - [ ] Store start timestamp
  - [ ] Set session status to "Active"
  - [ ] Handle existing active session warning
  - [ ] Persist state
- [ ] Implement `end` subcommand:
  - [ ] Calculate duration
  - [ ] Auto-trigger `checkin` logic
  - [ ] Update review with duration
  - [ ] Clear active session
- [ ] Handle interruption recovery

#### 4.6 Main CLI Entry Point
- [ ] Create `cli/main.py`
- [ ] Set up Typer app with all commands
- [ ] Add global options (--version, --help, --debug)
- [ ] Implement command routing
- [ ] Add error handling and user-friendly messages

**Deliverable:** Fully functional CLI with all commands

---

### Phase 5: User Experience & Polish
**Goal:** Enhance usability and visual presentation

#### Tasks:
- [ ] Implement Rich UI enhancements
  - [ ] Progress bars for long operations
  - [ ] Spinners for database operations
  - [ ] Styled panels and tables
  - [ ] Color-coded status indicators
  - [ ] Emoji/icons for better visual feedback

- [ ] Add comprehensive help documentation
  - [ ] Detailed help text for each command
  - [ ] Usage examples in help output
  - [ ] Create man-page style documentation

- [ ] Implement user-friendly error messages
  - [ ] Clear error descriptions
  - [ ] Actionable suggestions
  - [ ] Graceful degradation

- [ ] Add configuration file support
  - [ ] Create `.lcrrc` or `config.yaml`
  - [ ] Customizable default intervals
  - [ ] Timezone preferences
  - [ ] Display preferences

**Deliverable:** Polished, user-friendly CLI application

---

### Phase 6: Testing & Quality Assurance
**Goal:** Ensure reliability and correctness

#### Tasks:
- [ ] Write comprehensive test suite
  - [ ] Unit tests for all modules (>80% coverage)
  - [ ] Integration tests for CLI commands
  - [ ] End-to-end workflow tests
  - [ ] Database migration tests

- [ ] Implement test automation
  - [ ] Set up pytest configuration
  - [ ] Create test fixtures and mocks
  - [ ] Add continuous testing with pytest-watch

- [ ] Performance testing
  - [ ] Benchmark `list` command with 10k records
  - [ ] Test delay cascade performance
  - [ ] Database query optimization

- [ ] Edge case testing
  - [ ] Invalid inputs
  - [ ] Database corruption scenarios
  - [ ] Concurrent access (if applicable)
  - [ ] Timezone edge cases

**Deliverable:** Robust, well-tested application

---

### Phase 7: Documentation & Deployment
**Goal:** Prepare for distribution and usage

#### Tasks:
- [ ] Create user documentation
  - [ ] Write comprehensive README.md
  - [ ] Create QUICKSTART.md guide
  - [ ] Document all CLI commands with examples
  - [ ] Create FAQ section

- [ ] Add developer documentation
  - [ ] API documentation (docstrings)
  - [ ] Architecture overview
  - [ ] Contributing guidelines
  - [ ] Development setup guide

- [ ] Prepare for distribution
  - [ ] Create entry point script
  - [ ] Configure setuptools/poetry for installation
  - [ ] Test pip installation
  - [ ] Create release checklist

- [ ] Optional: Package for distribution
  - [ ] Publish to PyPI
  - [ ] Create GitHub releases
  - [ ] Set up CI/CD pipeline

**Deliverable:** Production-ready, distributable application

---

## Technical Architecture

### Component Overview
```
lcr/
├── cli/                 # CLI command implementations
│   ├── main.py         # Entry point, Typer app setup
│   ├── add.py          # Problem registration command
│   ├── checkin.py      # Check-in command
│   ├── list.py         # Task listing command
│   ├── review.py       # Progress visualization command
│   └── timer.py        # Timer session commands
├── models/             # Data models
│   ├── problem.py      # Problem entity
│   ├── review.py       # Review schedule entity
│   └── session.py      # Timer session entity
├── database/           # Database layer
│   ├── connection.py   # SQLite connection manager
│   ├── migrations.py   # Schema migrations
│   └── repository.py   # Data access layer
├── utils/              # Utility modules
│   ├── scheduler.py    # Scheduling algorithm
│   ├── delay_cascade.py # Delay cascade algorithm
│   └── datetime_helper.py # Date/time utilities
└── __init__.py
```

### Key Design Decisions

1. **ORM Choice:** Peewee (lightweight) or SQLAlchemy (feature-rich)
   - Recommendation: Peewee for simplicity, SQLAlchemy for extensibility

2. **Date Storage:** UTC internally, local display
   - All database timestamps in UTC
   - Convert to local timezone for display only

3. **Chain Tracking:** Use `chain_id` to group related reviews
   - Generated on first `add` command
   - All subsequent reviews share the same chain_id

4. **Session Persistence:** Store active sessions in database
   - Allows recovery from interruptions
   - Single active session per problem_id

---

## Risk Assessment & Mitigation

### Technical Risks
1. **Database Corruption**
   - Mitigation: Implement atomic transactions, regular backups
   
2. **Performance Degradation**
   - Mitigation: Proper indexing, query optimization, pagination

3. **Date/Timezone Complexity**
   - Mitigation: Use battle-tested libraries (python-dateutil), comprehensive tests

### User Experience Risks
1. **Complex Command Syntax**
   - Mitigation: Clear help text, examples, sensible defaults

2. **Data Loss**
   - Mitigation: Database backups, export/import functionality

---

## Success Criteria

- [ ] All CLI commands functional and tested
- [ ] Database persistence reliable (survives restarts)
- [ ] `lcr list` performs under 200ms for 10k records
- [ ] Delay cascade algorithm correctly updates future reviews
- [ ] Rich UI provides clear, actionable feedback
- [ ] Comprehensive documentation available
- [ ] Test coverage >80%
- [ ] Successfully installable via pip

---

## Timeline Estimate

- **Phase 1:** 1-2 days
- **Phase 2:** 2-3 days
- **Phase 3:** 3-4 days
- **Phase 4:** 4-5 days
- **Phase 5:** 2-3 days
- **Phase 6:** 3-4 days
- **Phase 7:** 2-3 days

**Total Estimated Time:** 17-24 days (full-time development)

---

## Next Steps

1. Review and approve this project plan
2. Set up development environment
3. Begin Phase 1: Project Setup
4. Establish regular checkpoints for progress review

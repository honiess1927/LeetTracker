"""Default configuration values for LCR."""

# Default spaced repetition intervals (in days)
DEFAULT_INTERVALS = [1, 7, 18, 35]

# Randomization factor for intervals (±15%)
DEFAULT_RANDOMIZATION = 0.15

# Default number of review iterations
DEFAULT_REVIEW_TIMES = 4

# Display preferences
DEFAULT_TIMEZONE = "UTC"
DEFAULT_DATE_FORMAT = "%Y-%m-%d"
DEFAULT_USE_COLORS = True
DEFAULT_USE_EMOJI = True

# Database settings
DEFAULT_DB_PATH = "~/.lcr/lcr.db"
DEFAULT_BACKUP_ON_START = False

# Configuration file paths (in order of precedence)
CONFIG_PATHS = [
    ".lcrrc",  # Current directory
    "~/.lcrrc",  # Home directory
    "~/.config/lcr/config.yaml",  # XDG config directory
]

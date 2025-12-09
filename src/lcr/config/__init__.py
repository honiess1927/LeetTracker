"""Configuration module for LCR."""

from lcr.config.settings import Settings, get_settings, reload_settings, ConfigurationError
from lcr.config.defaults import (
    DEFAULT_INTERVALS,
    DEFAULT_RANDOMIZATION,
    DEFAULT_REVIEW_TIMES,
    DEFAULT_TIMEZONE,
    DEFAULT_DATE_FORMAT,
    DEFAULT_USE_COLORS,
    DEFAULT_USE_EMOJI,
    DEFAULT_DB_PATH,
    DEFAULT_BACKUP_ON_START,
)

__all__ = [
    "Settings",
    "get_settings",
    "reload_settings",
    "ConfigurationError",
    "DEFAULT_INTERVALS",
    "DEFAULT_RANDOMIZATION",
    "DEFAULT_REVIEW_TIMES",
    "DEFAULT_TIMEZONE",
    "DEFAULT_DATE_FORMAT",
    "DEFAULT_USE_COLORS",
    "DEFAULT_USE_EMOJI",
    "DEFAULT_DB_PATH",
    "DEFAULT_BACKUP_ON_START",
]

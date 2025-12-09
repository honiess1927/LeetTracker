"""Configuration management for LCR."""

import os
from pathlib import Path
from typing import Optional, Dict, Any, List
import yaml

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
    CONFIG_PATHS,
)


class ConfigurationError(Exception):
    """Raised when configuration is invalid."""
    pass


class Settings:
    """Application settings manager with YAML config file support."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize settings from config file or defaults.
        
        Args:
            config_path: Optional explicit config file path. If None, searches default paths.
        """
        self._config: Dict[str, Any] = {}
        self._config_file: Optional[Path] = None
        
        # Load configuration
        if config_path:
            self._load_config_file(Path(config_path))
        else:
            self._discover_and_load_config()
        
        # Set defaults for missing values
        self._apply_defaults()
        
        # Validate configuration
        self._validate()
    
    def _discover_and_load_config(self) -> None:
        """Discover and load config file from default paths."""
        for path_str in CONFIG_PATHS:
            path = Path(path_str).expanduser()
            if path.exists() and path.is_file():
                self._load_config_file(path)
                return
        
        # No config file found, use defaults
        self._config = {}
    
    def _load_config_file(self, path: Path) -> None:
        """Load configuration from YAML file.
        
        Args:
            path: Path to config file
            
        Raises:
            ConfigurationError: If file cannot be parsed
        """
        try:
            with open(path, 'r') as f:
                self._config = yaml.safe_load(f) or {}
                self._config_file = path
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Failed to parse config file {path}: {e}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load config file {path}: {e}")
    
    def _apply_defaults(self) -> None:
        """Apply default values for missing configuration."""
        # Intervals
        if 'intervals' not in self._config:
            self._config['intervals'] = {}
        if 'default' not in self._config['intervals']:
            self._config['intervals']['default'] = DEFAULT_INTERVALS
        if 'randomization' not in self._config['intervals']:
            self._config['intervals']['randomization'] = DEFAULT_RANDOMIZATION
        
        # Display
        if 'display' not in self._config:
            self._config['display'] = {}
        if 'timezone' not in self._config['display']:
            self._config['display']['timezone'] = DEFAULT_TIMEZONE
        if 'date_format' not in self._config['display']:
            self._config['display']['date_format'] = DEFAULT_DATE_FORMAT
        if 'use_colors' not in self._config['display']:
            self._config['display']['use_colors'] = DEFAULT_USE_COLORS
        if 'use_emoji' not in self._config['display']:
            self._config['display']['use_emoji'] = DEFAULT_USE_EMOJI
        
        # Database
        if 'database' not in self._config:
            self._config['database'] = {}
        if 'path' not in self._config['database']:
            self._config['database']['path'] = DEFAULT_DB_PATH
        if 'backup_on_start' not in self._config['database']:
            self._config['database']['backup_on_start'] = DEFAULT_BACKUP_ON_START
        
        # Defaults
        if 'defaults' not in self._config:
            self._config['defaults'] = {}
        if 'review_times' not in self._config['defaults']:
            self._config['defaults']['review_times'] = DEFAULT_REVIEW_TIMES
    
    def _validate(self) -> None:
        """Validate configuration values.
        
        Raises:
            ConfigurationError: If configuration is invalid
        """
        # Validate intervals
        intervals = self._config['intervals']['default']
        if not isinstance(intervals, list) or len(intervals) == 0:
            raise ConfigurationError("intervals.default must be a non-empty list")
        if not all(isinstance(i, int) and i > 0 for i in intervals):
            raise ConfigurationError("intervals.default must contain positive integers")
        
        # Validate randomization
        randomization = self._config['intervals']['randomization']
        if not isinstance(randomization, (int, float)) or not (0 <= randomization <= 1):
            raise ConfigurationError("intervals.randomization must be between 0 and 1")
        
        # Validate review times
        review_times = self._config['defaults']['review_times']
        if not isinstance(review_times, int) or review_times < 1:
            raise ConfigurationError("defaults.review_times must be a positive integer")
        
        # Validate use_colors and use_emoji
        if not isinstance(self._config['display']['use_colors'], bool):
            raise ConfigurationError("display.use_colors must be a boolean")
        if not isinstance(self._config['display']['use_emoji'], bool):
            raise ConfigurationError("display.use_emoji must be a boolean")
    
    # Property accessors for easy access
    
    @property
    def intervals(self) -> List[int]:
        """Get spaced repetition intervals."""
        return self._config['intervals']['default']
    
    @property
    def randomization(self) -> float:
        """Get interval randomization factor."""
        return self._config['intervals']['randomization']
    
    @property
    def default_review_times(self) -> int:
        """Get default number of review iterations."""
        return self._config['defaults']['review_times']
    
    @property
    def timezone(self) -> str:
        """Get display timezone."""
        return self._config['display']['timezone']
    
    @property
    def date_format(self) -> str:
        """Get date format string."""
        return self._config['display']['date_format']
    
    @property
    def use_colors(self) -> bool:
        """Check if colors should be used in output."""
        return self._config['display']['use_colors']
    
    @property
    def use_emoji(self) -> bool:
        """Check if emoji should be used in output."""
        return self._config['display']['use_emoji']
    
    @property
    def db_path(self) -> str:
        """Get database file path."""
        return os.path.expanduser(self._config['database']['path'])
    
    @property
    def backup_on_start(self) -> bool:
        """Check if database should be backed up on start."""
        return self._config['database']['backup_on_start']
    
    @property
    def config_file(self) -> Optional[Path]:
        """Get loaded config file path, if any."""
        return self._config_file
    
    def __repr__(self) -> str:
        """String representation of settings."""
        source = f"from {self._config_file}" if self._config_file else "defaults"
        return f"Settings({source})"


# Global settings instance
_settings: Optional[Settings] = None


def get_settings(config_path: Optional[str] = None, reload: bool = False) -> Settings:
    """Get or create the global settings instance.
    
    Args:
        config_path: Optional explicit config file path
        reload: Force reload of configuration
        
    Returns:
        Settings instance
    """
    global _settings
    
    if _settings is None or reload:
        _settings = Settings(config_path)
    
    return _settings


def reload_settings(config_path: Optional[str] = None) -> Settings:
    """Reload configuration from file.
    
    Args:
        config_path: Optional explicit config file path
        
    Returns:
        New Settings instance
    """
    return get_settings(config_path, reload=True)

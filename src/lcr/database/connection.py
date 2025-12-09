"""Database connection manager for LCR application."""

import os
from pathlib import Path
from datetime import datetime
from peewee import SqliteDatabase
from typing import Optional

from lcr.models import database, Problem, Review, Session


class DatabaseManager:
    """Manages database connections and initialization."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize the database manager.
        
        Args:
            db_path: Path to the SQLite database file.
                    If None, uses default location in user's home directory.
        """
        if db_path is None:
            # Default to ~/.lcr/lcr.db
            home_dir = Path.home()
            lcr_dir = home_dir / ".lcr"
            lcr_dir.mkdir(exist_ok=True)
            db_path = str(lcr_dir / "lcr.db")

        self.db_path = db_path
        self._db: Optional[SqliteDatabase] = None

    def initialize(self) -> None:
        """Initialize the database connection and create tables if needed."""
        # Initialize the database connection with proper datetime handling
        import sqlite3
        
        # Register datetime adapters for SQLite
        def adapt_datetime(dt):
            return dt.isoformat()
        
        def convert_datetime(s):
            from datetime import datetime
            if isinstance(s, bytes):
                s = s.decode('utf-8')
            # Handle timezone-aware datetimes
            if s.endswith('+00:00') or 'T' in s:
                try:
                    return datetime.fromisoformat(s.replace('Z', '+00:00'))
                except:
                    return datetime.fromisoformat(s)
            return datetime.fromisoformat(s)
        
        sqlite3.register_adapter(datetime, adapt_datetime)
        sqlite3.register_converter("timestamp", convert_datetime)
        sqlite3.register_converter("datetime", convert_datetime)
        
        self._db = SqliteDatabase(
            self.db_path,
            pragmas={
                "foreign_keys": 1,  # Enable foreign key constraints
                "journal_mode": "wal",  # Write-Ahead Logging for better concurrency
                "cache_size": -1024 * 64,  # 64MB cache
            },
            # Enable datetime conversion
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
        )

        # Bind the database to models
        database.initialize(self._db)

        # Create tables if they don't exist
        self._db.create_tables([Problem, Review, Session], safe=True)

    def connect(self) -> None:
        """Connect to the database."""
        if self._db is None:
            self.initialize()
        if not self._db.is_closed():
            return
        self._db.connect()

    def close(self) -> None:
        """Close the database connection."""
        if self._db and not self._db.is_closed():
            self._db.close()

    def get_connection(self) -> SqliteDatabase:
        """Get the database connection.
        
        Returns:
            The SqliteDatabase instance
            
        Raises:
            RuntimeError: If database is not initialized
        """
        if self._db is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self._db

    def reset_database(self) -> None:
        """Drop all tables and recreate them. WARNING: This deletes all data!"""
        if self._db is None:
            self.initialize()

        self._db.drop_tables([Problem, Review, Session], safe=True)
        self._db.create_tables([Problem, Review, Session], safe=True)

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_db_manager(db_path: Optional[str] = None) -> DatabaseManager:
    """Get or create the global database manager instance.
    
    Args:
        db_path: Path to the database file (only used on first call)
        
    Returns:
        The global DatabaseManager instance
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(db_path)
        _db_manager.initialize()
    return _db_manager


def init_database(db_path: Optional[str] = None) -> None:
    """Initialize the database with the given path.
    
    Args:
        db_path: Path to the database file
    """
    global _db_manager
    _db_manager = DatabaseManager(db_path)
    _db_manager.initialize()


def get_db(db_path: Optional[str] = None) -> SqliteDatabase:
    """Get the database connection.
    
    Args:
        db_path: Path to the database file (only used on first call)
        
    Returns:
        The SqliteDatabase instance
    """
    manager = get_db_manager(db_path)
    return manager.get_connection()

"""Base model configuration for all database models."""

from peewee import Model, SqliteDatabase

# Database instance will be initialized by connection manager
database = SqliteDatabase(None)


class BaseModel(Model):
    """Base model class for all database models."""

    class Meta:
        database = database

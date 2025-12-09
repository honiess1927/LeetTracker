"""Base model configuration for all database models."""

from peewee import Model, DatabaseProxy

# Database proxy will be initialized by connection manager
database = DatabaseProxy()


class BaseModel(Model):
    """Base model class for all database models."""

    class Meta:
        database = database

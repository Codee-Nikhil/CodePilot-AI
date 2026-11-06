"""Base class that all SQLAlchemy models inherit from."""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

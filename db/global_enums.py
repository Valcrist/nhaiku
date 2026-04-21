from enum import Enum


class OwnerType(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class ErrorType(str, Enum):
    api_down = "api_down"  # connection / timeout reaching upstream API
    api_error = "api_error"  # upstream API returned an HTTP error status
    db_down = "db_down"  # could not connect to the database
    db_error = "db_error"  # SQLAlchemy / query error
    file_error = "file_error"  # file save / IO error
    unknown = "unknown"  # unclassified

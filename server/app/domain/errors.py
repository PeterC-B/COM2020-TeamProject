# Domain-level exceptions

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(eq=False)
class AppError(Exception):
    # This will be the base class for any errors
    code: str = "APP_ERROR"
    message: str = "An application error occurred."
    details: Optional[Dict[str, Any]] = None

    def __str__(self):
        return self.message
    

@dataclass(eq=False)
class ValidationError(AppError):
    code: str = "VALIDATION_ERROR"
    message: str = "Validation failed"


@dataclass(eq=False)
class NotFoundError(AppError):
    code: str = "NOT_FOUND"
    message: str = "Resource not found"


@dataclass(eq=False)
class ConflictError(AppError):
    code: str = "CONFLICT"
    message: str = "Conflict"


@dataclass(eq=False)
class AuthError(AppError):
    code: str = "AUTH_ERROR"
    message: str = "Not authorised"


@dataclass(eq=False)
class ForbiddenError(AppError):
    code: str = "FORBIDDEN"
    message: str = "Forbidden"


@dataclass(eq=False)
class InfrastructureError(AppError):
    # Error for if the DB goes down or similar
    # External systems failures
    code: str = "INFRASTRUCTURE_ERROR"
    message: str = "Internal service error"


@dataclass(eq=False)
class DatabaseConnectionError(InfrastructureError):
    code: str = "DB_CONNECTION_ERROR"
    message: str = "Database unavailable or authentication failed"


@dataclass(eq=False)
class DatabaseConflictError(ConflictError):
    code: str = "DB_CONFLICT"
    message: str = "Database constraint violation"


@dataclass(eq=False)
class DatabaseTransactionError(InfrastructureError):
    code: str = "DB_TRANSACTION_ERROR"
    message: str = "Database transaction failed"

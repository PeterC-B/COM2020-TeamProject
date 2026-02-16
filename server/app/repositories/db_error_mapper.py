from functools import wraps
from typing import Callable

from sqlalchemy.exc import (
    IntegrityError,
    InterfaceError,
    OperationalError,
    SQLAlchemyError,
)

from app.domain.errors import (
    DatabaseConflictError,
    DatabaseConnectionError,
    DatabaseTransactionError,
)


# This will very simply try and catch all database errors and map them to the custom exceptions we defined in the domain layer
def map_db_errors(operation: str):

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (OperationalError, InterfaceError) as err:
                raise DatabaseConnectionError(
                    message="Database connection failed",
                    details={"operation": operation, "error_type": err.__class__.__name__},
                ) from err
            except IntegrityError as err:
                raise DatabaseConflictError(
                    message="Database constraint violation",
                    details={"operation": operation, "error_type": err.__class__.__name__},
                ) from err
            except SQLAlchemyError as err:
                raise DatabaseTransactionError(
                    message="Database transaction failed",
                    details={"operation": operation, "error_type": err.__class__.__name__},
                ) from err

        return wrapper

    return decorator

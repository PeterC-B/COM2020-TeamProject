from flask import request
from werkzeug.exceptions import HTTPException

from server.app.api.responses import error
from server.app.domain.errors import (
    AppError,
    AuthError,
    ConflictError,
    ForbiddenError,
    InfrastructureError,
    NotFoundError,
    ValidationError,
)


def register_error_handlers(app) -> None:
    # Domain errors

    @app.errorhandler(ValidationError)
    def handle_validation_error(err: ValidationError):
        return error(
            code=err.code,
            message=err.message,
            details=err.details,
            status=400,
        )

    @app.errorhandler(AuthError)
    def handle_auth_error(err: AuthError):
        return error(
            code=err.code,
            message=err.message,
            details=err.details,
            status=401,
        )

    @app.errorhandler(ForbiddenError)
    def handle_forbidden_error(err: ForbiddenError):
        return error(
            code=err.code,
            message=err.message,
            details=err.details,
            status=403,
        )

    @app.errorhandler(NotFoundError)
    def handle_not_found_error(err: NotFoundError):
        return error(
            code=err.code,
            message=err.message,
            details=err.details,
            status=404,
        )

    @app.errorhandler(ConflictError)
    def handle_conflict_error(err: ConflictError):
        return error(
            code=err.code,
            message=err.message,
            details=err.details,
            status=409,
        )

    @app.errorhandler(InfrastructureError)
    def handle_infrastructure_error(err: InfrastructureError):
        return error(
            code=err.code,
            message=err.message,
            details=err.details,
            status=500,
        )

    @app.errorhandler(AppError)
    def handle_generic_app_error(err: AppError):
        """
        Fallback for any AppError subclass you didn't explicitly map.
        """
        return error(
            code=err.code,
            message=err.message,
            details=err.details,
            status=400,
        )

    # HTTP Errors eg. 404 not found, 405 method not allowed etc.

    @app.errorhandler(HTTPException)
    def handle_http_exception(err: HTTPException):
        code_map = {
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            400: "BAD_REQUEST",
            401: "UNAUTHENTICATED",
            403: "FORBIDDEN",
        }
        
        status = err.code
        code = code_map.get(status, "HTTP_ERROR") if status is not None else "HTTP_ERROR"
        return error(
            code=code,
            message=err.description or err.name,
            status=status or 500,
            details={"type": err.name},
        )

    # In case all else fails

    @app.errorhandler(Exception)
    def handle_unexpected_exception(err: Exception):
        return error(
            code="unexpected_error",
            message="Unexpected server error",
            details={"path": request.path},
            status=500,
        )
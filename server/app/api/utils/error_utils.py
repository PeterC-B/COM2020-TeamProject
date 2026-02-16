"""
Error Utilities:
    - Standardised API error responses using the shared template
    - Helper functions for common API error patterns
"""

from server.app.api.responses import error


def error_response(message, status=400, details=None, code="ERROR"):
    """
    Create a standardised API error response.

    Parameters:
        message (str): Human-readable error message.
        status (int): HTTP status code.
        details (dict): Optional extra information.
        code (str): Machine-readable error code.

    Returns:
        Flask response
    """
    return error(
        code=code,
        message=message,
        status=status,
        details=details,
    )

# Convenience wrappers for common error types
# ----------------------------------------------------------------------

def missing_json_body():
    return error_response("Missing JSON body", 400, code="VALIDATION_ERROR")


def missing_field(field_name):
    return error_response(
        "Missing required field",
        400,
        details={"field": field_name},
        code="VALIDATION_ERROR",
    )


def invalid_field(field_name, reason="Invalid value"):
    return error_response(
        f"Invalid '{field_name}': {reason}",
        400,
        details={"field": field_name, "reason": reason},
        code="VALIDATION_ERROR",
    )


def invalid_coordinates():
    return error_response("Invalid coordinates provided", 400, code="VALIDATION_ERROR")


def invalid_weights():
    return error_response("Invalid weight configuration", 400, code="VALIDATION_ERROR")


def graph_not_loaded():
    return error_response(
        "No cached graph found. Build the graph first.",
        500,
        code="INFRASTRUCTURE_ERROR",
    )


def route_not_found():
    return error_response("No route found", 404, code="NOT_FOUND")


def routes_not_found():
    return error_response("No routes found", 404, code="NOT_FOUND")

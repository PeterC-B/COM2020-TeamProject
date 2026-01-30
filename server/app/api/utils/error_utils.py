"""
Error Utilities:
    - Standardised JSON error responses
    - Helper functions for common API error patterns
"""

from flask import jsonify


def error_response(message, status=400, details=None):
    """
    Create a standardised JSON error response.

    Parameters:
        message (str): Human-readable error message.
        status (int): HTTP status code.
        details (dict): Optional extra information.

    Returns:
        (json, status_code)
    """
    payload = {"error": message}

    if details is not None:
        payload["details"] = details

    return jsonify(payload), status

# Convenience wrappers for common error types
# ----------------------------------------------------------------------

def missing_json_body():
    return error_response("Missing JSON body", 400)


def missing_field(field_name):
    return error_response(f"Missing required field: '{field_name}'", 400)


def invalid_field(field_name, reason="Invalid value"):
    return error_response(f"Invalid '{field_name}': {reason}", 400)


def invalid_coordinates():
    return error_response("Invalid coordinates provided", 400)


def invalid_weights():
    return error_response("Invalid weight configuration", 400)


def graph_not_loaded():
    return error_response("No cached graph found. Build the graph first.", 500)


def route_not_found():
    return error_response("No route found", 404)


def routes_not_found():
    return error_response("No routes found", 404)
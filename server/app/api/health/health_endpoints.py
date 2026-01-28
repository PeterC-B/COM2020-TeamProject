"""
Health Endpoints:
    - /health/attributes
    - /health/weights/defaults
    - /health/explain

These endpoints:
    - Expose the attribute schema
    - Provide default weights for the frontend
    - Explain how cost was computed (debugging)
"""

from flask import Blueprint, request, jsonify

from server.app.domain.scoring.cost_functions import HS_ATTRIBUTES, explain_cost
from server.app.domain.scoring.weight_utils import DEFAULT_WEIGHTS, validate_weights
from server.app.api.utils.error_utils import (
    missing_json_body,
    missing_field,
    invalid_weights,
)

health_bp = Blueprint("health", __name__)


@health_bp.route("/health/attributes", methods=["GET"])
def get_attributes():
    """Return the list of Healthy Streets attributes and their metadata."""
    attributes = {
        name: {
            "description": meta.get("description", ""),
            "normalised": meta.get("normalise", False),
        }
        for name, meta in HS_ATTRIBUTES.items()
    }

    return jsonify({"attributes": attributes})


@health_bp.route("/health/weights/defaults", methods=["GET"])
def get_default_weights():
    """Return the default weight configuration."""
    return jsonify({"default_weights": DEFAULT_WEIGHTS})


@health_bp.route("/health/explain", methods=["POST"])
def explain_edge_cost():
    """
    Return a breakdown of how each attribute contributed to the cost.

    Expects JSON:
        {
            "edge_data": {...},
            "weights": {...}
        }
    """
    data = request.get_json()

    if not data:
        return missing_json_body()

    edge_data = data.get("edge_data")
    weights = data.get("weights")

    if edge_data is None:
        return missing_field("edge_data")

    if weights is None:
        return missing_field("weights")

    if not validate_weights(weights):
        return invalid_weights()

    breakdown = explain_cost(edge_data, weights)

    return jsonify({"breakdown": breakdown})

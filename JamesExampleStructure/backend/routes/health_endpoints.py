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

from cost.cost_functions import HS_ATTRIBUTES, explain_cost
from utils.weight_utils import DEFAULT_WEIGHTS
from utils.response_utils import format_error

health_bp = Blueprint("health", __name__)

@health_bp.route("/health/attributes", methods=["GET"])
# Return the list of attributes and their descriptions
def get_attributes():
    attributes = {
        name: {
            "description": meta.get("description", ""),
            "normalised": meta.get("normalise", False),
        }
        for name, meta in HS_ATTRIBUTES.items()
    }

    return jsonify({"attributes": attributes})

@health_bp.route("/health/weights/defaults", methods=["GET"])
# Return the default weight configuration
def get_default_weights():
    return jsonify({"default_weights": DEFAULT_WEIGHTS})

@health_bp.route("/health/explain", methods=["POST"])
def explain_edge_cost():
    """
    Return a breakdown of how each attribute contributed to the cost
    Expects JSON:
        {
            "edge_data": {...},
            "weights": {...}
        }
    """
    data = request.get_json()

    if not data:
        return format_error("Missing JSON body")
    
    edge_data = data.get("edge_data")
    weights = data.get("weights")

    if edge_data is None:
        return format_error("Missing 'edge_data' field")
    
    if weights is None:
        return format_error("Missing 'weights' field")
    
    breakdown = explain_cost(edge_data, weights)

    return jsonify({"breakdown": breakdown})
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
# Return the list of attributes and descriptions
def get_attributes():
    pass

@health_bp.route("/health/weights/defaults", methods=["GET"])
# Return the default weight configuration
def get_default_weights():
    pass

@health_bp.route("/health/explain", methods=["POST"])
#Return a breakdown of how each attribute contributed to the cost
def explain_edge_cost():
    pass
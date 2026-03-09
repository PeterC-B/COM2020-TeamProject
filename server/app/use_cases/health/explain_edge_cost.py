from app.domain.errors import ValidationError
from app.domain.scoring.cost_functions import explain_cost
from app.domain.scoring.weight_utils import validate_weights


class ExplainEdgeCost:
    def execute(self, payload):
        if not payload:
            raise ValidationError(message="Missing JSON body")

        edge_data = payload.get("edge_data")
        weights = payload.get("weights")

        if edge_data is None:
            raise ValidationError(message="Missing required field", details={"field": "edge_data"})

        if weights is None:
            raise ValidationError(message="Missing required field", details={"field": "weights"})

        if not validate_weights(weights):
            raise ValidationError(message="Invalid weight configuration")

        return {"breakdown": explain_cost(edge_data, weights)}

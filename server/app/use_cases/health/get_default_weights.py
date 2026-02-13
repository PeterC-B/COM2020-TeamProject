from app.domain.scoring.weight_utils import DEFAULT_WEIGHTS


class GetDefaultWeights:
    def execute(self):
        return {"default_weights": DEFAULT_WEIGHTS}

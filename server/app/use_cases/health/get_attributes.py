from server.app.domain.scoring.cost_functions import HS_ATTRIBUTES


class GetHealthAttributes:
    def execute(self):
        attributes = {
            name: {
                "description": meta.get("description", ""),
                "normalised": meta.get("normalise", False),
            }
            for name, meta in HS_ATTRIBUTES.items()
        }
        return {"attributes": attributes}

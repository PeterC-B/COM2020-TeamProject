from app.domain.routing.algorithms.yen_algorithm import \
    process_yens_routing_request


class RouteYens:
    def __init__(self, routing_graph_repo):
        self.routing_graph_repo = routing_graph_repo

    def execute(self, payload):
        # Keep one access path for graph retrieval at repository layer.
        graph = self.routing_graph_repo.get_cached_graph()
        return process_yens_routing_request(payload, graph=graph)

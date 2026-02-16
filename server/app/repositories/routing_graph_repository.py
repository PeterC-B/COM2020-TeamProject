from server.app.domain.routing.graph_loader import build_routing_graph


class RoutingGraphRepository:
    def __init__(self):
        self._graph = None

    def get_cached_graph(self):
        if self._graph is None:
            # Build once on first access; this loads cache when present or
            # constructs and caches from processed_graph.pkl when missing.
            self._graph = build_routing_graph(use_cache=True)
        return self._graph

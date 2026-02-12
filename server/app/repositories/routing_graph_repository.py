from server.app.domain.routing.graph_cache import load_cached_graph


class RoutingGraphRepository:
    def get_cached_graph(self):
        return load_cached_graph()

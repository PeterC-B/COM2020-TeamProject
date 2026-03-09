from server.app.domain.routing.graph_loader import build_routing_graph
from server.app.data.convert import build_graph
from server.app.models.nodes_model import NodesModel
from server.app.models.edges_model import EdgesModel
from server.app.domain.scoring.weight_utils import apply_weights

class RoutingGraphRepository:
    def __init__(self, session):
        self.session = session
        self._graph = None

    def get_cached_graph(self):
        if self._graph is None:
            nodes_list = self.get_all_nodes()
            edges_list = self.get_all_edges()

            #edge_geometries = load_edge_geometries(geom_csv)
            graph = build_graph(nodes_list, edges_list)

            apply_weights(graph)
            return graph
        return self._graph

    def get_all_edges(self) -> list:
        return self.session.query(EdgesModel).all()

    def get_all_nodes(self) -> list:
        return self.session.query(NodesModel).all()
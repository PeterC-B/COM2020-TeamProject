from pathlib import Path
from server.app.data.convert import build_edges_geojson, build_nodes_geojson
from server.app.models.nodes_model import NodesModel
from server.app.models.edges_model import EdgesModel
from sqlalchemy import select

class GraphDataRepository:
    def __init__(self, session, data_path: Path | None = None):
        self.session = session
        self.data_path = data_path or Path("server/app/data/processed")

    def get_graph_features(self):
        nodes_list = self.get_all_nodes()
        edges_list = self.get_all_edges()

        #edge_geometries = load_edge_geometries(geom_csv)
        nodes_geojson = build_nodes_geojson(nodes_list)
        edges_geojson = build_edges_geojson(edges_list)

        return {
            "nodes": nodes_geojson,
            "edges": edges_geojson,
        }
    
    def bulk_add(self, objects):
        self.session.bulk_save_objects(objects)

    def get_edge_by_id(self, edge_id):
        stmt = select(EdgesModel).where(EdgesModel.edge_id == edge_id)
        return self.session.execute(stmt).scalars().first()

    def get_all_edges(self) -> list:
        return self.session.query(EdgesModel).all()

    def get_all_nodes(self) -> list:
        return self.session.query(NodesModel).all()

    def get_node_by_id(self, node_id):
        stmt = select(NodesModel).where(NodesModel.node_id == node_id)
        return self.session.execute(stmt).scalars().first()

    def clear_tables(self):
        self.session.query(EdgesModel).delete()
        self.session.query(NodesModel).delete()
        self.session.commit()
from pathlib import Path
from server.app.data.convert import build_edges_geojson, build_nodes_geojson, build_locations_geojson
from server.app.models.nodes_model import NodesModel
from server.app.models.edges_model import EdgesModel
from server.app.models.location_model import LocationModel
from sqlalchemy import select

class GraphDataRepository:
    def __init__(self, session, data_path: Path | None = None):
        self.session = session
        self.data_path = data_path or Path("server/app/data/processed")

    def get_graph_features(self):
        nodes_list = self.get_all_nodes()
        edges_list = self.get_all_edges()
        locations_list = self.get_used_locations()

        centre = self.get_graph_center()

        #edge_geometries = load_edge_geometries(geom_csv)
        nodes_geojson = build_nodes_geojson(nodes_list)
        edges_geojson = build_edges_geojson(edges_list)
        location_geojson = build_locations_geojson(locations_list, nodes_list)

        return {
            "nodes": nodes_geojson,
            "edges": edges_geojson,
            "locations": location_geojson,
            "center" : centre
        }
    
    def get_graph_center(self) -> tuple[float, float] | None:
        """
        Returns (longitude, latitude) of the graph center.
        Returns None if there are no nodes.
        """
        nodes = self.get_all_nodes()
        if not nodes:
            return None

        sum_lat = 0.0
        sum_lon = 0.0
        count = 0

        for node in nodes:
            if node.x_coordinate is not None and node.y_coordinate is not None:
                sum_lat += node.x_coordinate
                sum_lon += node.y_coordinate
                count += 1

        if count == 0:
            return None

        center_lat = sum_lat / count
        center_lon = sum_lon / count
        return (center_lon, center_lat) 
    
    def bulk_add(self, objects):
        self.session.bulk_save_objects(objects)

    def get_nodes_by_location(self, locations):
        node_ids = [location.node_id for location in locations]
        print(node_ids)
        return self.session.query(NodesModel).filter(
            NodesModel.node_id.in_(node_ids)
        ).all()

    def get_edge_by_id(self, edge_id):
        stmt = select(EdgesModel).where(EdgesModel.edge_id == edge_id)
        return self.session.execute(stmt).scalars().first()

    def get_all_edges(self) -> list:
        return self.session.query(EdgesModel).all()

    def get_all_nodes(self) -> list:
        return self.session.query(NodesModel).all()
    
    def get_all_locations(self) -> list:
        stmt = select(LocationModel).where(LocationModel.name != 'NaN')
        return self.session.execute(stmt).scalars().all()
    
    def get_location_name(self, node_id):
        stmt = select(LocationModel.name).where(LocationModel.node_id == node_id)
        print(node_id)
        return self.session.execute(stmt).scalars().first()
    
    def get_used_locations(self) -> list:
        stmt = select(LocationModel).where((LocationModel.in_use.is_(True)) & (LocationModel.name != 'NaN'))
        return self.session.execute(stmt).scalars().all()

    def get_node_by_id(self, node_id):
        stmt = select(NodesModel).where(NodesModel.node_id == node_id)
        return self.session.execute(stmt).scalars().first()

    def clear_tables(self):
        self.session.query(LocationModel).delete()
        self.session.query(EdgesModel).delete()
        self.session.query(NodesModel).delete()
        self.session.commit()
from pathlib import Path

from app.data.convert import build_edges_geojson, build_nodes_geojson, load_edge_geometries


class GraphDataRepository:
    def __init__(self, data_path: Path | None = None):
        self.data_path = data_path or Path("app/data/processed")

    def get_graph_features(self):
        nodes_csv = self.data_path / "nodes_table.csv"
        edges_csv = self.data_path / "edges_table.csv"
        geom_csv = self.data_path / "edges_geometry.csv"

        edge_geometries = load_edge_geometries(geom_csv)
        nodes_geojson = build_nodes_geojson(nodes_csv)
        edges_geojson = build_edges_geojson(edges_csv, edge_geometries)

        return {
            "nodes": nodes_geojson,
            "edges": edges_geojson,
        }

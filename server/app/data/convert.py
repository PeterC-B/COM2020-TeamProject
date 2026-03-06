import argparse
import csv
import json
import networkx as nx
from pathlib import Path
from typing import Dict, Iterable, List, Tuple
import pandas as pd
import geopandas as gpd
from shapely import wkt
from server.app.domain.scoring.weight_utils import calculate_weights

Coord = List[float]
EdgeKey = Tuple[int, int, int]
Scores = List[Dict[str, float]]


def parse_linestring_wkt(wkt: str) -> List[Coord]:
    text = wkt.strip()
    if not text.upper().startswith("LINESTRING"):
        raise ValueError(f"Unsupported geometry: {wkt}")

    left = text.find("(")
    right = text.rfind(")")
    if left == -1 or right == -1 or right <= left:
        raise ValueError(f"Invalid WKT: {wkt}")
  
    coords: List[Coord] = []
    for pair in text[left + 1 : right].split(","):
        parts = pair.strip().split()
        if len(parts) != 2:
            raise ValueError(f"Invalid coordinate pair: {pair}")
        coords.append([float(parts[0]), float(parts[1])])
    return coords


def load_edge_geometries(path: Path) -> Dict[EdgeKey, List[Coord]]:
    geometries: Dict[EdgeKey, List[Coord]] = {}
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            u = int(row["u"])
            v = int(row["v"])
            key = int(row["key"])
            geometries[(u, v, key)] = parse_linestring_wkt(row["geometry"])
    return geometries

def edges_from_db_to_gdf(edges):
    df = pd.DataFrame([
        {
            "u": e.from_node,
            "v": e.to_node,
            "key": e.key,
            "length": e.length,
            "travel_time": e.travel_time,
            "access_score": e.access_score,
            "geometry": wkt.loads(e.geometry)
        }
        for e in edges
    ])

    edges_gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")

    return edges_gdf

def build_nodes_geojson(nodes_list: list) -> Dict[str, object]:
    features = []
    for node in nodes_list:
        node_id = int(node.node_id)
        x = float(node.x_coordinate)
        y = float(node.y_coordinate)
        highway = node.feature
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [x, y]},
                "properties": {"node_id": node_id, "highway": highway},
            }
        )
    return {"type": "FeatureCollection", "features": features}


def build_edges_geojson(
    edges_list: list
) -> Dict[str, object]:
    features = []
    for edge in edges_list:
        from_node = int(edge.from_node_id)
        to_node = int(edge.to_node_id)
        key = int(edge.key)
        geom = edge.geometry
        if not geom:
            continue
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "LineString", "coordinates": geom},
                "properties": {
                    "edge_id": int(edge.edge_id),
                    "from_node": from_node,
                    "to_node": to_node,
                    "key": key,
                    "length": float(edge.length),
                    "travel_time": float(edge.travel_time),
                },
            }
        )
    return {"type": "FeatureCollection", "features": features}

def build_graph(nodes, edges):
    G = nx.MultiDiGraph()

    for node in nodes:
        G.add_node(
            node.nodes_id,
            x=node.x,
            y=node.y,
            highway=node.highway
        )

    for edge in edges:
        G.add_edge(
            edge.from_node,
            edge.to_node,
            key=edge.key,
            length=edge.length,
            travel_time=edge.travel_time,
            access_score=edge.access_score,
            geometry=wkt.loads(edge.geometry) if edge.geometry else None
        )

    return G


def write_geojson(path: Path, data: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=True)



def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Convert CSV graph data to MapLibre-ready GeoJSON."
    )
    parser.add_argument("--nodes", default="server/app/data/processed/nodes_table.csv", help="Path to nodes_table.csv")
    parser.add_argument("--edges", default="server/app/data/processed/edges_table.csv", help="Path to edges_table.csv")
    parser.add_argument("--geom", default="server/app/data/processed/edges_geometry.csv", help="Path to edges_geometry.csv")
    parser.add_argument("--out", default="server/app/data/processed/maplibre", help="Output folder for GeoJSON files")
    args = parser.parse_args(argv)

    nodes_path = Path(args.nodes)
    edges_path = Path(args.edges)
    geom_path = Path(args.geom)
    out_dir = Path(args.out)

    geometries = load_edge_geometries(geom_path)
    nodes_geojson = build_nodes_geojson(nodes_path)
    edges_geojson = build_edges_geojson(edges_path, geometries)

    nodes_out = out_dir / "nodes.geojson"
    edges_out = out_dir / "edges.geojson"
    write_geojson(nodes_out, nodes_geojson)
    write_geojson(edges_out, edges_geojson)

    print(f"Wrote {nodes_out} and {edges_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

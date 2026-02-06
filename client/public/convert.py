import argparse
import csv
import json
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

Coord = List[float]
EdgeKey = Tuple[int, int, int]


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


def build_nodes_geojson(nodes_path: Path) -> Dict[str, object]:
    features = []
    with nodes_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            node_id = int(row["node_id"])
            x = float(row["x"])
            y = float(row["y"])
            features.append(
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [x, y]},
                    "properties": {"node_id": node_id},
                }
            )
    return {"type": "FeatureCollection", "features": features}


def build_edges_geojson(
    edges_path: Path, geometries: Dict[EdgeKey, List[Coord]]
) -> Dict[str, object]:
    features = []
    with edges_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            from_node = int(row["from_node"])
            to_node = int(row["to_node"])
            key = int(row["key"])
            geom = geometries.get((from_node, to_node, key))
            if not geom:
                continue
            features.append(
                {
                    "type": "Feature",
                    "geometry": {"type": "LineString", "coordinates": geom},
                    "properties": {
                        "edge_id": int(row["edge_id"]),
                        "from_node": from_node,
                        "to_node": to_node,
                        "key": key,
                        "length": float(row["length"]),
                        "travel_time": float(row["travel_time"]),
                        "access_score": float(row["access_score"]),
                    },
                }
            )
    return {"type": "FeatureCollection", "features": features}


def write_geojson(path: Path, data: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=True)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Convert CSV graph data to MapLibre-ready GeoJSON."
    )
    parser.add_argument("--nodes", default="data/nodes_table.csv", help="Path to nodes_table.csv")
    parser.add_argument("--edges", default="data/edges_table.csv", help="Path to edges_table.csv")
    parser.add_argument("--geom", default="data/edges_geometry.csv", help="Path to edges_geometry.csv")
    parser.add_argument("--out", default="data/maplibre", help="Output folder for GeoJSON files")
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

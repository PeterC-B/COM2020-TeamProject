import random
from server.app import create_app
from server.app.extensions import db
from server.app.domain.routing.graph_loader import load_graph_from_disk
from server.app.models.nodes_model import NodesModel
from server.app.models.edges_model import EdgesModel
from server.app.models.location_model import LocationModel
from server.app.models.enums.LOCATION_TYPE import LocationType

app = create_app()
app.app_context().push()

print("Loading processed graph...")
graph = load_graph_from_disk()

print("Clearing existing DB tables...")
db.session.query(LocationModel).delete()
db.session.query(EdgesModel).delete()
db.session.query(NodesModel).delete()
db.session.commit()

print("Seeding nodes...")
node_objects = []
for node_id, data in graph.nodes(data=True):
    x = data.get("x")
    y = data.get("y")
    if x is None or y is None:
        continue

    node_objects.append(
        NodesModel(
            node_id=int(node_id),
            x_coordinate=float(x),
            y_coordinate=float(y),
            feature=data.get("highway")
        )
    )

db.session.bulk_save_objects(node_objects)
db.session.commit()
print(f"Inserted {len(node_objects)} nodes.")

print("Seeding edges...")
edge_objects = []
edge_id_counter = 1

for u, v, key, data in graph.edges(keys=True, data=True):
    geom = data.get("geometry")
    if geom is None:
        continue

    edge_objects.append(
        EdgesModel(
            edge_id=edge_id_counter,
            from_node_id=int(u),
            to_node_id=int(v),
            key=int(key),
            length=float(data.get("length", 0)),
            travel_time=float(data.get("travel_time", 0)),
            access_score=float(data.get("access_score", 0)),
            geometry=geom.wkt,
            lighting=float(data.get("lighting", 0)),
            greenery=float(data.get("greenery", 0)),
            pollution=float(data.get("pollution", 0)),
            surface_quality=float(data.get("surface_quality", 0)),
            pub_distance=float(data.get("amenity_proximity", 0)),
        )
    )
    edge_id_counter += 1

db.session.bulk_save_objects(edge_objects)
db.session.commit()
print(f"Inserted {len(edge_objects)} edges.")

print("Generating 50+ locations...")
all_node_ids = [n.node_id for n in node_objects]
random.shuffle(all_node_ids)
selected = all_node_ids[:50]

location_objects = []
for i, node_id in enumerate(selected, start=1):
    location_objects.append(
        LocationModel(
            name=f"Location {i}",
            node_id=node_id,
            type=LocationType.GENERAL_AMENITY,
            information="Generated location",
            in_use=True
        )
    )

db.session.bulk_save_objects(location_objects)
db.session.commit()
print(f"Inserted {len(location_objects)} locations.")

print("Graph DB seeding complete.")

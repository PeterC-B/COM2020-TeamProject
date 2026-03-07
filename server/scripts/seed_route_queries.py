import random
from server.app import create_app
from server.app.extensions import db
from server.app.models.location_model import LocationModel
from server.app.models.route_query_model import RouteQuery

app = create_app()
app.app_context().push()

# Load all seeded locations from the database
locations = LocationModel.query.all()

if len(locations) < 2:
    raise RuntimeError(f"Not enough locations in DB. Found {len(locations)}.")

def to_coord_string(loc):
    lat = loc.node.y_coordinate
    lon = loc.node.x_coordinate
    return f"{lat},{lon}"

def random_weights():
    return {
        "distance": round(random.uniform(0.5, 1.0), 2),
        "lighting": round(random.uniform(0.0, 1.0), 2),
        "greenery": round(random.uniform(0.0, 1.0), 2),
        "pollution": round(random.uniform(0.0, 1.0), 2),
        "surface_quality": round(random.uniform(0.0, 1.0), 2),
        "amenity_proximity": round(random.uniform(0.0, 1.0), 2),
    }

entries = []

for _ in range(200):
    start, end = random.sample(locations, 2)

    q = RouteQuery(
        user_id=None,
        start=to_coord_string(start),
        end=to_coord_string(end),
        weights_json=random_weights(),
        chosen_route_rank=1,
        chosen_route_path=[],
    )

    entries.append(q)
    db.session.add(q)

db.session.commit()

print("Seeded 200+ route queries from DB locations.")

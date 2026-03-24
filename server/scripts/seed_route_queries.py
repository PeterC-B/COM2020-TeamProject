import random
import sys
from pathlib import Path
from uuid import uuid4

SERVER_ROOT = Path(__file__).resolve().parents[1]
if str(SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVER_ROOT))

from app import create_app
from app.extensions import db
from app.models.enums.ACCESS_TYPE import UserAccessType
from app.models.location_model import LocationModel
from app.models.route_query_model import RouteQuery
from app.models.user_account_model import UserAccountModel
from app.security.passwords import hash_password

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
        "distance": round(random.uniform(0.5, 1.0), 1),
        "lighting": round(random.uniform(0.0, 1.0), 1),
        "greenery": round(random.uniform(0.0, 1.0), 1),
        "pollution": round(random.uniform(0.0, 1.0), 1),
        "surface_quality": round(random.uniform(0.0, 1.0), 1),
        "is_accessible": random.choice([True, False]),
    }

entries = []
seeded_user_id = uuid4()

def insert_seeded_user():
    user = UserAccountModel(
        user_id=seeded_user_id,
        username="Seeded_Data",
        email="seeding@CAE.com",
        password_hash=hash_password("seeding"),
        role=UserAccessType.ADMINS,
    )
    db.session.add(user)
    db.session.commit()
    print("Seeding user created\n\nUsername: Seeded Data\nPassword: seeding")    

def delete_data():
    db.session.query(RouteQuery).delete()
    db.session.commit()

insert_seeded_user()
for _ in range(200):
    start, end = random.sample(locations, 2)

    q = RouteQuery(
        user_id=seeded_user_id,
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

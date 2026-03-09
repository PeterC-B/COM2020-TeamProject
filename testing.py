from app.extensions import db
from app.models.missions_model import MissionsModel
from app.models.location_model import LocationModel
from app.models.edges_model import EdgesModel
from app.models.nodes_model import NodesModel
from app.models.mission_progress_model import MissionProgressModel
from app.models.user_account_model import UserAccountModel
from app.models.enums.MISSION_TIER import MissionTier#
import osmnx as ox

from app import create_app

app = create_app()

def seed_missions():
    mission1 = MissionsModel(
        mission_name="City Navigation",
        question="What is the safest route through the city at night?",
        possible_answers="Main roads,Back alleys,Parks,Unlit streets",
        answer="Main roads",
        tier=MissionTier.EASY,
    )

    mission2 = MissionsModel(
        mission_name="Environmental Awareness",
        question="Which route minimises air pollution exposure?",
        possible_answers="Busy roads,Industrial areas,Green spaces,Motorways",
        answer="Green spaces",
        tier=MissionTier.MEDIUM,
    )

    db.session.add_all([mission1, mission2])
    db.session.commit()

    print("✅ Missions inserted successfully")

from datetime import datetime, timezone

from app.models.enums.ACCESS_TYPE import UserAccessType


def seed_test_user():
    from app.security.passwords import hash_password

    test_user = UserAccountModel(
        username="dev",
        email="dev@example.com",
        password_hash=hash_password("dev123"),  # real bcrypt hash
        role=UserAccessType.MAINTAINERS,
        created_at=datetime.now(tz=timezone.utc),
    )


    db.session.add(test_user)
    db.session.commit()

    print("✅ Test user inserted:")
    print("   username: dev")
    print("   password: dev123")


def reset_db():
    db.drop_all()
    db.create_all()
    seed_missions()
    seed_test_user()

if __name__ == "__main__":
    with app.app_context():
        reset_db()
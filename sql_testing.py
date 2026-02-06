from server.app import create_app
from server.app.extensions import db
from server.app.models import user_account_model, missions_model, location_model, nodes_model
from server.app.models.enums.ACCESS_TYPE import UserAccessType as access
from server.app.models.enums.MISSION_TIER import MissionTier as tier
from server.app.models.enums.LOCATION_TYPE import LocationType as locType
from sqlalchemy import inspect


# Create Flask app properly
app = create_app()

def insert_user():
    user = user_account_model.UserAccountModel(
        username="maxChambers",
        email="mc1276@exeter.ac.uk",
        password_hash="password",  # see note below
        role=access.MAINTAINERS,
    )

    print("Inserting user...")
    db.session.add(user)
    db.session.commit()
    print("User inserted successfully")

def select_all_users():
    print("\nSelecting all users...")


    active_users = (
        db.session
        .query(user_account_model.UserAccountModel)
        .all()
    )


    for u in active_users:
        print(u.id, u.email, u.password_hash)

def insert_mission():
    mission = missions_model.MissionsModel(
        mission_name="Least crossings",
        question="Why is it good to avoid crossings?",
        answer="So you don't get turned into jam",
        tier=tier.HARD,
    )

    print("Inserting mission...")
    db.session.add(mission)
    db.session.commit()
    print("Mission inserted successfully")

def insert_locations():

    location = location_model.LocationModel(
        name="Point A",
        node_id=104804,
        type=locType.GENERAL_AMENITY
    )

    print("Inserting mission...")
    db.session.add(location)

    location2 = location_model.LocationModel(
        name="Point B",
        node_id=13288882110,
        type=locType.DRINKING_AREA
    )

    print("Inserting mission 2...")
    db.session.add(location2)
    db.session.commit()
    print("Missions inserted successfully")

def query_locations():
    print("\nSelecting all locations...")

    locations = (
        db.session
        .query(location_model.LocationModel)
        .all()
    )


    for u in locations:
        print(u.location_id, u.name, u.node_id, u.type)

def insert_nodes():
    node1 = nodes_model.NodesModel(
        node_id=104804,
        x_coordinate=52.356,
        y_coordinate=-2.271428
    )

    db.session.add(node1)

    node2 = nodes_model.NodesModel(
        node_id=13288882110,
        x_coordinate=52.356,
        y_coordinate=-2.271428
    )

    db.session.add(node2)
    db.session.commit()

def query_mission():
    print("\nSelecting all missions...")


    missions = (
        db.session
        .query(missions_model.MissionsModel)
        .all()
    )


    for u in missions:
        print(u.mission_id, u.mission_name, u.question, u.answer, u.tier)

with app.app_context():
    db.drop_all()
    db.create_all()
    insert_nodes()
    insert_locations()
    query_locations()